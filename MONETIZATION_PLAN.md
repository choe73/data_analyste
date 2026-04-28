# 🛡️ FRONT 1: Système d'Abonnement & Monétisation

## Objectif
Implémenter les plans d'abonnement (Gratuit, Standard 1000 XAF, Avancé 5000 XAF, Entreprise) avec blocage des quotas et paiement Mobile Money.

---

## PHASE 1: Modélisation des Données (Backend)

### 1.1 Tables Supabase à Créer

Exécuter ce SQL dans l'éditeur SQL de Supabase :

```sql
-- Table des plans d'abonnement
CREATE TABLE IF NOT EXISTS plans (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    price_xaf INTEGER,
    features JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Table des abonnements utilisateurs
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plan_id INTEGER REFERENCES plans(id),
    status TEXT DEFAULT 'pending',
    start_date TIMESTAMPTZ DEFAULT now(),
    end_date TIMESTAMPTZ,
    auto_renew BOOLEAN DEFAULT true,
    payment_provider TEXT,
    provider_subscription_id TEXT,
    analyses_used_this_month INTEGER DEFAULT 0,
    datasets_created_this_month INTEGER DEFAULT 0,
    forms_created_this_month INTEGER DEFAULT 0,
    gemini_calls_this_month INTEGER DEFAULT 0,
    quota_reset_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Table d'historique des paiements
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    amount_xaf INTEGER NOT NULL,
    currency TEXT DEFAULT 'XAF',
    status TEXT DEFAULT 'pending',
    payment_provider TEXT,
    provider_payment_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Insérer les plans par défaut
INSERT INTO plans (name, price_xaf, features) VALUES
('free', 0, '{"max_analyses": 2, "max_datasets": 3, "max_forms": 2, "gemini": false, "export": false}'),
('standard', 1000, '{"max_analyses": 20, "max_datasets": 50, "max_forms": 20, "gemini": true, "export": true}'),
('advanced', 5000, '{"max_analyses": 100, "max_datasets": 500, "max_forms": 100, "gemini": true, "export": true, "team": false}'),
('enterprise', NULL, '{"custom": true}');
```

### 1.2 Modèles SQLAlchemy

Créer `backend/app/models/plan.py` :

```python
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    price_xaf = Column(Integer, nullable=True)
    features = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    subscriptions = relationship("Subscription", back_populates="plan", lazy="select")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount_xaf = Column(Integer, nullable=False)
    currency = Column(String(3), default="XAF")
    status = Column(String(20), default="pending")
    payment_provider = Column(String(50), nullable=True)
    provider_payment_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 1.3 Mettre à jour le modèle Subscription existant

Le modèle `Subscription` existe déjà dans `backend/app/models/user.py`. Vérifier qu'il a tous les champs nécessaires.

---

## PHASE 2: Endpoints Backend

### 2.1 Créer `backend/app/api/endpoints/plans.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.plan import Plan

router = APIRouter()

@router.get("/plans")
async def list_plans(db: AsyncSession = Depends(get_db)):
    """List all available plans (public endpoint)."""
    query = select(Plan)
    result = await db.execute(query)
    plans = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price_xaf": p.price_xaf,
            "features": p.features,
        }
        for p in plans
    ]

@router.get("/plans/{plan_id}")
async def get_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    """Get plan details."""
    query = select(Plan).where(Plan.id == plan_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {
        "id": plan.id,
        "name": plan.name,
        "price_xaf": plan.price_xaf,
        "features": plan.features,
    }
```

### 2.2 Créer `backend/app/api/endpoints/subscriptions_v2.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User as UserModel, Subscription
from app.models.plan import Plan, Payment

router = APIRouter()

@router.get("/subscriptions/me")
async def get_my_subscription(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's subscription."""
    query = select(Subscription).where(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        # Return free plan by default
        return {
            "plan": "free",
            "status": "active",
            "features": {"max_analyses": 2, "max_datasets": 3, "max_forms": 2}
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

@router.post("/subscriptions/upgrade")
async def upgrade_subscription(
    plan_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade to a new plan (simulate payment)."""
    try:
        # Get plan
        plan_query = select(Plan).where(Plan.id == plan_id)
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
        
        # Return payment simulation URL
        return {
            "payment_id": payment.id,
            "amount_xaf": plan.price_xaf,
            "plan": plan.name,
            "status": "pending",
            "message": "Payment initiated. Simulate payment completion via webhook."
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Upgrade failed: {str(e)}")

@router.post("/subscriptions/webhook")
async def payment_webhook(
    payment_id: int,
    status: str,
    db: AsyncSession = Depends(get_db)
):
    """Webhook to confirm payment (simulate Mobile Money callback)."""
    try:
        # Get payment
        payment_query = select(Payment).where(Payment.id == payment_id)
        payment_result = await db.execute(payment_query)
        payment = payment_result.scalar_one_or_none()
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        if status == "succeeded":
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
            return {"status": "success", "message": "Subscription activated"}
        else:
            payment.status = "failed"
            await db.commit()
            raise HTTPException(status_code=400, detail="Payment failed")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Webhook failed: {str(e)}")
```

### 2.3 Enregistrer les routers

Ajouter dans `backend/app/api/router.py` :

```python
from app.api.endpoints import plans, subscriptions_v2

api_router.include_router(plans.router, prefix="/plans", tags=["Plans"])
api_router.include_router(subscriptions_v2.router, prefix="/subscriptions", tags=["Subscriptions"])
```

---

## PHASE 3: Middleware de Quotas (Backend)

Créer `backend/app/dependencies/quota.py` :

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User as UserModel, Subscription
from app.models.plan import Plan

async def check_quota(
    feature: str,  # "analysis", "dataset", "form", "gemini"
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if user has quota for the requested feature."""
    
    # Get active subscription
    sub_query = select(Subscription).where(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    )
    sub_result = await db.execute(sub_query)
    subscription = sub_result.scalar_one_or_none()
    
    # Default to free plan
    if not subscription:
        features = {"max_analyses": 2, "max_datasets": 3, "max_forms": 2, "gemini": False}
    else:
        plan_query = select(Plan).where(Plan.id == subscription.plan_id)
        plan_result = await db.execute(plan_query)
        plan = plan_result.scalar_one_or_none()
        features = plan.features if plan else {}
    
    # Check quota based on feature
    if feature == "analysis":
        max_analyses = features.get("max_analyses", 2)
        if subscription and subscription.analyses_used_this_month >= max_analyses:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Analysis quota exceeded. Upgrade to {features.get('name', 'Standard')} plan."
            )
    elif feature == "dataset":
        max_datasets = features.get("max_datasets", 3)
        if subscription and subscription.datasets_created_this_month >= max_datasets:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Dataset quota exceeded. Upgrade your plan."
            )
    elif feature == "form":
        max_forms = features.get("max_forms", 2)
        if subscription and subscription.forms_created_this_month >= max_forms:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Form quota exceeded. Upgrade your plan."
            )
    elif feature == "gemini":
        if not features.get("gemini", False):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Gemini AI is only available in paid plans. Upgrade to Standard (1000 XAF)."
            )
    
    return subscription
```

---

## PHASE 4: Frontend - Page de Tarification

Créer `frontend/src/pages/Pricing.tsx` :

```tsx
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Check } from 'lucide-react';

