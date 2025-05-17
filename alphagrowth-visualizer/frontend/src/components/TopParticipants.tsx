import { useEffect, useState, useMemo } from 'react'
import axios from 'axios'
import { apiBaseUrl } from '../config'

interface Participant {
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
            timeout: 5000, // 5 second timeout
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            }
          })
          setParticipants(response.data)
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
              await new Promise(resolve => setTimeout(resolve, 1000)) // Wait 1 second before retry
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

      try {
        console.log('Fetching participants from:', `${apiBaseUrl}/api/participants`)
        const response = await axios.get<Participant[]>(`${apiBaseUrl}/api/participants`)
        setParticipants(response.data)
        setError(null)
      } catch (error) {
        console.error('Error fetching participants:', error)
        if (axios.isAxiosError(error)) {
          console.error('Response data:', error.response?.data)
          console.error('Response status:', error.response?.status)
          setError(`Failed to load participants: ${error.response?.data?.message || error.message}`)
        } else {
          setError('Failed to load participants: Unknown error')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Memoize filtered participants to prevent unnecessary recalculations
  const filteredParticipants = useMemo(() => {
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
          return b.host_spaces - a.host_spaces
        case 'speakers':
          return b.speaker_spaces - a.speaker_spaces
        case 'overall':
          return b.spaces - a.spaces
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
              <div className="flex items-center space-x-3">
                <span className="text-gray-500 font-medium w-8">#{(currentPage - 1) * ITEMS_PER_PAGE + index + 1}</span>
                <span className="font-medium min-w-[200px]">{participant.name}</span>
                <span className="text-sm text-gray-500">
                  ({participant.role === 'both' ? 'Host & Speaker' : participant.role})
                </span>
                {participant.twitter && (
                  <a
                    href={participant.twitter}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                    </svg>
                  </a>
                )}
              </div>
              <span className="text-sm font-medium text-gray-900 ml-4">
                {activeTab === 'hosts' ? participant.host_spaces :
                 activeTab === 'speakers' ? participant.speaker_spaces :
                 participant.spaces} spaces
                {participant.role === 'both' && (
                  <span className="text-gray-500 ml-2">
                    ({participant.host_spaces} hosted, {participant.speaker_spaces} spoken)
                  </span>
                )}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex flex-col sm:flex-row items-center justify-between border-t border-gray-200 pt-4">
          <div className="mb-4 sm:mb-0">
            <p className="text-sm text-gray-700">
              Showing <span className="font-medium">{(currentPage - 1) * ITEMS_PER_PAGE + 1}</span> to{' '}
              <span className="font-medium">
                {Math.min(currentPage * ITEMS_PER_PAGE, filteredParticipants.length)}
              </span>{' '}
              of <span className="font-medium">{filteredParticipants.length}</span> results
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
              className="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              First
            </button>
            <button
              onClick={() => setCurrentPage(page => Math.max(1, page - 1))}
              disabled={currentPage === 1}
              className="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              className="relative inline-flex items-center px-3 py-2 border text-sm font-medium z-10 bg-blue-50 border-blue-500 text-blue-600"
            >
              {currentPage}
            </button>
            <button
              onClick={() => setCurrentPage(page => Math.min(totalPages, page + 1))}
              disabled={currentPage === totalPages}
              className="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
            <button
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage === totalPages}
              className="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Last
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default TopParticipants 