/**
 * Configuration multi-sites
 * Les URLs sont injectées via variables d'environnement Render
 */

export const config = {
  primary: {
    api: import.meta.env.VITE_API_URL || 'https://datacollect-cameroun-prod.onrender.com',
    name: 'DataCollect Cameroun',
  },
  secondary: {
    api: import.meta.env.VITE_SECONDARY_SITE_URL || 'https://datacollect-cameroun-prod.onrender.com',
    name: 'DataCollect Secondary',
  },
}

// Déterminer quel site est actif basé sur l'URL actuelle
export const getActiveConfig = () => {
  const currentHost = window.location.hostname
  
  // Si c'est le site secondaire, utiliser sa config
  if (import.meta.env.VITE_SECONDARY_SITE_URL && currentHost.includes('sdfsd-qdfsd-22')) {
    return config.secondary
  }
  
  return config.primary
}

export const getApiUrl = () => getActiveConfig().api
export const getSiteName = () => getActiveConfig().name
