import { useEffect, useState } from 'react'
import axios from 'axios'

interface ParticipantDetailsProps {
  participantId: string
}

interface ParticipantDetails {
  id: string
  role: string
  spaces: string[]
  connections: Array<{
    id: string
    role: string
    spaces: string[]
  }>
}

const ParticipantDetails = ({ participantId }: ParticipantDetailsProps) => {
  const [details, setDetails] = useState<ParticipantDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const response = await axios.get<ParticipantDetails>(`/api/participants/${participantId}`)
        setDetails(response.data)
        setLoading(false)
      } catch (error) {
        setError('Failed to fetch participant details')
        setLoading(false)
      }
    }

    fetchDetails()
  }, [participantId])

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-xl font-semibold mb-4">Participant Details</h2>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  if (error || !details) {
    return (
      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-xl font-semibold mb-4">Participant Details</h2>
        <div className="text-red-500">{error || 'No details available'}</div>
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h2 className="text-xl font-semibold mb-4">Participant Details</h2>
      <div className="space-y-4">
        <div>
          <h3 className="font-medium text-gray-700">ID</h3>
          <p className="text-gray-900">{details.id}</p>
        </div>
        <div>
          <h3 className="font-medium text-gray-700">Role</h3>
          <p className="text-gray-900 capitalize">{details.role}</p>
        </div>
        <div>
          <h3 className="font-medium text-gray-700">Spaces</h3>
          <div className="mt-1 space-y-1">
            {details.spaces.map((space) => (
              <div key={space} className="text-sm text-gray-600">
                {space}
              </div>
            ))}
          </div>
        </div>
        <div>
          <h3 className="font-medium text-gray-700">Connections</h3>
          <div className="mt-1 space-y-1">
            {details.connections.map((connection) => (
              <div key={connection.id} className="text-sm text-gray-600">
                {connection.id} ({connection.role})
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ParticipantDetails 