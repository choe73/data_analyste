"""Public form endpoints – no authentication required."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.form import Form, FormField, FormResponse
from app.schemas.form import FormPublicOut, FormResponseOut, FormSubmit

router = APIRouter()


@router.get("/{share_token}", response_model=FormPublicOut)
async def get_public_form(
    share_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Access a published form via its share token."""
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Form).where(
            Form.share_token == share_token,
            Form.is_published == True,
        ).options(selectinload(Form.fields))
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or not published")
    
    # Manually construct response to ensure proper serialization
    return FormPublicOut(
        title=form.title,
        description=form.description,
        domain=form.domain,
        fields=[
            {
                "id": f.id,
                "form_id": f.form_id,
                "field_type": f.field_type,
                "label": f.label,
                "placeholder": f.placeholder,
                "required": f.required,
                "options": f.options,
                "validation": f.validation,
                "conditional": f.conditional,
                "order": f.order,
                "created_at": f.created_at,
            }
            for f in (form.fields or [])
        ],
        closes_at=form.closes_at,
    )


@router.post("/{share_token}/submit", response_model=FormResponseOut, status_code=201)
async def submit_form_response(
    share_token: str,
    payload: FormSubmit,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Submit a response to a published form."""
    result = await db.execute(
        select(Form).where(
            Form.share_token == share_token,
            Form.is_published == True,
        )
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or not published")

    if form.max_responses and form.response_count >= form.max_responses:
        raise HTTPException(
            status_code=403, detail="This form no longer accepts responses"
        )

    respondent_ip = None
    if request.client:
        respondent_ip = request.client.host

    response = FormResponse(
        form_id=form.id,
        responses=payload.responses,
        session_id=payload.session_id,
        respondent_ip=respondent_ip,
    )
    db.add(response)
    form.response_count = (form.response_count or 0) + 1
    await db.commit()
    await db.refresh(response)
    
    # Manually construct response to ensure proper serialization
    return FormResponseOut(
        id=response.id,
        form_id=response.form_id,
        responses=response.responses,
        submitted_at=response.submitted_at,
    )
