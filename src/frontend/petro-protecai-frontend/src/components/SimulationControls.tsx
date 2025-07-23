import { useState, useEffect } from 'react'

// Interfaces para simulação
interface FaultSimulationRequest {
  location: {
    line: string
    position_km: number
    position_percent: number
  }
  type: 'phase_to_ground' | 'three_phase' | 'phase_to_phase' | 'double_phase_ground'
  magnitude: number
}

interface DeviceOperation {
  device: string
  operation_time: number
  pickup_current: number
  settings_used: {
    pickup: string
    time_dial: number
  }
  operation_reason: string
  successful: boolean
}

interface BackupDevice {
  device: string
  armed_time: number
  pickup_current: number
  operated: boolean
  reason_not_operated?: string
}

interface CoordinationRestoration {
  pre_fault_settings: Record<string, any>
  rl_adjustments: Array<{
    device: string
    parameter: string
    old_value: string | number
    new_value: string | number
    reason: string
    confidence: number
  }>
  coordination_validation: {
    selectivity_maintained: boolean
    speed_improved: boolean
    margin_adequate: boolean
    standards_compliance: string
  }
}

interface FaultSimulationResult {
  simulation_id: string
  fault_simulation: {
    fault_details: any
    devices_operation: {
      primary_operation: DeviceOperation[]
      backup_devices: BackupDevice[]
      adjacent_zones: any[]
    }
    coordination_restoration: CoordinationRestoration
  }
  standards_validation: Record<string, any>
  overall_assessment: string
  timestamp: string
}

interface RLAnalysis {
  analysis_summary: string
  rl_analysis: {
    algorithm_details: {
      type: string
      convergence_episode: number
      training_episodes: number
    }
    convergence_analysis: {
      convergence_speed: string
      warning_flags: string[]
    }
    performance_metrics: {
      training_accuracy: number
      validation_accuracy: number
      test_accuracy: number
    }
    recommendations: string[]
  }
}

