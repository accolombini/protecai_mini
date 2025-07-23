import { useState, useEffect } from 'react'

// Interfaces para os dados das zonas
interface DeviceConfig {
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

interface ZoneData {
  description: string
  devices: DeviceConfig[]
  total_devices: number
  coverage_area: string
  operation_time: string
  selectivity_index: number
}

interface ZoneConfigurationData {
  network_overview: string
  zone_configuration: {
    zona_1_primaria: ZoneData
    zona_2_backup: ZoneData
  }
  coordination_analysis: {
    initial_settings: {
      coordination_method: string
      safety_margin: string
      pickup_coordination: string
      standards_reference: string[]
    }
    validation_criteria: {
      selectivity: string
      speed: string
      sensitivity: string
      stability: string
    }
    compliance_status: {
      overall: string
      critical_issues: number
      warnings: number
      recommendations: string[]
    }
  }
  last_validation: string
  next_review_due: string
}

export function ZoneConfiguration() {
  const [zoneData, setZoneData] = useState<ZoneConfigurationData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchZoneConfiguration()
  }, [])

  const fetchZoneConfiguration = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/v1/protection-zones/zones/detailed-configuration')
      
      if (!response.ok) {
        throw new Error(`Erro ao carregar configuração das zonas: ${response.status}`)
      }

      const data = await response.json()
      setZoneData(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
      console.error('Erro ao carregar configuração das zonas:', err)
    } finally {
      setLoading(false)
    }
  }

  const getComplianceColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'compliant': return 'text-green-600 bg-green-50'
      case 'marginal': return 'text-yellow-600 bg-yellow-50'
      case 'non_compliant': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getSelectivityColor = (index: number) => {
    if (index >= 95) return 'text-green-600'
    if (index >= 85) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Carregando configuração das zonas...</span>
        </div>
      </div>
    )
  }

  if (error || !zoneData) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Erro ao Carregar Configuração</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={fetchZoneConfiguration}
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
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Configuração das Zonas de Proteção</h2>
          <div className="text-sm text-gray-600">
            <span className="font-medium">Rede:</span> {zoneData.network_overview}
          </div>
        </div>
        
        {/* Status geral */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600">Status Geral</div>
            <div className={`text-lg font-bold ${
              zoneData.coordination_analysis.compliance_status.overall === 'compliant' 
                ? 'text-green-600' 
                : 'text-yellow-600'
            }`}>
              {zoneData.coordination_analysis.compliance_status.overall === 'compliant' 
                ? 'CONFORME' 
                : 'REQUER ATENÇÃO'}
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600">Questões Críticas</div>
            <div className={`text-lg font-bold ${
              zoneData.coordination_analysis.compliance_status.critical_issues === 0 
                ? 'text-green-600' 
                : 'text-red-600'
            }`}>
              {zoneData.coordination_analysis.compliance_status.critical_issues}
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600">Avisos</div>
            <div className={`text-lg font-bold ${
              zoneData.coordination_analysis.compliance_status.warnings <= 2 
                ? 'text-yellow-600' 
                : 'text-red-600'
            }`}>
              {zoneData.coordination_analysis.compliance_status.warnings}
            </div>
          </div>
        </div>
      </div>

      {/* Comparação das Zonas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Zona 1 Primária */}
        <div className="bg-white rounded-lg shadow">
          <div className="bg-red-500 text-white px-6 py-4 rounded-t-lg">
            <h3 className="text-xl font-bold flex items-center">
              <span className="w-3 h-3 bg-red-300 rounded-full mr-3"></span>
              Zona 1 - Primária
            </h3>
            <p className="text-red-100 text-sm mt-1">
              {zoneData.zone_configuration.zona_1_primaria.description}
            </p>
          </div>
          
          <div className="p-6">
            {/* Métricas da Zona 1 */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {zoneData.zone_configuration.zona_1_primaria.total_devices}
                </div>
                <div className="text-sm text-gray-600">Dispositivos</div>
              </div>
              <div className="text-center">
                <div className={`text-2xl font-bold ${getSelectivityColor(zoneData.zone_configuration.zona_1_primaria.selectivity_index)}`}>
                  {zoneData.zone_configuration.zona_1_primaria.selectivity_index}%
                </div>
                <div className="text-sm text-gray-600">Seletividade</div>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex justify-between">
                <span className="text-gray-600">Cobertura:</span>
                <span className="font-medium">{zoneData.zone_configuration.zona_1_primaria.coverage_area}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tempo de Operação:</span>
                <span className="font-medium text-green-600">{zoneData.zone_configuration.zona_1_primaria.operation_time}</span>
              </div>
            </div>

            {/* Dispositivos da Zona 1 */}
            <h4 className="font-bold text-gray-900 mb-3">Dispositivos Principais</h4>
            <div className="space-y-3">
              {zoneData.zone_configuration.zona_1_primaria.devices.slice(0, 2).map((device, index) => (
                <div key={index} className="border rounded-lg p-3 bg-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <div className="font-medium text-gray-900">{device.device_id}</div>
                    <div className="text-sm text-gray-600">{device.location}</div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
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
                  
                  {/* Conformidade */}
                  <div className="flex space-x-2 mt-2">
                    {Object.entries(device.standards_compliance).map(([standard, status]) => (
                      <span key={standard} className={`text-xs px-2 py-1 rounded-full ${getComplianceColor(status)}`}>
                        {standard.replace(/_/g, ' ')}: {status}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
              
              {zoneData.zone_configuration.zona_1_primaria.total_devices > 2 && (
                <div className="text-center text-sm text-gray-600 py-2">
                  + {zoneData.zone_configuration.zona_1_primaria.total_devices - 2} dispositivos adicionais
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Zona 2 Backup */}
        <div className="bg-white rounded-lg shadow">
          <div className="bg-blue-600 text-white px-6 py-4 rounded-t-lg">
            <h3 className="text-xl font-bold flex items-center">
              <span className="w-3 h-3 bg-blue-300 rounded-full mr-3"></span>
              Zona 2 - Backup
            </h3>
            <p className="text-blue-100 text-sm mt-1">
              {zoneData.zone_configuration.zona_2_backup.description}
            </p>
          </div>
          
          <div className="p-6">
            {/* Métricas da Zona 2 */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {zoneData.zone_configuration.zona_2_backup.total_devices}
                </div>
                <div className="text-sm text-gray-600">Dispositivos</div>
              </div>
              <div className="text-center">
                <div className={`text-2xl font-bold ${getSelectivityColor(zoneData.zone_configuration.zona_2_backup.selectivity_index)}`}>
                  {zoneData.zone_configuration.zona_2_backup.selectivity_index}%
                </div>
                <div className="text-sm text-gray-600">Seletividade</div>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex justify-between">
                <span className="text-gray-600">Cobertura:</span>
                <span className="font-medium">{zoneData.zone_configuration.zona_2_backup.coverage_area}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tempo de Operação:</span>
                <span className="font-medium text-blue-600">{zoneData.zone_configuration.zona_2_backup.operation_time}</span>
              </div>
            </div>

            {/* Dispositivos da Zona 2 */}
            <h4 className="font-bold text-gray-900 mb-3">Dispositivos Principais</h4>
            <div className="space-y-3">
              {zoneData.zone_configuration.zona_2_backup.devices.slice(0, 2).map((device, index) => (
                <div key={index} className="border rounded-lg p-3 bg-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <div className="font-medium text-gray-900">{device.device_id}</div>
                    <div className="text-sm text-gray-600">{device.location}</div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
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
                  
                  {/* Conformidade */}
                  <div className="flex space-x-2 mt-2">
                    {Object.entries(device.standards_compliance).map(([standard, status]) => (
                      <span key={standard} className={`text-xs px-2 py-1 rounded-full ${getComplianceColor(status)}`}>
                        {standard.replace(/_/g, ' ')}: {status}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
              
              {zoneData.zone_configuration.zona_2_backup.total_devices > 2 && (
                <div className="text-center text-sm text-gray-600 py-2">
                  + {zoneData.zone_configuration.zona_2_backup.total_devices - 2} dispositivos adicionais
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Análise de Coordenação */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Análise de Coordenação</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Configurações Iniciais */}
          <div>
            <h4 className="font-bold text-gray-900 mb-3">Configurações Iniciais</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Método:</span>
                <span className="font-medium">{zoneData.coordination_analysis.initial_settings.coordination_method}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Margem Segurança:</span>
                <span className="font-medium">{zoneData.coordination_analysis.initial_settings.safety_margin}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Coordenação Pickup:</span>
                <span className="font-medium">{zoneData.coordination_analysis.initial_settings.pickup_coordination}</span>
              </div>
            </div>
            
            <div className="mt-4">
              <h5 className="font-medium text-gray-900 mb-2">Normas de Referência:</h5>
              <ul className="text-sm text-gray-600 space-y-1">
                {zoneData.coordination_analysis.initial_settings.standards_reference.map((standard, index) => (
                  <li key={index} className="flex items-center">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                    {standard}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Critérios de Validação */}
          <div>
            <h4 className="font-bold text-gray-900 mb-3">Critérios de Validação</h4>
            <div className="space-y-3">
              {Object.entries(zoneData.coordination_analysis.validation_criteria).map(([key, value]) => (
                <div key={key} className="bg-gray-50 rounded-lg p-3">
                  <div className="font-medium text-gray-900 mb-1 capitalize">
                    {key.replace('_', ' ')}:
                  </div>
                  <div className="text-sm text-gray-600">{value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recomendações */}
        {zoneData.coordination_analysis.compliance_status.recommendations.length > 0 && (
          <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
            <h4 className="font-bold text-yellow-800 mb-3 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              Recomendações
            </h4>
            <ul className="space-y-2">
              {zoneData.coordination_analysis.compliance_status.recommendations.map((rec, index) => (
                <li key={index} className="text-sm text-yellow-700 flex items-start">
                  <span className="w-2 h-2 bg-yellow-500 rounded-full mr-3 mt-2 flex-shrink-0"></span>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Próxima Revisão */}
        <div className="mt-6 flex justify-between items-center p-4 bg-blue-50 rounded-lg">
          <div>
            <div className="text-sm text-blue-600">Última Validação:</div>
            <div className="font-medium text-blue-800">
              {new Date(zoneData.last_validation).toLocaleDateString('pt-BR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-blue-600">Próxima Revisão:</div>
            <div className="font-medium text-blue-800">
              {new Date(zoneData.next_review_due).toLocaleDateString('pt-BR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
