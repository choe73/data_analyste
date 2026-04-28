"""Subscription management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User as UserModel, Subscription
from app.models.plan import Plan, Payment

router = APIRouter()


class UpgradeRequest(BaseModel):
    plan_id: int


class WebhookRequest(BaseModel):
    payment_id: int
    status: str  # succeeded, failed


@router.get("/subscriptions/me")
async def get_my_subscription(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's subscription."""
    try:
        # Get active subscription
        sub_query = select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        )
        sub_result = await db.execute(sub_query)
        subscription = sub_result.scalar_one_or_none()
        
        # Default to free plan
        if not subscription:
            return {
                "plan": "free",
                "status": "active",
                "features": {
                    "max_analyses": 2,
                    "max_datasets": 3,
                    "max_forms": 2,
                    "gemini": False,
                    "export": False
                },
                "usage": {
                    "analyses": 0,
                    "datasets": 0,
                    "forms": 0,
                    "gemini_calls": 0,
                }
            }
        
        # Get plan details
        plan_query = select(Plan).where(Plan.id == subscription.plan_id)
        plan_result = await db.execute(plan_query)
        plan = plan_result.scalar_one_or_none()
        
        return {
            "id": subscription.id,
            "plan": plan.name if plan else "free",
            "status": subscription.status,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date,
            "features": plan.features if plan else {},
            "usage": {
                "analyses": subscription.analyses_used_this_month,
                "datasets": subscription.datasets_created_this_month,
                "forms": subscription.forms_created_this_month,
                "gemini_calls": subscription.gemini_calls_this_month,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch subscription: {str(e)}")


@router.post("/subscriptions/upgrade")
async def upgrade_subscription(
    request: UpgradeRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade to a new plan (initiate payment)."""
    try:
        # Get plan
        plan_query = select(Plan).where(Plan.id == request.plan_id)
        plan_result = await db.execute(plan_query)
        plan = plan_result.scalar_one_or_none()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            amount_xaf=plan.price_xaf or 0,
            status="pending",
            payment_provider="mobile_money"
        )
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        
        # Return payment simulation URL
        return {
            "payment_id": payment.id,
            "amount_xaf": plan.price_xaf,
            "plan": plan.name,
            "status": "pending",
            "message": "Payment initiated. Simulate payment completion via webhook.",
            "webhook_url": f"/api/v1/subscriptions/webhook"
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Upgrade failed: {str(e)}")


@router.post("/subscriptions/webhook")
async def payment_webhook(
    request: WebhookRequest,
    db: AsyncSession = Depends(get_db)
):
    """Webhook to confirm payment (simulate Mobile Money callback)."""
    try:
        # Get payment
        payment_query = select(Payment).where(Payment.id == request.payment_id)
        payment_result = await db.execute(payment_query)
        payment = payment_result.scalar_one_or_none()
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        if request.status == "succeeded":
            # Update payment status
            payment.status = "succeeded"
            
            # Get plan by price
            plan_query = select(Plan).where(Plan.price_xaf == payment.amount_xaf)
            plan_result = await db.execute(plan_query)
            plan = plan_result.scalar_one_or_none()
            
            if plan:
                # Create or update subscription
                sub_query = select(Subscription).where(
                    Subscription.user_id == payment.user_id
                )
                sub_result = await db.execute(sub_query)
                subscription = sub_result.scalar_one_or_none()
                
                if subscription:
                    subscription.plan_id = plan.id
                    subscription.status = "active"
                    subscription.end_date = datetime.utcnow() + timedelta(days=30)
                else:
                    subscription = Subscription(
                        user_id=payment.user_id,
                        plan_id=plan.id,
                        status="active",
                        end_date=datetime.utcnow() + timedelta(days=30)
                    )
                    db.add(subscription)
            
            await db.commit()
            return {
                "status": "success",
                "message": "Subscription activated",
                "plan": plan.name if plan else "unknown"
            }
        else:
            payment.status = "failed"
            await db.commit()
            raise HTTPException(status_code=400, detail="Payment failed")
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Webhook failed: {str(e)}")


@router.post("/subscriptions/cancel")
async def cancel_subscription(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel current subscription."""
    try:
        # Get active subscription
        sub_query = select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        )
        sub_result = await db.execute(sub_query)
        subscription = sub_result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription")
        
        subscription.status = "cancelled"
        subscription.end_date = datetime.utcnow()
        await db.commit()
        
        return {"status": "success", "message": "Subscription cancelled"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Cancellation failed: {str(e)}")
