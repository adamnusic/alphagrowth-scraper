import React from 'react'
import ErrorBoundary from './components/ErrorBoundary'
import ParticipationStats from './components/ParticipationStats'
import TopParticipants from './components/TopParticipants'

function App() {
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
      </div>
    </ErrorBoundary>
  )
}

export default App 