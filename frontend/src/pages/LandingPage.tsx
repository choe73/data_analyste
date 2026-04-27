import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Logo } from '@/components/layout/Logo'
import { BarChart3, Database, Zap, Users, Globe, Shield } from 'lucide-react'

export function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#007A5E]/5 via-white to-[#CE1126]/5">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Logo size={40} />
            <div>
              <h1 className="text-xl font-bold text-[#007A5E]">DataCollect</h1>
              <p className="text-xs text-gray-500">Pro Cameroun</p>
            </div>
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => navigate('/login')}
              className="border-[#007A5E] text-[#007A5E] hover:bg-[#007A5E]/5"
            >
              Se connecter
            </Button>
            <Button
              onClick={() => navigate('/login')}
              className="bg-[#007A5E] hover:bg-[#005a45]"
            >
              S'inscrire
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-5xl font-bold text-gray-900 mb-6">
              Collecte et analyse intelligente de données
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Plateforme complète pour collecter, analyser et visualiser les données du Cameroun avec l'IA.
            </p>
            <div className="flex gap-4">
              <Button
                size="lg"
                onClick={() => navigate('/login')}
                className="bg-[#007A5E] hover:bg-[#005a45]"
              >
                Commencer maintenant
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-gray-300"
              >
                En savoir plus
              </Button>
            </div>
          </div>
          <div className="bg-gradient-to-br from-[#007A5E]/10 to-[#CE1126]/10 rounded-lg p-12 flex items-center justify-center min-h-96">
            <div className="text-center">
              <Database className="w-24 h-24 text-[#007A5E] mx-auto mb-4 opacity-50" />
              <p className="text-gray-500">Visualisation des données</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Fonctionnalités principales
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Database,
                title: 'Collecte de données',
                description: 'Collectez des données de multiples sources en temps réel'
              },
              {
                icon: BarChart3,
                title: 'Analyses avancées',
                description: 'Analyses statistiques, ML, clustering et prédictions'
              },
              {
                icon: Zap,
                title: 'IA intégrée',
                description: 'Interprétations intelligentes avec Gemini'
              },
              {
                icon: Globe,
                title: 'Données régionales',
                description: 'Données spécifiques aux 10 régions du Cameroun'
              },
              {
                icon: Users,
                title: 'Collaboration',
                description: 'Partagez et collaborez sur les analyses'
              },
              {
                icon: Shield,
                title: 'Sécurisé',
                description: 'Authentification JWT et chiffrement des données'
              },
            ].map((feature, i) => (
              <div key={i} className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition">
                <feature.icon className="w-12 h-12 text-[#007A5E] mb-4" />
                <h4 className="font-semibold text-gray-900 mb-2">{feature.title}</h4>
                <p className="text-gray-600 text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid md:grid-cols-4 gap-8 text-center">
          {[
            { label: 'Datasets', value: '50+' },
            { label: 'Analyses', value: '1000+' },
            { label: 'Utilisateurs', value: '100+' },
            { label: 'Régions', value: '10' },
          ].map((stat, i) => (
            <div key={i}>
              <div className="text-4xl font-bold text-[#007A5E] mb-2">{stat.value}</div>
              <div className="text-gray-600">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gradient-to-r from-[#007A5E] to-[#005a45] text-white py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-3xl font-bold mb-4">Prêt à commencer?</h3>
          <p className="text-lg mb-8 opacity-90">
            Rejoignez des centaines d'analystes et de décideurs utilisant DataCollect Pro
          </p>
          <Button
            size="lg"
            onClick={() => navigate('/login')}
            className="bg-white text-[#007A5E] hover:bg-gray-100"
          >
            S'inscrire gratuitement
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="text-white font-semibold mb-4">Produit</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Fonctionnalités</a></li>
                <li><a href="#" className="hover:text-white">Tarification</a></li>
                <li><a href="#" className="hover:text-white">Documentation</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Entreprise</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">À propos</a></li>
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Légal</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Confidentialité</a></li>
                <li><a href="#" className="hover:text-white">Conditions</a></li>
                <li><a href="#" className="hover:text-white">Cookies</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Suivez-nous</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Twitter</a></li>
                <li><a href="#" className="hover:text-white">LinkedIn</a></li>
                <li><a href="#" className="hover:text-white">GitHub</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>&copy; 2026 DataCollect Pro Cameroun. Tous droits réservés.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
