const config = {
  development: {
    apiBaseUrl: 'http://localhost:5002'
  },
  production: {
    apiBaseUrl: 'https://alphagrowth-scraper.onrender.com'  // Replace with your actual Render URL
  }
}

// Use Vite's environment mode
const env = import.meta.env.MODE || 'development'
export const apiBaseUrl = import.meta.env.VITE_API_URL || 'https://alphagrowth-scraper.onrender.com' 