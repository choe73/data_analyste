"""Form Builder endpoints – CRUD, publish, responses, analytics."""

import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.form import Form, FormField, FormResponse
from app.models.user import User
from app.schemas.form import (PLAN_LIMITS, FormAnalytics, FormCreate, FormOut,
                              FormResponseOut, FormUpdate)

router = APIRouter()


@router.post("", response_model=FormOut, status_code=201)
async def create_form(
    payload: FormCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new form with fields."""
    plan = "free"
    if current_user.subscriptions:
        active = [s for s in current_user.subscriptions if s.status == "active"]
        if active:
            plan = active[0].plan

    limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])["forms"][0]
    result = await db.execute(
        select(func.count(Form.id)).where(Form.user_id == current_user.id)
    )
    count = result.scalar() or 0
    if count >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"Form limit reached ({limit}). Upgrade your plan.",
        )

    share_token = secrets.token_urlsafe(32)
    form = Form(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        domain=payload.domain,
        max_responses=payload.max_responses,
        closes_at=payload.closes_at,
        share_token=share_token,
    )
    db.add(form)
    await db.flush()

    for field_data in payload.fields:
        field = FormField(
            form_id=form.id,
            field_type=field_data.field_type,
            label=field_data.label,
            placeholder=field_data.placeholder,
            required=field_data.required,
            options=field_data.options,
            validation=field_data.validation,
            conditional=field_data.conditional,
            order=field_data.order,
        )
        db.add(field)

    await db.commit()
    await db.refresh(form)
    return form


@router.get("", response_model=list[FormOut])
async def list_forms(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List current user's forms."""
    result = await db.execute(
        select(Form)
        .where(Form.user_id == current_user.id)
        .order_by(Form.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{form_id}", response_model=FormOut)
async def get_form(
    form_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a form by ID."""
    result = await db.execute(
        select(Form).where(Form.id == form_id, Form.user_id == current_user.id)
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return form


@router.put("/{form_id}", response_model=FormOut)
async def update_form(
    form_id: int,
    payload: FormUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a form."""
    result = await db.execute(
        select(Form).where(Form.id == form_id, Form.user_id == current_user.id)
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    for key, value in payload.model_dump(
        exclude_unset=True, exclude={"fields"}
    ).items():
        setattr(form, key, value)

    if payload.fields is not None:
        result = await db.execute(select(FormField).where(FormField.form_id == form_id))
        old_fields = result.scalars().all()
        for f in old_fields:
            await db.delete(f)
        await db.flush()

        for field_data in payload.fields:
            field = FormField(
                form_id=form.id,
                field_type=field_data.field_type,
                label=field_data.label,
                placeholder=field_data.placeholder,
                required=field_data.required,
                options=field_data.options,
                validation=field_data.validation,
                conditional=field_data.conditional,
                order=field_data.order,
            )
            db.add(field)

    await db.commit()
    await db.refresh(form)
    return form


@router.delete("/{form_id}", status_code=204)
async def delete_form(
    form_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a form."""
    result = await db.execute(
        select(Form).where(Form.id == form_id, Form.user_id == current_user.id)
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    await db.delete(form)
    await db.commit()


@router.post("/{form_id}/publish", response_model=FormOut)
async def publish_form(
    form_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Publish a form – makes it accessible via share link."""
    result = await db.execute(
        select(Form).where(Form.id == form_id, Form.user_id == current_user.id)
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    form.is_published = True
    await db.commit()
    await db.refresh(form)
    return form


@router.post("/{form_id}/unpublish", response_model=FormOut)
async def unpublish_form(
    form_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unpublish a form."""
    result = await db.execute(
        select(Form).where(Form.id == form_id, Form.user_id == current_user.id)
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    form.is_published = False
    await db.commit()
    await db.refresh(form)
    return form


@router.get("/{form_id}/responses", response_model=list[FormResponseOut])
async def list_responses(
    form_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List responses for a form."""
    result = await db.execute(
        select(Form).where(Form.id == form_id, Form.user_id == current_user.id)
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    result = await db.execute(
        select(FormResponse)
        .where(FormResponse.form_id == form_id)
        .order_by(FormResponse.submitted_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{form_id}/analytics", response_model=FormAnalytics)
async def form_analytics(
    form_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get analytics for a form's responses."""
    result = await db.execute(
        select(Form).where(Form.id == form_id, Form.user_id == current_user.id)
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    result = await db.execute(
        select(FormResponse).where(FormResponse.form_id == form_id)
    )
    responses = result.scalars().all()

    field_stats = {}
    for field in form.fields:
        key = field.label
        values = [r.responses.get(str(field.id)) for r in responses if r.responses]
        non_empty = [v for v in values if v is not None]

        if field.field_type == "number" and non_empty:
            nums = [float(v) for v in non_empty if isinstance(v, (int, float, str))]
            if nums:
                field_stats[key] = {
                    "count": len(nums),
                    "mean": sum(nums) / len(nums),
                    "min": min(nums),
                    "max": max(nums),
                }
        elif field.field_type in ("select", "multiselect", "rating") and non_empty:
            from collections import Counter

            counts = Counter(str(v) for v in non_empty)
            field_stats[key] = {"distribution": dict(counts), "total": len(non_empty)}
        else:
            field_stats[key] = {"count": len(non_empty)}

    return FormAnalytics(total_responses=len(responses), field_stats=field_stats)


@router.get("/{form_id}/responses/export")
async def export_responses(
    form_id: int,
    format: str = Query("csv", regex="^(csv|json)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export form responses as CSV or JSON."""
    import io
    import csv
    import json as json_lib
    from fastapi.responses import StreamingResponse

    result = await db.execute(
        select(Form).where(Form.id == form_id, Form.user_id == current_user.id)
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    result = await db.execute(
        select(FormResponse).where(FormResponse.form_id == form_id).order_by(FormResponse.submitted_at)
    )
    responses = result.scalars().all()

    # Build field label map
    field_labels = {str(f.id): f.label for f in form.fields}

    if format == "json":
        data = [
            {
                "id": r.id,
                "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
                **{field_labels.get(k, k): v for k, v in (r.responses or {}).items()},
            }
            for r in responses
        ]
        content = json_lib.dumps(data, ensure_ascii=False, indent=2)
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="form_{form_id}_responses.json"'},
        )

    # CSV
    output = io.StringIO()
    headers = ["id", "submitted_at"] + [f.label for f in sorted(form.fields, key=lambda x: x.order)]
    writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    for r in responses:
        row = {
            "id": r.id,
            "submitted_at": r.submitted_at.isoformat() if r.submitted_at else "",
        }
        for field in form.fields:
            row[field.label] = (r.responses or {}).get(str(field.id), "")
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),  # utf-8-sig for Excel compatibility
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="form_{form_id}_responses.csv"'},
    )