export default function Pricing() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/plans`
      );
      const data = await response.json();
      setPlans(data);
    } catch (error) {
      console.error('Failed to fetch plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = (planId: number) => {
    // TODO: Implement payment flow
    console.log('Upgrade to plan:', planId);
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-4">Plans & Tarification</h1>
        <p className="text-center text-gray-600 mb-12">
          Choisissez le plan qui correspond à vos besoins
        </p>

        <div className="grid md:grid-cols-4 gap-6">
          {plans.map((plan) => (
            <Card key={plan.id} className="p-6 flex flex-col">
              <h3 className="text-2xl font-bold mb-2 capitalize">{plan.name}</h3>
              <div className="mb-6">
                {plan.price_xaf ? (
                  <>
                    <span className="text-4xl font-bold">{plan.price_xaf}</span>
                    <span className="text-gray-600"> XAF/mois</span>
                  </>
                ) : (
                  <span className="text-2xl font-bold">Sur devis</span>
                )}
              </div>

              <ul className="space-y-3 mb-6 flex-grow">
                {plan.features.max_analyses && (
                  <li className="flex items-center">
                    <Check className="w-5 h-5 text-green-600 mr-2" />
                    <span>{plan.features.max_analyses} analyses/mois</span>
                  </li>
                )}
                {plan.features.max_datasets && (
                  <li className="flex items-center">
                    <Check className="w-5 h-5 text-green-600 mr-2" />
                    <span>{plan.features.max_datasets} datasets</span>
                  </li>
                )}
                {plan.features.max_forms && (
                  <li className="flex items-center">
                    <Check className="w-5 h-5 text-green-600 mr-2" />
                    <span>{plan.features.max_forms} formulaires</span>
                  </li>
                )}
                {plan.features.gemini && (
                  <li className="flex items-center">
                    <Check className="w-5 h-5 text-green-600 mr-2" />
                    <span>IA Gemini incluse</span>
                  </li>
                )}
              </ul>

              <Button
                onClick={() => handleUpgrade(plan.id)}
                className={plan.name === 'free' ? 'bg-gray-400' : 'bg-green-600'}
                disabled={plan.name === 'free'}
              >
                {plan.name === 'free' ? 'Plan actuel' : 'S\'abonner'}
              </Button>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## PHASE 5: Tests

### Test 1: Créer les plans
```bash
curl -s "https://datacollect-cameroun-prod.onrender.com/api/v1/plans" | jq .
```

### Test 2: Récupérer l'abonnement actuel
```bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  "https://datacollect-cameroun-prod.onrender.com/api/v1/subscriptions/me" | jq .
```

### Test 3: Simuler un upgrade
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  "https://datacollect-cameroun-prod.onrender.com/api/v1/subscriptions/upgrade" \
  -H "Content-Type: application/json" \
  -d '{"plan_id": 2}' | jq .
```

---

## Checklist d'Implémentation

- [ ] Créer les tables Supabase
- [ ] Créer les modèles SQLAlchemy (Plan, Payment)
- [ ] Créer les endpoints `/plans` et `/subscriptions`
- [ ] Créer le middleware de quotas
- [ ] Créer la page Pricing.tsx
- [ ] Tester l'upgrade de plan
- [ ] Tester le webhook de paiement
- [ ] Intégrer les quotas dans les endpoints sensibles
