import { useState, useEffect } from 'react'

// Interfaces para os dados dos dispositivos
interface DeviceRealTimeStatus {
  zone_id: string
  status: 'armed' | 'monitoring' | 'alarm'
  current_pickup: number
  threshold: number
  margin_percent: number
  last_operation: string | null
}

interface DeviceDetailedInfo {
  device_id: string
  location: string
  pickup_current: string
  time_dial: string
  reach_percentage: string
  coordination_margin: string
  standards_compliance: {
    IEEE_C37_112: string
    IEC_60255: string
    ANSI_C37_90: string
  }
}

interface ZoneDetail {
  description: string
  devices: DeviceDetailedInfo[]
  total_devices: number
  coverage_area: string
  operation_time: string
  selectivity_index: number
}

interface ZoneConfiguration {
  zona_1_primaria: ZoneDetail
  zona_2_backup: ZoneDetail
}

interface RealtimeStatusSummary {
  total_zones: number
  armed_zones: number
  monitoring_zones: number
  alarm_zones: number
  average_margin: number
  system_health: 'good' | 'attention' | 'critical'
}

export function DeviceManagement() {
  const [realtimeStatus, setRealtimeStatus] = useState<DeviceRealTimeStatus[]>([])
  const [zoneConfiguration, setZoneConfiguration] = useState<ZoneConfiguration | null>(null)
  const [statusSummary, setStatusSummary] = useState<RealtimeStatusSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null)
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'device_id' | 'status' | 'margin'>('device_id')

  useEffect(() => {
    Promise.all([
      fetchRealtimeStatus(),
      fetchZoneConfiguration()
    ])
  }, [])

  const fetchRealtimeStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/protection-zones/zones/real-time-status')
      
      if (!response.ok) {
        throw new Error(`Erro ao carregar status em tempo real: ${response.status}`)
      }

      const data = await response.json()
      setRealtimeStatus(data.zones_status)
      setStatusSummary(data.summary)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
      console.error('Erro ao carregar status em tempo real:', err)
    }
  }

  const fetchZoneConfiguration = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/v1/protection-zones/zones/detailed-configuration')
      
      if (!response.ok) {
        throw new Error(`Erro ao carregar configuração das zonas: ${response.status}`)
      }

      const data = await response.json()
      setZoneConfiguration(data.zone_configuration)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
      console.error('Erro ao carregar configuração das zonas:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'armed': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'monitoring': return 'bg-green-100 text-green-800 border-green-200'
      case 'alarm': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getMarginColor = (margin: number) => {
    if (margin >= 30) return 'text-green-600'
    if (margin >= 15) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getComplianceColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'compliant': return 'text-green-600'
      case 'marginal': return 'text-yellow-600'
      case 'non_compliant': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const filterDevices = (devices: DeviceDetailedInfo[], zoneType: 'primary' | 'backup') => {
    // Combine static config with realtime status
    return devices.map(device => {
      const realtimeData = realtimeStatus.find(rt => 
        rt.zone_id.includes(device.device_id) || 
        rt.zone_id.includes(device.device_id.replace('relay_', '').replace('_', '-'))
      )
      
      return {
        ...device,
        realtime: realtimeData,
        zone_type: zoneType
      }
    }).filter(device => {
      if (filterStatus === 'all') return true
      return device.realtime?.status === filterStatus
    }).sort((a, b) => {
      switch (sortBy) {
        case 'status':
          return (a.realtime?.status || 'zzz').localeCompare(b.realtime?.status || 'zzz')
        case 'margin':
          return (b.realtime?.margin_percent || 0) - (a.realtime?.margin_percent || 0)
        default:
          return a.device_id.localeCompare(b.device_id)
      }
    })
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Carregando gerenciamento de dispositivos...</span>
        </div>
      </div>
    )
  }

  if (error || !zoneConfiguration || !statusSummary) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Erro ao Carregar Dispositivos</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => Promise.all([fetchRealtimeStatus(), fetchZoneConfiguration()])}
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
      {/* Header com resumo do sistema */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Gerenciamento de Dispositivos</h2>
          <div className={`px-4 py-2 rounded-lg font-medium ${
            statusSummary.system_health === 'good' ? 'bg-green-100 text-green-800' :
            statusSummary.system_health === 'attention' ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            Status do Sistema: {statusSummary.system_health.toUpperCase()}
          </div>
        </div>

        {/* Cards de resumo */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">{statusSummary.total_zones}</div>
            <div className="text-sm text-gray-600">Total de Zonas</div>
          </div>
          
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">{statusSummary.armed_zones}</div>
            <div className="text-sm text-gray-600">Armadas</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{statusSummary.monitoring_zones}</div>
            <div className="text-sm text-gray-600">Monitorando</div>
          </div>
          
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">{statusSummary.alarm_zones}</div>
            <div className="text-sm text-gray-600">Em Alarme</div>
          </div>
          
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{statusSummary.average_margin.toFixed(1)}%</div>
            <div className="text-sm text-gray-600">Margem Média</div>
          </div>
        </div>
      </div>

      {/* Controles e filtros */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex gap-4">
            {/* Filtro por status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Filtrar por Status</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Todos</option>
                <option value="armed">Armado</option>
                <option value="monitoring">Monitorando</option>
                <option value="alarm">Alarme</option>
              </select>
            </div>

            {/* Ordenação */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ordenar por</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="border border-gray-300 rounded-md px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="device_id">ID do Dispositivo</option>
                <option value="status">Status</option>
                <option value="margin">Margem de Coordenação</option>
              </select>
            </div>
          </div>

          {/* Botão de atualização */}
          <button
            onClick={() => Promise.all([fetchRealtimeStatus(), fetchZoneConfiguration()])}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Atualizar
          </button>
        </div>
      </div>

      {/* Lista de dispositivos organizados por zona */}
      <div className="grid gap-6">
        {/* Zona 1 - Primária */}
        <div className="bg-white rounded-lg shadow">
          <div className="bg-red-500 text-white px-6 py-4 rounded-t-lg">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold">Zona 1 - Primária</h3>
              <div className="text-red-100">
                {filterDevices(zoneConfiguration.zona_1_primaria.devices, 'primary').length} dispositivos
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid gap-4">
              {filterDevices(zoneConfiguration.zona_1_primaria.devices, 'primary').map((device) => (
                <div 
                  key={device.device_id}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => setSelectedDevice(selectedDevice === device.device_id ? null : device.device_id)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <div className="font-bold text-gray-900 mr-3">{device.device_id}</div>
                      <div className="text-sm text-gray-600">{device.location}</div>
                    </div>
                    
                    {device.realtime && (
                      <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(device.realtime.status)}`}>
                        {device.realtime.status.toUpperCase()}
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Pickup:</span>
                      <span className="font-medium ml-1">{device.pickup_current}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Tempo:</span>
                      <span className="font-medium ml-1">{device.time_dial}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Alcance:</span>
                      <span className="font-medium ml-1">{device.reach_percentage}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Margem:</span>
                      <span className="font-medium ml-1">{device.coordination_margin}</span>
                    </div>
                  </div>

                  {device.realtime && (
                    <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Corrente Atual:</span>
                        <span className="font-medium ml-1">{device.realtime.current_pickup.toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Limiar:</span>
                        <span className="font-medium ml-1">{device.realtime.threshold}%</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Margem:</span>
                        <span className={`font-medium ml-1 ${getMarginColor(device.realtime.margin_percent)}`}>
                          {device.realtime.margin_percent.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Detalhes expandidos */}
                  {selectedDevice === device.device_id && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <h4 className="font-medium text-gray-900 mb-3">Conformidade com Normas</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        {Object.entries(device.standards_compliance).map(([standard, status]) => (
                          <div key={standard} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <span className="text-sm text-gray-600">{standard.replace(/_/g, ' ')}</span>
                            <span className={`text-sm font-medium ${getComplianceColor(status)}`}>
                              {status}
                            </span>
                          </div>
                        ))}
                      </div>
                      
                      {device.realtime?.last_operation && (
                        <div className="mt-3">
                          <span className="text-sm text-gray-600">Última Operação:</span>
                          <span className="text-sm font-medium ml-1">
                            {new Date(device.realtime.last_operation).toLocaleString('pt-BR')}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Zona 2 - Backup */}
        <div className="bg-white rounded-lg shadow">
          <div className="bg-blue-600 text-white px-6 py-4 rounded-t-lg">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold">Zona 2 - Backup</h3>
              <div className="text-blue-100">
                {filterDevices(zoneConfiguration.zona_2_backup.devices, 'backup').length} dispositivos
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid gap-4">
              {filterDevices(zoneConfiguration.zona_2_backup.devices, 'backup').map((device) => (
                <div 
                  key={device.device_id}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => setSelectedDevice(selectedDevice === device.device_id ? null : device.device_id)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <div className="font-bold text-gray-900 mr-3">{device.device_id}</div>
                      <div className="text-sm text-gray-600">{device.location}</div>
                    </div>
                    
                    {device.realtime && (
                      <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(device.realtime.status)}`}>
                        {device.realtime.status.toUpperCase()}
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Pickup:</span>
                      <span className="font-medium ml-1">{device.pickup_current}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Tempo:</span>
                      <span className="font-medium ml-1">{device.time_dial}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Alcance:</span>
                      <span className="font-medium ml-1">{device.reach_percentage}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Margem:</span>
                      <span className="font-medium ml-1">{device.coordination_margin}</span>
                    </div>
                  </div>

                  {device.realtime && (
                    <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Corrente Atual:</span>
                        <span className="font-medium ml-1">{device.realtime.current_pickup.toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Limiar:</span>
                        <span className="font-medium ml-1">{device.realtime.threshold}%</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Margem:</span>
                        <span className={`font-medium ml-1 ${getMarginColor(device.realtime.margin_percent)}`}>
                          {device.realtime.margin_percent.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Detalhes expandidos */}
                  {selectedDevice === device.device_id && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <h4 className="font-medium text-gray-900 mb-3">Conformidade com Normas</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        {Object.entries(device.standards_compliance).map(([standard, status]) => (
                          <div key={standard} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <span className="text-sm text-gray-600">{standard.replace(/_/g, ' ')}</span>
                            <span className={`text-sm font-medium ${getComplianceColor(status)}`}>
                              {status}
                            </span>
                          </div>
                        ))}
                      </div>
                      
                      {device.realtime?.last_operation && (
                        <div className="mt-3">
                          <span className="text-sm text-gray-600">Última Operação:</span>
                          <span className="text-sm font-medium ml-1">
                            {new Date(device.realtime.last_operation).toLocaleString('pt-BR')}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Resumo de coordenação */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Resumo de Coordenação</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Zona 1 - Primária</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Seletividade:</span>
                <span className="font-medium text-green-600">{zoneConfiguration.zona_1_primaria.selectivity_index}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tempo de Operação:</span>
                <span className="font-medium">{zoneConfiguration.zona_1_primaria.operation_time}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Dispositivos Ativos:</span>
                <span className="font-medium">{zoneConfiguration.zona_1_primaria.total_devices}</span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Zona 2 - Backup</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Seletividade:</span>
                <span className="font-medium text-yellow-600">{zoneConfiguration.zona_2_backup.selectivity_index}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tempo de Operação:</span>
                <span className="font-medium">{zoneConfiguration.zona_2_backup.operation_time}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Dispositivos Ativos:</span>
                <span className="font-medium">{zoneConfiguration.zona_2_backup.total_devices}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