export function SimulationControls() {
  const [faultRequest, setFaultRequest] = useState<FaultSimulationRequest>({
    location: {
      line: 'line_2_5',
      position_km: 3.2,
      position_percent: 65.4
    },
    type: 'phase_to_ground',
    magnitude: 2.5
  })
  
  const [simulationResult, setSimulationResult] = useState<FaultSimulationResult | null>(null)
  const [rlAnalysis, setRlAnalysis] = useState<RLAnalysis | null>(null)
  const [isSimulating, setIsSimulating] = useState(false)
  const [isAnalyzingRL, setIsAnalyzingRL] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'simulation' | 'rl-analysis' | 'standards'>('simulation')

  const availableLines = [
    'line_1_2', 'line_1_5', 'line_2_3', 'line_2_4', 'line_2_5',
    'line_3_4', 'line_4_5', 'line_4_7', 'line_4_9', 'line_5_6'
  ]

  const faultTypes = [
    { value: 'phase_to_ground', label: 'Fase-Terra (Monofásica)' },
    { value: 'three_phase', label: 'Trifásica' },
    { value: 'phase_to_phase', label: 'Fase-Fase (Bifásica)' },
    { value: 'double_phase_ground', label: 'Bifásica-Terra' }
  ]

  useEffect(() => {
    fetchRLAnalysis()
  }, [])

  const runFaultSimulation = async () => {
    setIsSimulating(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/protection-zones/fault-simulation/detailed-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(faultRequest)
      })

      if (!response.ok) {
        throw new Error(`Erro na simulação: ${response.status}`)
      }

      const data = await response.json()
      setSimulationResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
      console.error('Erro na simulação:', err)
    } finally {
      setIsSimulating(false)
    }
  }

  const fetchRLAnalysis = async () => {
    setIsAnalyzingRL(true)
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/protection-zones/rl-algorithm/detailed-analysis')
      
      if (!response.ok) {
        throw new Error(`Erro na análise RL: ${response.status}`)
      }

      const data = await response.json()
      setRlAnalysis(data)
    } catch (err) {
      console.error('Erro na análise RL:', err)
    } finally {
      setIsAnalyzingRL(false)
    }
  }

  const getDeviceStatusColor = (successful: boolean) => {
    return successful ? 'text-green-600' : 'text-red-600'
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600'
    if (confidence >= 0.7) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Controles de Simulação</h2>
        
        {/* Abas */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('simulation')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'simulation'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Simulação de Falta
            </button>
            <button
              onClick={() => setActiveTab('rl-analysis')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'rl-analysis'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Análise RL
            </button>
            <button
              onClick={() => setActiveTab('standards')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'standards'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Conformidade
            </button>
          </nav>
        </div>
      </div>

      {/* Aba de Simulação de Falta */}
      {activeTab === 'simulation' && (
        <div className="space-y-6">
          {/* Configuração da Simulação */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Configuração da Falta</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Localização */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Linha
                </label>
                <select
                  value={faultRequest.location.line}
                  onChange={(e) => setFaultRequest({
                    ...faultRequest,
                    location: { ...faultRequest.location, line: e.target.value }
                  })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {availableLines.map(line => (
                    <option key={line} value={line}>
                      {line.replace('_', '-').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              {/* Posição */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Posição (%)
                </label>
                <input
                  type="range"
                  min="10"
                  max="90"
                  step="5"
                  value={faultRequest.location.position_percent}
                  onChange={(e) => {
                    const percent = parseFloat(e.target.value)
                    setFaultRequest({
                      ...faultRequest,
                      location: {
                        ...faultRequest.location,
                        position_percent: percent,
                        position_km: percent * 0.05 // Aproximação
                      }
                    })
                  }}
                  className="w-full"
                />
                <div className="text-sm text-gray-600 mt-1">
                  {faultRequest.location.position_percent}% ({faultRequest.location.position_km.toFixed(1)} km)
                </div>
              </div>

              {/* Tipo de Falta */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Falta
                </label>
                <select
                  value={faultRequest.type}
                  onChange={(e) => setFaultRequest({
                    ...faultRequest,
                    type: e.target.value as any
                  })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {faultTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Magnitude */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Magnitude (pu)
                </label>
                <input
                  type="range"
                  min="1.0"
                  max="5.0"
                  step="0.1"
                  value={faultRequest.magnitude}
                  onChange={(e) => setFaultRequest({
                    ...faultRequest,
                    magnitude: parseFloat(e.target.value)
                  })}
                  className="w-full"
                />
                <div className="text-sm text-gray-600 mt-1">
                  {faultRequest.magnitude} pu ({(faultRequest.magnitude * 1200).toFixed(0)} A)
                </div>
              </div>
            </div>

            {/* Botão de Simulação */}
            <div className="mt-6">
              <button
                onClick={runFaultSimulation}
                disabled={isSimulating}
                className={`px-6 py-3 rounded-md font-medium transition ${
                  isSimulating
                    ? 'bg-gray-400 text-gray-300 cursor-not-allowed'
                    : 'bg-red-600 text-white hover:bg-red-700'
                }`}
              >
                {isSimulating ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                    Simulando...
                  </div>
                ) : (
                  '⚡ Executar Simulação de Falta'
                )}
              </button>
            </div>

            {/* Erro */}
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <div className="text-red-800">{error}</div>
              </div>
            )}
          </div>

          {/* Resultados da Simulação */}
          {simulationResult && (
            <div className="space-y-6">
              {/* Resumo */}
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-gray-900">Resultado da Simulação</h3>
                  <div className={`px-4 py-2 rounded-lg font-medium ${
                    simulationResult.overall_assessment.includes('COORDENAÇÃO MANTIDA')
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {simulationResult.overall_assessment}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-lg font-bold text-blue-600">
                      {simulationResult.fault_simulation.devices_operation.primary_operation.length}
                    </div>
                    <div className="text-sm text-gray-600">Dispositivos Primários Atuaram</div>
                  </div>
                  
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <div className="text-lg font-bold text-yellow-600">
                      {simulationResult.fault_simulation.devices_operation.backup_devices.length}
                    </div>
                    <div className="text-sm text-gray-600">Dispositivos Backup Preparados</div>
                  </div>
                  
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-lg font-bold text-green-600">
                      {simulationResult.fault_simulation.coordination_restoration.rl_adjustments.length}
                    </div>
                    <div className="text-sm text-gray-600">Ajustes RL Realizados</div>
                  </div>
                </div>
              </div>

              {/* Operação dos Dispositivos */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Operação dos Dispositivos</h3>
                
                {/* Dispositivos Primários */}
                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-3">Proteção Primária</h4>
                  <div className="space-y-3">
                    {simulationResult.fault_simulation.devices_operation.primary_operation.map((device, index) => (
                      <div key={index} className="border rounded-lg p-4 bg-green-50">
                        <div className="flex items-center justify-between mb-2">
                          <div className="font-medium text-gray-900">{device.device}</div>
                          <div className={`font-medium ${getDeviceStatusColor(device.successful)}`}>
                            {device.successful ? '✅ OPEROU' : '❌ FALHOU'}
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Tempo:</span>
                            <span className="font-medium ml-1">{(device.operation_time * 1000).toFixed(0)}ms</span>
                          </div>
                          <div>
                            <span className="text-gray-600">Corrente:</span>
                            <span className="font-medium ml-1">{device.pickup_current}A</span>
                          </div>
                          <div>
                            <span className="text-gray-600">Pickup:</span>
                            <span className="font-medium ml-1">{device.settings_used.pickup}</span>
                          </div>
                        </div>
                        
                        <div className="mt-2 text-sm text-gray-600">
                          <strong>Razão:</strong> {device.operation_reason}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Dispositivos Backup */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Proteção Backup</h4>
                  <div className="space-y-3">
                    {simulationResult.fault_simulation.devices_operation.backup_devices.map((device, index) => (
                      <div key={index} className="border rounded-lg p-4 bg-yellow-50">
                        <div className="flex items-center justify-between mb-2">
                          <div className="font-medium text-gray-900">{device.device}</div>
                          <div className={`font-medium ${device.operated ? 'text-red-600' : 'text-green-600'}`}>
                            {device.operated ? '🔴 OPEROU' : '✅ NÃO OPEROU'}
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Tempo Armado:</span>
                            <span className="font-medium ml-1">{(device.armed_time * 1000).toFixed(0)}ms</span>
                          </div>
                          <div>
                            <span className="text-gray-600">Corrente Vista:</span>
                            <span className="font-medium ml-1">{device.pickup_current}A</span>
                          </div>
                        </div>
                        
                        {device.reason_not_operated && (
                          <div className="mt-2 text-sm text-gray-600">
                            <strong>Razão:</strong> {device.reason_not_operated}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Ajustes RL */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Ajustes do Sistema RL</h3>
                
                <div className="space-y-4">
                  {simulationResult.fault_simulation.coordination_restoration.rl_adjustments.map((adjustment, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="font-medium text-gray-900">{adjustment.device}</div>
                        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(adjustment.confidence)}`}>
                          Confiança: {(adjustment.confidence * 100).toFixed(0)}%
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Parâmetro:</span>
                          <span className="font-medium ml-1 capitalize">{adjustment.parameter.replace('_', ' ')}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">De:</span>
                          <span className="font-medium ml-1">{adjustment.old_value}</span>
                          <span className="mx-2">→</span>
                          <span className="text-gray-600">Para:</span>
                          <span className="font-medium ml-1 text-blue-600">{adjustment.new_value}</span>
                        </div>
                        <div className="md:col-span-1">
                          <span className="text-gray-600">Razão:</span>
                          <span className="font-medium ml-1">{adjustment.reason}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Validação da Coordenação */}
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-3">Validação da Coordenação</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(simulationResult.fault_simulation.coordination_restoration.coordination_validation).map(([key, value]) => (
                      <div key={key} className="text-center">
                        <div className={`text-2xl ${value ? 'text-green-600' : 'text-red-600'}`}>
                          {value ? '✅' : '❌'}
                        </div>
                        <div className="text-sm text-gray-700 capitalize">
                          {key.replace(/_/g, ' ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Aba de Análise RL */}
      {activeTab === 'rl-analysis' && (
        <div className="space-y-6">
          {isAnalyzingRL ? (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-center items-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Analisando algoritmo RL...</span>
              </div>
            </div>
          ) : rlAnalysis ? (
            <div className="space-y-6">
              {/* Resumo da Análise */}
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-gray-900">Análise do Algoritmo RL</h3>
                  <div className="bg-yellow-100 text-yellow-800 px-4 py-2 rounded-lg font-medium">
                    {rlAnalysis.analysis_summary}
                  </div>
                </div>

                {/* Detalhes do Algoritmo */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {rlAnalysis.rl_analysis.algorithm_details.type}
                    </div>
                    <div className="text-sm text-gray-600">Tipo de Algoritmo</div>
                  </div>
                  
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">
                      {rlAnalysis.rl_analysis.algorithm_details.convergence_episode}
                    </div>
                    <div className="text-sm text-gray-600">Episódio de Convergência</div>
                  </div>
                  
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {rlAnalysis.rl_analysis.performance_metrics.training_accuracy.toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Acurácia de Treinamento</div>
                  </div>
                </div>

                {/* Análise de Convergência */}
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-3">Análise de Convergência</h4>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="font-medium text-yellow-800 mb-2">
                      ⚠️ {rlAnalysis.rl_analysis.convergence_analysis.convergence_speed}
                    </div>
                    <ul className="space-y-1">
                      {rlAnalysis.rl_analysis.convergence_analysis.warning_flags.map((flag, index) => (
                        <li key={index} className="text-sm text-yellow-700 flex items-start">
                          <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2 mt-2 flex-shrink-0"></span>
                          {flag}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Métricas de Performance */}
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-3">Métricas de Performance</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-lg font-bold text-gray-900">
                        {rlAnalysis.rl_analysis.performance_metrics.training_accuracy.toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Treinamento</div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-lg font-bold text-gray-900">
                        {rlAnalysis.rl_analysis.performance_metrics.validation_accuracy.toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Validação</div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-lg font-bold text-gray-900">
                        {rlAnalysis.rl_analysis.performance_metrics.test_accuracy.toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Teste</div>
                    </div>
                  </div>
                </div>

                {/* Recomendações */}
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-3">Recomendações</h4>
                  <div className="space-y-2">
                    {rlAnalysis.rl_analysis.recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start p-3 bg-blue-50 rounded-lg">
                        <span className="text-blue-600 mr-3">{rec.split(' ')[0]}</span>
                        <span className="text-blue-800">{rec.substring(rec.indexOf(' ') + 1)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <p className="text-gray-600">Nenhuma análise RL disponível</p>
              <button
                onClick={fetchRLAnalysis}
                className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                Carregar Análise
              </button>
            </div>
          )}
        </div>
      )}

      {/* Aba de Conformidade */}
      {activeTab === 'standards' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Conformidade com Normas</h3>
          
          {simulationResult && (
            <div className="space-y-4">
              {Object.entries(simulationResult.standards_validation).map(([standard, validation]) => (
                <div key={standard} className="border rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">{standard.replace(/_/g, ' ')}</h4>
                  <div className="text-sm text-gray-600">
                    {typeof validation === 'object' && validation !== null ? (
                      <div className="space-y-1">
                        {Object.entries(validation as Record<string, any>).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span>{key.replace(/_/g, ' ')}:</span>
                            <span className={`font-medium ${
                              typeof value === 'string' && value.includes('PASS') 
                                ? 'text-green-600' 
                                : 'text-gray-900'
                            }`}>
                              {value}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span>{validation}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {!simulationResult && (
            <div className="text-center text-gray-600">
              Execute uma simulação para ver a conformidade com normas
            </div>
          )}
        </div>
      )}
    </div>
  )
}
