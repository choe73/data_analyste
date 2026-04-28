import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Check, X } from 'lucide-react';
import { useAuth } from '@/store/auth';

interface Plan {
  id: number;
  name: string;
  price_xaf: number | null;
  features: Record<string, any>;
}

export default function Pricing() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState<number | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/plans`
      );
      if (!response.ok) throw new Error('Failed to fetch plans');
      const data = await response.json();
      setPlans(data);
    } catch (error) {
      console.error('Failed to fetch plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (planId: number) => {
    if (!user) {
      window.location.href = '/login';
      return;
    }

    setUpgrading(planId);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/subscriptions/upgrade`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ plan_id: planId }),
        }
      );

      if (!response.ok) throw new Error('Upgrade failed');
      const data = await response.json();

      // Simulate payment success
      alert(`Payment initiated for ${data.plan} plan (${data.amount_xaf} XAF)`);

      // Simulate webhook callback
      setTimeout(async () => {
        try {
          const webhookResponse = await fetch(
            `${import.meta.env.VITE_API_URL}/api/v1/subscriptions/webhook`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                payment_id: data.payment_id,
                status: 'succeeded',
              }),
            }
          );

          if (webhookResponse.ok) {
            alert('✅ Subscription activated! Refresh the page to see your new plan.');
            window.location.reload();
          }
        } catch (error) {
          console.error('Webhook error:', error);
        }
      }, 1000);
    } catch (error) {
      console.error('Upgrade error:', error);
      alert('Upgrade failed. Please try again.');
    } finally {
      setUpgrading(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p>Chargement des plans...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Plans & Tarification
          </h1>
          <p className="text-xl text-gray-600">
            Choisissez le plan qui correspond à vos besoins
          </p>
        </div>

        {/* Plans Grid */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          {plans.map((plan) => {
            const isPopular = plan.name === 'standard';
            const isCurrent = plan.name === 'free'; // Assume free is current for demo

            return (
              <Card
                key={plan.id}
                className={`p-6 flex flex-col transition-all ${
                  isPopular ? 'ring-2 ring-green-600 shadow-lg scale-105' : ''
                }`}
              >
                {isPopular && (
                  <div className="bg-green-600 text-white px-3 py-1 rounded-full text-sm font-semibold mb-4 w-fit">
                    Populaire
                  </div>
                )}

                <h3 className="text-2xl font-bold mb-2 capitalize">{plan.name}</h3>

                {/* Price */}
                <div className="mb-6">
                  {plan.price_xaf ? (
                    <>
                      <span className="text-4xl font-bold text-gray-900">
                        {plan.price_xaf.toLocaleString()}
                      </span>
                      <span className="text-gray-600"> XAF/mois</span>
                    </>
                  ) : (
                    <span className="text-2xl font-bold text-gray-900">Sur devis</span>
                  )}
                </div>

                {/* Features */}
                <ul className="space-y-3 mb-6 flex-grow">
                  {plan.features.max_analyses && (
                    <li className="flex items-start">
                      <Check className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">
                        {plan.features.max_analyses} analyses/mois
                      </span>
                    </li>
                  )}
                  {plan.features.max_datasets && (
                    <li className="flex items-start">
                      <Check className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">
                        {plan.features.max_datasets} datasets
                      </span>
                    </li>
                  )}
                  {plan.features.max_forms && (
                    <li className="flex items-start">
                      <Check className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">
                        {plan.features.max_forms} formulaires
                      </span>
                    </li>
                  )}
                  {plan.features.gemini ? (
                    <li className="flex items-start">
                      <Check className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">IA Gemini incluse</span>
                    </li>
                  ) : (
                    <li className="flex items-start">
                      <X className="w-5 h-5 text-gray-400 mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-500">IA Gemini</span>
                    </li>
                  )}
                  {plan.features.export ? (
                    <li className="flex items-start">
                      <Check className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">Export CSV/Excel</span>
                    </li>
                  ) : (
                    <li className="flex items-start">
                      <X className="w-5 h-5 text-gray-400 mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-500">Export CSV/Excel</span>
                    </li>
                  )}
                </ul>

                {/* CTA Button */}
                <Button
                  onClick={() => handleUpgrade(plan.id)}
                  disabled={isCurrent || upgrading === plan.id}
                  className={`w-full ${
                    isCurrent
                      ? 'bg-gray-400 cursor-not-allowed'
                      : isPopular
                      ? 'bg-green-600 hover:bg-green-700'
                      : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
                  }`}
                >
                  {upgrading === plan.id ? (
                    <span className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                      Traitement...
                    </span>
                  ) : isCurrent ? (
                    'Plan actuel'
                  ) : plan.name === 'enterprise' ? (
                    'Nous contacter'
                  ) : (
                    'S\'abonner'
                  )}
                </Button>
              </Card>
            );
          })}
        </div>

        {/* FAQ Section */}
        <div className="bg-white rounded-lg shadow-md p-8 max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold mb-6">Questions fréquentes</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Puis-je changer de plan à tout moment ?
              </h3>
              <p className="text-gray-600">
                Oui, vous pouvez upgrader ou downgrader votre plan à tout moment. Les changements
                prennent effet immédiatement.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Quel est le délai de renouvellement ?
              </h3>
              <p className="text-gray-600">
                Les abonnements se renouvellent automatiquement chaque mois. Vous pouvez annuler
                à tout moment.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Acceptez-vous d'autres modes de paiement ?
              </h3>
              <p className="text-gray-600">
                Actuellement, nous acceptons Mobile Money (MTN, Orange). D'autres options seront
                bientôt disponibles.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
