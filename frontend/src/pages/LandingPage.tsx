import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Logo } from '@/components/layout/Logo'
import {
  BarChart3, Database, Zap, Users, Globe, Shield,
  ArrowRight, Sparkles, TrendingUp, Layers, Brain, Upload,
  CheckCircle2, FileText, MapPin
} from 'lucide-react'

export function LandingPage() {
  const navigate = useNavigate()

  const features = [
    {
      icon: Database,
      title: 'Collecte multi-sources',
      description: 'Importez CSV/Excel ou connectez les API World Bank, FAO, NASA — données en temps réel pour les 10 régions du Cameroun.',
      gradient: 'from-blue-500 to-cyan-400',
    },
    {
      icon: BarChart3,
      title: 'Analyses statistiques',
      description: 'Descriptives, régression, ACP, clustering et classification — tout le pipeline analytique en quelques clics.',
      gradient: 'from-emerald-500 to-green-400',
    },
    {
      icon: Sparkles,
      title: 'Interprétation IA',
      description: 'Gemini traduit vos résultats en recommandations actionnables, adaptées au contexte camerounais.',
      gradient: 'from-violet-500 to-purple-400',
    },
    {
      icon: Globe,
      title: 'Données régionales',
      description: 'Agriculture, santé, éducation, finance — données spécifiques aux 10 régions du Cameroun.',
      gradient: 'from-amber-500 to-orange-400',
    },
    {
      icon: Users,
      title: 'Formulaires & Enquêtes',
      description: 'Créez et partagez des formulaires de collecte adaptés au terrain, avec suivi en temps réel.',
      gradient: 'from-pink-500 to-rose-400',
    },
    {
      icon: Shield,
      title: 'Sécurité & Conformité',
      description: 'Authentification JWT, chiffrement, consentement RGPD — vos données sont protégées.',
      gradient: 'from-slate-500 to-gray-400',
    },
  ]

  const steps = [
    {
      num: '01',
      title: 'Importez vos données',
      desc: 'CSV, Excel, API ou formulaire — vos données sont structurées automatiquement.',
      icon: Upload,
    },
    {
      num: '02',
      title: 'Choisissez votre analyse',
      desc: 'Statistiques descriptives, régression, ACP, clustering ou classification supervisée.',
      icon: Brain,
    },
    {
      num: '03',
      title: 'Obtenez des recommandations',
      desc: 'L\'IA Gemini interprète vos résultats et propose des actions concrètes.',
      icon: Sparkles,
    },
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white/90 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Logo size={36} />
            <div>
              <h1 className="text-lg font-bold text-[#007A5E] leading-tight">DataCollect</h1>
              <p className="text-[10px] text-gray-400 font-medium tracking-wide uppercase">Pro Cameroun</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              onClick={() => navigate('/login')}
              className="text-gray-600 hover:text-[#007A5E]"
            >
              Se connecter
            </Button>
            <Button
              onClick={() => navigate('/login')}
              className="bg-[#007A5E] hover:bg-[#005a45] text-white shadow-sm"
            >
              Commencer gratuitement
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#007A5E]/5 via-transparent to-[#FCD116]/5" />
        <div className="absolute top-20 right-0 w-96 h-96 bg-[#007A5E]/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-[#FCD116]/10 rounded-full blur-3xl" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <div className="inline-flex items-center gap-2 bg-[#007A5E]/10 text-[#007A5E] px-3 py-1.5 rounded-full text-sm font-medium mb-6">
                <MapPin className="w-3.5 h-3.5" />
                Adapté aux 10 régions du Cameroun
              </div>
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-[1.1]">
                De la donnée brute à{' '}
                <span className="text-[#007A5E]">l'action</span>
              </h2>
              <p className="text-lg text-gray-600 mb-8 leading-relaxed max-w-lg">
                Collectez, analysez et obtenez des recommandations contextuelles.
                Régression, ACP, clustering et classification, interprétés par l'IA Gemini.
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  size="lg"
                  onClick={() => navigate('/login')}
                  className="bg-[#007A5E] hover:bg-[#005a45] text-white shadow-lg shadow-[#007A5E]/20 h-12 px-8"
                >
                  Commencer gratuitement
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  className="border-gray-200 h-12 px-8"
                  onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
                >
                  Découvrir la plateforme
                </Button>
              </div>
              <div className="flex items-center gap-6 mt-8 text-sm text-gray-500">
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span>Gratuit pour débuter</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span>Aucune carte requise</span>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="relative bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-8 border border-gray-200/50 shadow-xl">
                {/* Mock dashboard preview */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="w-3 h-3 rounded-full bg-red-400" />
                    <div className="w-3 h-3 rounded-full bg-yellow-400" />
                    <div className="w-3 h-3 rounded-full bg-green-400" />
                    <span className="text-xs text-gray-400 ml-2">DataCollect Pro — Dashboard</span>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { label: 'Datasets', val: '52', color: 'bg-blue-500' },
                      { label: 'Analyses', val: '1.2k', color: 'bg-emerald-500' },
                      { label: 'Régions', val: '10', color: 'bg-amber-500' },
                    ].map(s => (
                      <div key={s.label} className="bg-white rounded-lg p-3 shadow-sm border border-gray-100">
                        <div className={`w-6 h-1 rounded ${s.color} mb-2`} />
                        <div className="text-lg font-bold text-gray-800">{s.val}</div>
                        <div className="text-[10px] text-gray-400">{s.label}</div>
                      </div>
                    ))}
                  </div>
                  <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp className="w-4 h-4 text-[#007A5E]" />
                      <span className="text-xs font-medium text-gray-600">Régression — PIB régional</span>
                    </div>
                    <div className="flex items-end gap-1 h-20">
                      {[35, 50, 42, 65, 58, 72, 68, 85, 78, 92].map((h, i) => (
                        <div
                          key={i}
                          className="flex-1 rounded-t bg-gradient-to-t from-[#007A5E] to-[#007A5E]/60"
                          style={{ height: `${h}%` }}
                        />
                      ))}
                    </div>
                  </div>
                  <div className="bg-white rounded-lg p-3 shadow-sm border border-gray-100">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-3.5 h-3.5 text-violet-500" />
                      <span className="text-[11px] text-gray-500">
                        <span className="font-medium text-violet-600">Gemini :</span>{' '}
                        La région du Littoral montre une croissance soutenue de 4.2%...
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              {/* Decorative elements */}
              <div className="absolute -top-4 -right-4 w-20 h-20 bg-[#FCD116]/20 rounded-full blur-xl" />
              <div className="absolute -bottom-4 -left-4 w-16 h-16 bg-[#CE1126]/10 rounded-full blur-xl" />
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="bg-gray-50/50 py-20 border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <p className="text-sm font-semibold text-[#007A5E] mb-2">Comment ça marche</p>
            <h3 className="text-3xl font-bold text-gray-900">Trois étapes vers l'insight</h3>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((step) => {
              const Icon = step.icon
              return (
                <div key={step.num} className="relative">
                  <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-100 hover:shadow-md transition-shadow h-full">
                    <div className="flex items-center gap-4 mb-4">
                      <span className="text-4xl font-black text-[#007A5E]/10">{step.num}</span>
                      <div className="p-2.5 rounded-xl bg-[#007A5E]/10">
                        <Icon className="w-5 h-5 text-[#007A5E]" />
                      </div>
                    </div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">{step.title}</h4>
                    <p className="text-sm text-gray-500 leading-relaxed">{step.desc}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <p className="text-sm font-semibold text-[#007A5E] mb-2">Fonctionnalités</p>
            <h3 className="text-3xl font-bold text-gray-900">Tout ce dont vous avez besoin</h3>
            <p className="text-gray-500 mt-3 max-w-2xl mx-auto">
              Une plateforme complète pour la collecte, l'analyse et l'interprétation des données camerounaises.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => {
              const Icon = feature.icon
              return (
                <div key={feature.title} className="group bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300">
                  <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${feature.gradient} text-white mb-4`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <h4 className="text-base font-semibold text-gray-900 mb-2">{feature.title}</h4>
                  <p className="text-sm text-gray-500 leading-relaxed">{feature.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-gradient-to-br from-[#007A5E] via-[#006B50] to-[#005a45] py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { label: 'Sources de données', value: '50+' },
              { label: 'Analyses réalisées', value: '1 000+' },
              { label: 'Utilisateurs actifs', value: '100+' },
              { label: 'Régions couvertes', value: '10' },
            ].map((stat) => (
              <div key={stat.label}>
                <div className="text-3xl md:text-4xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-sm text-green-200">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-12 border border-gray-200/50">
            <div className="inline-flex p-3 rounded-full bg-[#007A5E]/10 mb-6">
              <Sparkles className="w-6 h-6 text-[#007A5E]" />
            </div>
            <h3 className="text-3xl font-bold text-gray-900 mb-4">Prêt à transformer vos données ?</h3>
            <p className="text-gray-500 mb-8 max-w-lg mx-auto">
              Rejoignez les analystes et décideurs qui utilisent DataCollect Pro pour des décisions éclairées au Cameroun.
            </p>
            <Button
              size="lg"
              onClick={() => navigate('/login')}
              className="bg-[#007A5E] hover:bg-[#005a45] text-white shadow-lg shadow-[#007A5E]/20 h-12 px-8"
            >
              S'inscrire gratuitement
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Logo size={28} />
                <span className="text-white font-bold">DataCollect Pro</span>
              </div>
              <p className="text-sm leading-relaxed">
                Plateforme intelligente de collecte et analyse de données pour le Cameroun.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Produit</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#features" className="hover:text-white transition-colors">Fonctionnalités</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Tarification</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Ressources</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">API Reference</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Guides</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Légal</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Confidentialité</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Conditions</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Cookies</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm">&copy; 2025 DataCollect Pro Cameroun. Tous droits réservés.</p>
            <div className="flex gap-1">
              <div className="w-6 h-1 rounded bg-[#007A5E]" />
              <div className="w-6 h-1 rounded bg-[#CE1126]" />
              <div className="w-6 h-1 rounded bg-[#FCD116]" />
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
