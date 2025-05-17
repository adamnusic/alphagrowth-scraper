import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import axios from 'axios'

interface NetworkGraphProps {
  onSelectParticipant: (id: string) => void
}

interface NetworkNode extends d3.SimulationNodeDatum {
  id: string
  size: number
  color: string
  name: string
  twitter: string
}

interface NetworkLink extends d3.SimulationLinkDatum<NetworkNode> {
  source: string
  target: string
  value: number
}

interface NetworkData {
  nodes: NetworkNode[]
  links: NetworkLink[]
}

const API_BASE_URL = 'http://localhost:5002'

const NetworkGraph = ({ onSelectParticipant }: NetworkGraphProps) => {
  const svgRef = useRef<SVGSVGElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('')
  const [minConnections, setMinConnections] = useState<number>(1)
  const [layout, setLayout] = useState<'force' | 'radial'>('force')
  const [networkData, setNetworkData] = useState<NetworkData | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get<NetworkData>(`${API_BASE_URL}/api/network`)
        setNetworkData(response.data)
        setError(null)
      } catch (error) {
        console.error('Error fetching network data:', error)
        setError('Failed to load network data')
      }
    }

    fetchData()
  }, [])

  useEffect(() => {
    if (!networkData || !svgRef.current) return

    // Clear previous graph
    d3.select(svgRef.current).selectAll('*').remove()

    const width = 800
    const height = 600

    // Filter nodes and links based on criteria
    const filteredNodes = networkData.nodes.filter(node => {
      const connections = networkData.links.filter(
        link => link.source === node.id || link.target === node.id
      ).length
      return node.name.toLowerCase().includes(filter.toLowerCase()) && connections >= minConnections
    })

    const filteredLinks = networkData.links.filter(link => {
      const sourceNode = filteredNodes.find(n => n.id === link.source)
      const targetNode = filteredNodes.find(n => n.id === link.target)
      return sourceNode && targetNode
    })

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)

    // Create zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        svg.select('g').attr('transform', event.transform)
      })

    svg.call(zoom as any)

    // Create main group for zooming
    const g = svg.append('g')

    // Create simulation
    const simulation = d3.forceSimulation(filteredNodes)
      .force('link', d3.forceLink(filteredLinks).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))

    if (layout === 'radial') {
      simulation.force('radial', d3.forceRadial(
        (d: any) => d.size * 50,
        width / 2,
        height / 2
      ).strength(0.5))
    }

    // Create links
    const link = g.append('g')
      .selectAll('line')
      .data(filteredLinks)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d: any) => Math.sqrt(d.value))

    // Create nodes
    const node = g.append('g')
      .selectAll('g')
      .data(filteredNodes)
      .join('g')
      .call(d3.drag<any, any>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))

    // Add circles to nodes
    node.append('circle')
      .attr('r', (d: any) => Math.sqrt(d.size) * 2)
      .attr('fill', (d: any) => d.color)
      .on('click', (event: any, d: any) => onSelectParticipant(d.id))

    // Add labels to nodes
    node.append('text')
      .text((d: any) => d.name)
      .attr('x', (d: any) => Math.sqrt(d.size) * 2 + 5)
      .attr('y', 4)
      .style('font-size', '10px')
      .style('pointer-events', 'none')

    // Add tooltips
    node.append('title')
      .text((d: any) => `${d.name}\nTwitter: ${d.twitter}\nConnections: ${filteredLinks.filter(l => l.source === d.id || l.target === d.id).length}`)

    // Update positions on each tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
    })

    // Drag functions
    function dragstarted(event: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      event.subject.fx = event.subject.x
      event.subject.fy = event.subject.y
    }

    function dragged(event: any) {
      event.subject.fx = event.x
      event.subject.fy = event.y
    }

    function dragended(event: any) {
      if (!event.active) simulation.alphaTarget(0)
      event.subject.fx = null
      event.subject.fy = null
    }
  }, [networkData, filter, minConnections, layout, onSelectParticipant])

  if (error) {
    return (
      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-xl font-semibold mb-4">Network Graph</h2>
        <div className="text-red-500">{error}</div>
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h2 className="text-xl font-semibold mb-4">Network Graph</h2>
      <div className="mb-4 space-y-4">
        <div className="flex space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700">Filter by name</label>
            <input
              type="text"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="Search participants..."
            />
          </div>
          <div className="w-48">
            <label className="block text-sm font-medium text-gray-700">Min connections</label>
            <input
              type="number"
              value={minConnections}
              onChange={(e) => setMinConnections(Number(e.target.value))}
              min="0"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div className="w-48">
            <label className="block text-sm font-medium text-gray-700">Layout</label>
            <select
              value={layout}
              onChange={(e) => setLayout(e.target.value as 'force' | 'radial')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="force">Force-directed</option>
              <option value="radial">Radial</option>
            </select>
          </div>
        </div>
        <div className="text-sm text-gray-500">
          <p>• Drag nodes to rearrange the network</p>
          <p>• Click on a node to view participant details</p>
          <p>• Use mouse wheel to zoom in/out</p>
          <p>• Drag the background to pan</p>
        </div>
      </div>
      <svg ref={svgRef} className="w-full h-[600px] border border-gray-200 rounded"></svg>
    </div>
  )
}

export default NetworkGraph 