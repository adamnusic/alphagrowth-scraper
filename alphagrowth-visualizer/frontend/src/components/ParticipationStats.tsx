import { useEffect, useState } from 'react'
import axios from 'axios'
import { apiBaseUrl } from '../config'

interface Stats {
  total_participants: number
  total_hosts: number
  total_speakers: number
  total_both: number
  total_spaces: number
  average_participants_per_space: number
  most_active_host: {
    name: string
    spaces: number
  }
  most_active_speaker: {
    name: string
    spaces: number
  }
}

const ParticipationStats = () => {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      let retries = 3
      while (retries > 0) {
        try {
          console.log('Fetching stats from:', `${apiBaseUrl}/api/stats`)
          const response = await axios.get<Stats>(`${apiBaseUrl}/api/stats`, {
            timeout: 15000,
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            withCredentials: false // Don't send credentials
          })
          setStats(response.data)
          setError(null)
          break
        } catch (error) {
          console.error('Error fetching stats:', error)
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
            setError(`Failed to load stats: ${error.response?.data?.message || error.message}`)
          } else {
            setError('Failed to load stats: Unknown error')
          }
        } finally {
          setLoading(false)
        }
        break
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Participation Statistics</h2>
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
        <h2 className="text-xl font-semibold mb-4">Participation Statistics</h2>
        <div className="text-amber-600 bg-amber-50 p-4 rounded-lg">
          <p className="font-medium">No data available yet</p>
          <p className="text-sm mt-1">
            The data collection process is still running. Please check back later.
          </p>
        </div>
      </div>
    )
  }

  if (!stats) return null

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Participation Statistics</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-blue-600">Total Participants</h3>
          <p className="mt-2 text-3xl font-semibold text-blue-900">{stats.total_participants}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-green-600">Total Spaces</h3>
          <p className="mt-2 text-3xl font-semibold text-green-900">{stats.total_spaces}</p>
          <p className="mt-1 text-sm text-green-600">
            Avg. {stats.average_participants_per_space.toFixed(1)} participants per space
          </p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-red-600">Total Hosts</h3>
          <p className="mt-2 text-3xl font-semibold text-red-900">{stats.total_hosts}</p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-purple-600">Total Speakers</h3>
          <p className="mt-2 text-3xl font-semibold text-purple-900">{stats.total_speakers}</p>
          <p className="mt-1 text-sm text-purple-600">
            {stats.total_both} participants have done both
          </p>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-orange-600">Most Active</h3>
          <div className="mt-2 space-y-2">
            <p className="text-sm">
              <span className="font-medium">Host:</span> {stats.most_active_host.name} ({stats.most_active_host.spaces} spaces)
            </p>
            <p className="text-sm">
              <span className="font-medium">Speaker:</span> {stats.most_active_speaker.name} ({stats.most_active_speaker.spaces} spaces)
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ParticipationStats 