import { useEffect, useState } from 'react'
import axios from 'axios'
import { apiBaseUrl } from '../config'

interface ParticipantListProps {
  onSelectParticipant: (id: string) => void
}

interface Participant {
  name: string
  id: string
  twitter: string | null
  alphagrowth_link: string | null
  host_spaces: string[]
  speaker_spaces: string[]
  total_spaces: number
  node_color: string
}

const ParticipantList = ({ onSelectParticipant }: ParticipantListProps) => {
  const [participants, setParticipants] = useState<Participant[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchParticipants = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await axios.get<Participant[]>(`${apiBaseUrl}/api/participants`)
        console.log('Fetched participants data:', response.data)
        if (Array.isArray(response.data)) {
          setParticipants(response.data)
        } else {
          setError('Invalid data format')
          console.error('Invalid data format:', response.data)
        }
      } catch (err) {
        setError('Failed to fetch participants')
        console.error('Error fetching participants:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchParticipants()
  }, [])

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-xl font-semibold mb-4">Participants</h2>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-xl font-semibold mb-4">Participants</h2>
        <div className="text-red-500">{error}</div>
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h2 className="text-xl font-semibold mb-4">Participants</h2>
      <div className="space-y-2 max-h-[400px] overflow-y-auto">
        {participants.map((participant) => (
          <button
            key={participant.id}
            onClick={() => onSelectParticipant(participant.id)}
            className="w-full text-left p-2 hover:bg-gray-100 rounded flex items-center space-x-2"
          >
            <span 
              className="w-2 h-2 rounded-full" 
              style={{ backgroundColor: participant.node_color }}
            ></span>
            <span className="truncate">{participant.name}</span>
            {participant.twitter && (
              <a 
                href={participant.twitter} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-500 hover:text-blue-700"
                onClick={(e) => e.stopPropagation()}
              >
                Twitter
              </a>
            )}
          </button>
        ))}
      </div>
    </div>
  )
}

export default ParticipantList 