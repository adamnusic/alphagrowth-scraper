import { useEffect, useState, useMemo } from 'react'
import axios from 'axios'
import { apiBaseUrl } from '../config'

interface Participant {
  id: string
  name: string
  spaces: number
  role: 'host' | 'speaker' | 'both'
  host_spaces: number
  speaker_spaces: number
  twitter: string | null
}

const ITEMS_PER_PAGE = 10

const TopParticipants = () => {
  const [participants, setParticipants] = useState<Participant[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'hosts' | 'speakers' | 'overall'>('hosts')
  const [currentPage, setCurrentPage] = useState(1)

  useEffect(() => {
    const fetchData = async () => {
      let retries = 3
      while (retries > 0) {
        try {
          console.log('Fetching participants from:', `${apiBaseUrl}/api/participants`)
          const response = await axios.get<Participant[]>(`${apiBaseUrl}/api/participants`, {
            timeout: 15000,
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            withCredentials: false
          })
          
          // Validate the response data
          if (!response.data) {
            console.error('No data in response')
            throw new Error('No data received')
          }
          
          // Parse the data if it's a string
          let participants = response.data
          if (typeof participants === 'string') {
            try {
              participants = JSON.parse(participants)
            } catch (e) {
              console.error('Failed to parse participants data:', e)
              throw new Error('Invalid data format')
            }
          }
          
          // Ensure we have an array
          if (!Array.isArray(participants)) {
            console.error('Participants is not an array:', participants)
            throw new Error('Invalid data format')
          }
          
          // Validate each participant
          const validParticipants = participants.filter(p => {
            if (!p || typeof p !== 'object') return false
            if (!p.name || typeof p.name !== 'string') return false
            if (!p.role || !['host', 'speaker', 'both'].includes(p.role)) return false
            if (typeof p.spaces !== 'number' || isNaN(p.spaces)) return false
            if (typeof p.speaker_spaces !== 'number' || isNaN(p.speaker_spaces)) return false
            if (typeof p.host_spaces !== 'number' || isNaN(p.host_spaces)) return false
            return true
          })
          
          // Log the first few items to verify data structure
          console.log('First 3 participants:', validParticipants.slice(0, 3))
          console.log('Total participants:', validParticipants.length)
          
          if (validParticipants.length === 0) {
            throw new Error('No valid participants found')
          }
          
          setParticipants(validParticipants)
          setError(null)
          break
        } catch (error) {
          console.error('Error fetching participants:', error)
          if (axios.isAxiosError(error)) {
            console.error('Response data:', error.response?.data)
            console.error('Response status:', error.response?.status)
            console.error('Response headers:', error.response?.headers)
            if (retries > 1) {
              console.log(`Retrying... ${retries - 1} attempts left`)
              retries--
              await new Promise(resolve => setTimeout(resolve, 1000))
              continue
            }
            setError(`Failed to load participants: ${error.response?.data?.message || error.message}`)
          } else {
            setError('Failed to load participants: Unknown error')
          }
        } finally {
          setLoading(false)
        }
        break
      }
    }

    fetchData()
  }, [])

  // Memoize filtered participants to prevent unnecessary recalculations
  const filteredParticipants = useMemo(() => {
    if (!Array.isArray(participants)) {
      console.error('Participants is not an array:', participants)
      return []
    }
    
    let filtered: Participant[] = []
    
    switch (activeTab) {
      case 'hosts':
        filtered = participants.filter(p => p.role === 'host' || p.role === 'both')
        break
      case 'speakers':
        filtered = participants.filter(p => p.role === 'speaker' || p.role === 'both')
        break
      case 'overall':
        filtered = [...participants]
        break
    }

    // Sort by the appropriate metric based on the tab
    return filtered.sort((a, b) => {
      switch (activeTab) {
        case 'hosts':
          return (b.host_spaces || 0) - (a.host_spaces || 0)
        case 'speakers':
          return (b.speaker_spaces || 0) - (a.speaker_spaces || 0)
        case 'overall':
          return (b.spaces || 0) - (a.spaces || 0)
        default:
          return 0
      }
    })
  }, [participants, activeTab])

  // Memoize paginated participants
  const paginatedParticipants = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
    return filteredParticipants.slice(startIndex, startIndex + ITEMS_PER_PAGE)
  }, [filteredParticipants, currentPage])

  const totalPages = Math.ceil(filteredParticipants.length / ITEMS_PER_PAGE)

  const handleTabChange = (tab: 'hosts' | 'speakers' | 'overall') => {
    setActiveTab(tab)
    setCurrentPage(1)
  }

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Top Participants</h2>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Top Participants</h2>
        <div className="text-amber-600 bg-amber-50 p-4 rounded-lg">
          <p className="font-medium">No data available yet</p>
          <p className="text-sm mt-1">
            The data collection process is still running. Please check back later.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Top Participants</h2>
      
      {/* Category Tabs */}
      <div className="border-b border-gray-200 mb-4 overflow-x-auto">
        <nav className="-mb-px flex space-x-8 min-w-max">
          <button
            onClick={() => handleTabChange('hosts')}
            className={`${
              activeTab === 'hosts'
                ? 'border-red-500 text-red-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Top Hosts
          </button>
          <button
            onClick={() => handleTabChange('speakers')}
            className={`${
              activeTab === 'speakers'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Top Speakers
          </button>
          <button
            onClick={() => handleTabChange('overall')}
            className={`${
              activeTab === 'overall'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Most Active Overall
          </button>
        </nav>
      </div>

      {/* Participants List */}
      <div className="space-y-2 overflow-x-auto">
        <div className="min-w-max">
          {paginatedParticipants.map((participant, index) => (
            <div
              key={`${activeTab}-${participant.name}`}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2"
            >
              <div className="flex items-center space-x-4">
                <span className="text-gray-500 font-medium">{index + 1 + (currentPage - 1) * ITEMS_PER_PAGE}.</span>
                <div>
                  <h3 className="font-medium text-gray-900">{participant.name}</h3>
                  <p className="text-sm text-gray-500">
                    {activeTab === 'hosts' && `${participant.host_spaces} host spaces`}
                    {activeTab === 'speakers' && `${participant.speaker_spaces} speaker spaces`}
                    {activeTab === 'overall' && `${participant.spaces} total spaces`}
                  </p>
                </div>
              </div>
              {participant.twitter && (
                <a
                  href={participant.twitter}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                  title="View on X"
                >
                  <svg 
                    viewBox="0 0 24 24" 
                    className="w-5 h-5 fill-current"
                    aria-hidden="true"
                  >
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                  </svg>
                </a>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex justify-center space-x-2">
          <button
            onClick={() => setCurrentPage(1)}
            disabled={currentPage === 1}
            className={`px-3 py-1 rounded ${
              currentPage === 1
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
            }`}
          >
            First
          </button>
          <button
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className={`px-3 py-1 rounded ${
              currentPage === 1
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
            }`}
          >
            Previous
          </button>
          <span className="px-3 py-1 text-gray-600">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className={`px-3 py-1 rounded ${
              currentPage === totalPages
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
            }`}
          >
            Next
          </button>
          <button
            onClick={() => setCurrentPage(totalPages)}
            disabled={currentPage === totalPages}
            className={`px-3 py-1 rounded ${
              currentPage === totalPages
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
            }`}
          >
            Last
          </button>
        </div>
      )}
    </div>
  )
}

export default TopParticipants 