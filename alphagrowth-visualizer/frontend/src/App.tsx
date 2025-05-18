import ErrorBoundary from './components/ErrorBoundary'
import ParticipationStats from './components/ParticipationStats'
import TopParticipants from './components/TopParticipants'
import { useEffect, useState } from 'react'
import axios from 'axios'
import { apiBaseUrl } from './config'

function App() {
  const [lastRunDate, setLastRunDate] = useState<string | null>(null)

  useEffect(() => {
    const fetchLastRunDate = async () => {
      try {
        const response = await axios.get(`${apiBaseUrl}/api/last-run`, {
          withCredentials: true
        })
        setLastRunDate(response.data.last_run_date)
      } catch (error) {
        console.error('Error fetching last run date:', error)
      }
    }

    fetchLastRunDate()
  }, [])

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-100">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold text-gray-900">
              AlphaGrowth Spaces Report
            </h1>
            <p className="mt-2 text-sm text-gray-600">
              Analysis of participation in{' '}
              <a 
                href="https://alphagrowth.io/spaces" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 hover:underline"
              >
                AlphaGrowth Twitter Spaces
              </a>
              {lastRunDate && (
                <span className="ml-2 text-gray-500">
                  (Last updated: {lastRunDate})
                </span>
              )}
            </p>
          </div>
        </header>
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
              <div className="space-y-6">
              {/* Overview Statistics */}
              <section>
                <ParticipationStats />
              </section>

              {/* Top Participants */}
              <section>
                <TopParticipants />
              </section>
            </div>
          </div>
        </main>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-500 mb-4">
            API spins down with inactivity, which can delay requests by 50 seconds or more.
          </div>
        </div>
        <footer className="bg-white border-t border-gray-200 mt-8">
          <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
            <div className="flex justify-center items-center space-x-2 text-sm text-gray-500">
              <span>Scraped by</span>
              <a 
                href="https://songjam.space" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 hover:underline"
              >
                Songjam
              </a>
              <span>•</span>
              <a 
                href="https://github.com/adamsongjam/alphagrowth-scraper" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 hover:underline flex items-center space-x-1"
              >
                <svg 
                  viewBox="0 0 24 24" 
                  className="w-4 h-4 fill-current"
                  aria-hidden="true"
                >
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                <span>View Source</span>
              </a>
            </div>
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  )
}

export default App 