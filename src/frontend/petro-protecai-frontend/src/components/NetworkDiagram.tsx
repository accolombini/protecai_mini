import { useState, useEffect } from 'react'

// Interfaces para dados da rede
interface BusData {
  x: number
  y: number
  voltage: number
}

interface LineData {
  id: string
  from: number
  to: number
  status: string
  current: number
}

interface NetworkTopology {
  buses: Record<number, BusData>
  lines: LineData[]
}

interface ProtectionZone {
  zone_id: string
  zone_type: string
  device_id: string
  device_type: string
  coverage_area: Array<{x: number, y: number}>
  protected_elements: string[]
  reach_settings: Record<string, number>
  coordination_margin: number
  priority: number
}

interface ZoneVisualizationData {
  network_topology: NetworkTopology
  protection_zones: ProtectionZone[]
  device_locations: Record<string, {x: number, y: number, status: string}>
  color_scheme: Record<string, string>
  analysis_summary: {
    total_zones: number
    primary_zones: number
    backup_zones: number
    coverage_percentage: number
    coordination_score: number
    overall_assessment: string
  }
}

export function NetworkDiagram() {
  const [networkData, setNetworkData] = useState<ZoneVisualizationData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showZones, setShowZones] = useState(true)
  const [showDevices, setShowDevices] = useState(true)
  const [selectedZone, setSelectedZone] = useState<string | null>(null)

  useEffect(() => {
    fetchNetworkVisualization()
  }, [])

  const fetchNetworkVisualization = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/v1/protection-zones/visualization/complete')
      
      if (!response.ok) {
        throw new Error(`Erro ao carregar visualização da rede: ${response.status}`)
      }

      const data = await response.json()
      setNetworkData(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
      console.error('Erro ao carregar visualização da rede:', err)
    } finally {
      setLoading(false)
    }
  }

  // Função para escalar coordenadas para o SVG
  const scaleCoordinate = (coord: number, isX: boolean) => {
    const scale = 80  // escala para o SVG
    const offset = isX ? 50 : 30  // offset para centralizar
    return coord * scale + offset
  }

  const getZoneColor = (zoneType: string) => {
    if (!networkData) return '#gray'
    
    switch (zoneType) {
      case 'primary': return networkData.color_scheme.primary_zone || '#FF6B6B'
      case 'backup': return networkData.color_scheme.backup_zone || '#4ECDC4'
      case 'emergency': return networkData.color_scheme.emergency_zone || '#45B7D1'
      default: return '#gray'
    }
  }

  const getDeviceStatusColor = (status: string) => {
    if (!networkData) return '#gray'
    
    switch (status) {
      case 'active': return networkData.color_scheme.device_active || '#00B894'
      case 'alarm': return networkData.color_scheme.device_alarm || '#E84393'
      case 'monitoring': return networkData.color_scheme.network_normal || '#74B9FF'
      default: return '#gray'
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-center items-center h-96">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Carregando diagrama da rede...</span>
        </div>
      </div>
    )
  }

  if (error || !networkData) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Erro ao Carregar Diagrama</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={fetchNetworkVisualization}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header com controles */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">IEEE 14 Bus System - Rede Petrolífera</h2>
          <div className="flex space-x-4">
            <button
              onClick={() => setShowZones(!showZones)}
              className={`px-4 py-2 rounded-md transition-colors ${
                showZones 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {showZones ? 'Ocultar' : 'Mostrar'} Zonas
            </button>
            <button
              onClick={() => setShowDevices(!showDevices)}
              className={`px-4 py-2 rounded-md transition-colors ${
                showDevices 
                  ? 'bg-green-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {showDevices ? 'Ocultar' : 'Mostrar'} Dispositivos
            </button>
          </div>
        </div>

        {/* Métricas rápidas */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{Object.keys(networkData.network_topology.buses).length}</div>
            <div className="text-sm text-gray-600">Barras</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{networkData.network_topology.lines.length}</div>
            <div className="text-sm text-gray-600">Linhas</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{networkData.analysis_summary.primary_zones}</div>
            <div className="text-sm text-gray-600">Zonas Primárias</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{networkData.analysis_summary.backup_zones}</div>
            <div className="text-sm text-gray-600">Zonas Backup</div>
          </div>
        </div>
      </div>

      {/* Diagrama principal */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="w-full overflow-x-auto">
          <svg width="800" height="600" className="border border-gray-200 rounded-lg">
            {/* Grid de fundo */}
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#f0f0f0" strokeWidth="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />

            {/* Zonas de proteção (se habilitadas) */}
            {showZones && networkData.protection_zones.map((zone) => (
              <g key={zone.zone_id}>
                {zone.coverage_area.length > 2 && (
                  <polygon
                    points={zone.coverage_area.map(point => 
                      `${scaleCoordinate(point.x, true)},${scaleCoordinate(point.y, false)}`
                    ).join(' ')}
                    fill={getZoneColor(zone.zone_type)}
                    fillOpacity="0.2"
                    stroke={getZoneColor(zone.zone_type)}
                    strokeWidth="2"
                    strokeDasharray={zone.zone_type === 'backup' ? '5,5' : 'none'}
                    className="cursor-pointer hover:fillOpacity-0.3 transition-all"
                    onClick={() => setSelectedZone(selectedZone === zone.zone_id ? null : zone.zone_id)}
                  />
                )}
              </g>
            ))}

            {/* Linhas de transmissão */}
            {networkData.network_topology.lines.map((line) => {
              const fromBus = networkData.network_topology.buses[line.from]
              const toBus = networkData.network_topology.buses[line.to]
              
              if (!fromBus || !toBus) return null

              const isHighCurrent = line.current > 200
              
              return (
                <g key={line.id}>
                  <line
                    x1={scaleCoordinate(fromBus.x, true)}
                    y1={scaleCoordinate(fromBus.y, false)}
                    x2={scaleCoordinate(toBus.x, true)}
                    y2={scaleCoordinate(toBus.y, false)}
                    stroke={isHighCurrent ? "#dc2626" : "#374151"}
                    strokeWidth={isHighCurrent ? "4" : "2"}
                    className="hover:stroke-blue-500 transition-colors"
                  />
                  
                  {/* Label da linha */}
                  <text
                    x={(scaleCoordinate(fromBus.x, true) + scaleCoordinate(toBus.x, true)) / 2}
                    y={(scaleCoordinate(fromBus.y, false) + scaleCoordinate(toBus.y, false)) / 2 - 5}
                    fontSize="10"
                    fill="#666"
                    textAnchor="middle"
                    className="pointer-events-none"
                  >
                    {line.id}
                  </text>
                  
                  {/* Corrente */}
                  <text
                    x={(scaleCoordinate(fromBus.x, true) + scaleCoordinate(toBus.x, true)) / 2}
                    y={(scaleCoordinate(fromBus.y, false) + scaleCoordinate(toBus.y, false)) / 2 + 12}
                    fontSize="9"
                    fill={isHighCurrent ? "#dc2626" : "#666"}
                    textAnchor="middle"
                    className="pointer-events-none font-medium"
                  >
                    {line.current}A
                  </text>
                </g>
              )
            })}

            {/* Barras do sistema */}
            {Object.entries(networkData.network_topology.buses).map(([busId, bus]) => (
              <g key={busId}>
                <circle
                  cx={scaleCoordinate(bus.x, true)}
                  cy={scaleCoordinate(bus.y, false)}
                  r="8"
                  fill="#3b82f6"
                  stroke="#1e40af"
                  strokeWidth="2"
                  className="hover:r-10 transition-all cursor-pointer"
                />
                
                {/* Número da barra */}
                <text
                  x={scaleCoordinate(bus.x, true)}
                  y={scaleCoordinate(bus.y, false) + 3}
                  fontSize="10"
                  fill="white"
                  textAnchor="middle"
                  className="pointer-events-none font-bold"
                >
                  {busId}
                </text>
                
                {/* Tensão */}
                <text
                  x={scaleCoordinate(bus.x, true)}
                  y={scaleCoordinate(bus.y, false) - 20}
                  fontSize="10"
                  fill="#374151"
                  textAnchor="middle"
                  className="pointer-events-none"
                >
                  {bus.voltage}kV
                </text>
              </g>
            ))}

            {/* Dispositivos de proteção (se habilitados) */}
            {showDevices && Object.entries(networkData.device_locations).map(([deviceId, device]) => (
              <g key={deviceId}>
                <rect
                  x={scaleCoordinate(device.x, true) - 8}
                  y={scaleCoordinate(device.y, false) - 8}
                  width="16"
                  height="16"
                  fill={getDeviceStatusColor(device.status)}
                  stroke="#1f2937"
                  strokeWidth="1"
                  rx="2"
                  className="hover:stroke-2 transition-all cursor-pointer"
                  onClick={() => console.log(`Dispositivo: ${deviceId}`)}
                />
                
                {/* Ícone do dispositivo */}
                <text
                  x={scaleCoordinate(device.x, true)}
                  y={scaleCoordinate(device.y, false) + 3}
                  fontSize="8"
                  fill="white"
                  textAnchor="middle"
                  className="pointer-events-none font-bold"
                >
                  ⚡
                </text>
                
                {/* ID do dispositivo */}
                <text
                  x={scaleCoordinate(device.x, true)}
                  y={scaleCoordinate(device.y, false) + 25}
                  fontSize="8"
                  fill="#374151"
                  textAnchor="middle"
                  className="pointer-events-none"
                >
                  {deviceId.replace('relay_', '').replace('_', '-')}
                </text>
              </g>
            ))}
          </svg>
        </div>

        {/* Legenda */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Zonas de Proteção</h4>
            <div className="space-y-1 text-sm">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-red-500 rounded mr-2 opacity-50"></div>
                <span>Zona Primária</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-teal-500 rounded mr-2 opacity-50 border-dashed border-2 border-teal-600"></div>
                <span>Zona Backup</span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Dispositivos</h4>
            <div className="space-y-1 text-sm">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-green-600 rounded mr-2"></div>
                <span>Ativo</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-blue-500 rounded mr-2"></div>
                <span>Monitorando</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-red-500 rounded mr-2"></div>
                <span>Alarme</span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Linhas</h4>
            <div className="space-y-1 text-sm">
              <div className="flex items-center">
                <div className="w-6 h-0.5 bg-gray-600 mr-2"></div>
                <span>Normal (&lt;200A)</span>
              </div>
              <div className="flex items-center">
                <div className="w-6 h-1 bg-red-600 mr-2"></div>
                <span>Alta Corrente (&gt;200A)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Painel de informações da zona selecionada */}
      {selectedZone && (
        <div className="bg-white rounded-lg shadow p-6">
          {(() => {
            const zone = networkData.protection_zones.find(z => z.zone_id === selectedZone)
            if (!zone) return null
            
            return (
              <div>
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold text-gray-900">
                    Detalhes da Zona: {zone.zone_id}
                  </h3>
                  <button
                    onClick={() => setSelectedZone(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Informações Gerais</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tipo:</span>
                        <span className="font-medium capitalize">{zone.zone_type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Dispositivo:</span>
                        <span className="font-medium">{zone.device_id}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tipo Dispositivo:</span>
                        <span className="font-medium">{zone.device_type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Prioridade:</span>
                        <span className="font-medium">{zone.priority}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Margem Coordenação:</span>
                        <span className="font-medium">{(zone.coordination_margin * 1000).toFixed(0)}ms</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Elementos Protegidos</h4>
                    <div className="space-y-1">
                      {zone.protected_elements.map((element, index) => (
                        <div key={index} className="text-sm bg-gray-100 px-2 py-1 rounded">
                          {element}
                        </div>
                      ))}
                    </div>
                    
                    <h4 className="font-medium text-gray-900 mb-2 mt-4">Configurações de Alcance</h4>
                    <div className="space-y-1 text-sm">
                      {Object.entries(zone.reach_settings).map(([setting, value]) => (
                        <div key={setting} className="flex justify-between">
                          <span className="text-gray-600 capitalize">{setting}:</span>
                          <span className="font-medium">{value.toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )
          })()}
        </div>
      )}

      {/* Resumo da análise */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Resumo da Análise</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {networkData.analysis_summary.coverage_percentage}%
            </div>
            <div className="text-sm text-gray-600">Cobertura de Proteção</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {networkData.analysis_summary.coordination_score}%
            </div>
            <div className="text-sm text-gray-600">Score de Coordenação</div>
          </div>
          
          <div className="text-center">
            <div className={`text-3xl font-bold mb-2 ${
              networkData.analysis_summary.overall_assessment === 'excellent' ? 'text-green-600' :
              networkData.analysis_summary.overall_assessment === 'good' ? 'text-blue-600' :
              networkData.analysis_summary.overall_assessment === 'acceptable' ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {networkData.analysis_summary.overall_assessment.toUpperCase()}
            </div>
            <div className="text-sm text-gray-600">Avaliação Geral</div>
          </div>
        </div>
      </div>
    </div>
  )
}
