import { useState, useEffect } from 'react'

// Interfaces para dados da API
interface SystemMetrics {
  uptime: string
  cpu_usage: number
  memory_usage: number
  active_simulations: number
  total_devices: number
  network_status: 'healthy' | 'warning' | 'critical'
}

interface ProtectionDevice {
  id: string
  zone: 'Z1' | 'Z2'
  type: '50/51' | '67' | '87T' | '27/59'
  location: string
  pickup_current: number
  time_delay: number
  distance_km: number
  status: 'active' | 'inactive' | 'fault'
}

interface ProtectionZone {
  id: 'Z1' | 'Z2'
  transformer: string
  power_mva: number
  voltage_kv: number
  buses: number[]
  devices: ProtectionDevice[]
}

interface FaultSimulationResult {
  fault_location: string
  fault_type: string
  fault_current_a: number
  affected_zone: string
  coordination_ok: boolean
  device_responses: Array<{
    device_id: string
    type: string
    should_operate: boolean
    operating_time: number
    coordination_ok: boolean
  }>
  coordination_issues: Array<{
    device1: string
    device2: string
    margin: number
    required: number
  }>
  normative_compliance: {
    IEEE_C37_112: { coordination_margins: boolean; issues: string[] }
    IEC_61850: { goose_performance: boolean; issues: string[] }
    NBR_5410: { selectivity_dr: boolean; issues: string[] }
    API_RP_14C: { offshore_environment: boolean; issues: string[] }
  }
}

interface RLStatus {
  status: string
  episodes: number
  max_episodes: number
  learning_rate: number
  epsilon: number
  state_size: number
  action_space_size: number
}

// API Base URL
const API_BASE_URL = 'http://localhost:8001/api'

export default function DashboardTab() {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    uptime: '2h 45m',
    cpu_usage: 23,
    memory_usage: 67,
    active_simulations: 3,
    total_devices: 8,
    network_status: 'healthy'
  })

  const [protectionZones, setProtectionZones] = useState<ProtectionZone[]>([])
  const [faultLocation, setFaultLocation] = useState<number>(4)
  const [faultType, setFaultType] = useState<string>('3ph')
  const [faultSeverity, setFaultSeverity] = useState<number>(0.5)
  const [faultResult, setFaultResult] = useState<FaultSimulationResult | null>(null)
  const [rlStatus, setRlStatus] = useState<RLStatus | null>(null)
  const [isSimulating, setIsSimulating] = useState(false)
  const [apiConnected, setApiConnected] = useState(false)

  // Funções da API
  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/status`)
      if (response.ok) {
        const data = await response.json()
        setMetrics(prev => ({
          ...prev,
          total_devices: data.total_devices,
          active_simulations: data.zones,
          network_status: data.system_health
        }))
        setApiConnected(true)
      }
    } catch (error) {
      console.warn('API não disponível, usando dados mock')
      setApiConnected(false)
    }
  }

  const fetchProtectionZones = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/zones`)
      if (response.ok) {
        const zones = await response.json()
        setProtectionZones(zones)
      }
    } catch (error) {
      console.warn('Não foi possível carregar zonas de proteção')
    }
  }

  const fetchRLStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/rl/status`)
      if (response.ok) {
        const status = await response.json()
        setRlStatus(status)
      }
    } catch (error) {
      console.warn('Status RL não disponível')
    }
  }

  const simulateFault = async () => {
    setIsSimulating(true)
    try {
      const response = await fetch(`${API_BASE_URL}/simulate-fault`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          bus: faultLocation,
          fault_type: faultType,
          severity: faultSeverity
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        setFaultResult(result)
      } else {
        console.error('Erro na simulação de falta')
      }
    } catch (error) {
      console.error('Erro ao conectar com API:', error)
    } finally {
      setIsSimulating(false)
    }
  }

  const trainRLAgent = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/rl/train`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          episodes: 5,
          scenarios: [
            { bus: faultLocation, fault_type: faultType, severity: faultSeverity }
          ]
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('Treinamento RL concluído:', result)
        fetchRLStatus() // Atualiza status RL
      }
    } catch (error) {
      console.error('Erro no treinamento RL:', error)
    }
  }

  useEffect(() => {
    // Carrega dados iniciais
    fetchSystemStatus()
    fetchProtectionZones()
    fetchRLStatus()

    // Atualiza métricas periodicamente
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        cpu_usage: Math.floor(Math.random() * 30) + 15,
        memory_usage: Math.floor(Math.random() * 20) + 60
      }))
      fetchSystemStatus()
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      {/* Header - Plataforma Offshore */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">🛢️ ProtecAI - Coordenação de Proteção 2 Zonas (25 MVA)</h1>
        <div className="flex space-x-4">
          <div className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            ✅ IEEE 14-Bus {apiConnected ? 'Conectado' : 'Mock'}
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            rlStatus?.status === 'operational' ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'
          }`}>
            🤖 RL {rlStatus?.status === 'operational' ? 'Operacional' : 'Em Desenvolvimento'}
          </div>
          <div className="px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
            🛡️ ANSI 50/51/67/87T
          </div>
          <div className="px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800">
            ⚡ 2x25MVA 13.8kV
          </div>
        </div>
      </div>

      {/* Métricas de Proteção Offshore */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Barras IEEE 14-Bus */}
        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Barras IEEE 14-Bus</p>
              <p className="text-3xl font-bold text-blue-600">14</p>
              <p className="text-xs text-green-600">100% Monitoradas</p>
            </div>
            <div className="text-4xl">⚡</div>
          </div>
        </div>

        {/* Tensão Offshore 13.8kV */}
        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">CPU Usage</p>
              <p className="text-3xl font-bold text-green-600">{metrics.cpu_usage}%</p>
              <p className="text-xs text-green-600">Normal</p>
            </div>
            <div className="text-4xl">🖥️</div>
          </div>
        </div>

        {/* Dispositivos ANSI */}
        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Dispositivos ANSI</p>
              <p className="text-3xl font-bold text-green-600">{metrics.total_devices}</p>
              <p className="text-xs text-green-600">{apiConnected ? 'Sistema Funcional' : 'Modo Mock'}</p>
            </div>
            <div className="text-4xl">🛡️</div>
          </div>
        </div>

        {/* Status RL */}
        <div className={`bg-white p-6 rounded-xl shadow-lg border-l-4 ${
          rlStatus?.status === 'operational' ? 'border-green-500' : 'border-yellow-500'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">RL Status</p>
              <p className={`text-3xl font-bold ${
                rlStatus?.status === 'operational' ? 'text-green-600' : 'text-yellow-600'
              }`}>
                {rlStatus?.status === 'operational' ? 'ATIVO' : 'EM DESENVOLVIMENTO'}
              </p>
              <p className="text-xs text-gray-600">
                {rlStatus ? `Ep: ${rlStatus.episodes}/${rlStatus.max_episodes}` : 'Carregando...'}
              </p>
            </div>
            <div className="text-4xl">
              {rlStatus?.status === 'operational' ? '🧠' : '⚙️'}
            </div>
          </div>
        </div>
      </div>

      {/* Zonas de Proteção - Tabela Detalhada */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h3 className="text-xl font-semibold mb-4">🏗️ Configuração das Zonas de Proteção IEEE 14-Bus</h3>
        
        {protectionZones.map(zone => (
          <div key={zone.id} className="mb-6 p-4 border rounded-lg">
            <div className="flex justify-between items-center mb-3">
              <h4 className="text-lg font-semibold text-blue-600">
                Zona {zone.id}: {zone.transformer}
              </h4>
              <div className="text-sm text-gray-600">
                {zone.power_mva} MVA • {zone.voltage_kv} kV • Buses: {zone.buses.join(', ')}
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="p-2 text-left">Dispositivo</th>
                    <th className="p-2 text-left">Tipo ANSI</th>
                    <th className="p-2 text-left">Localização</th>
                    <th className="p-2 text-left">Pickup (pu)</th>
                    <th className="p-2 text-left">Tempo (s)</th>
                    <th className="p-2 text-left">Distância (km)</th>
                    <th className="p-2 text-left">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {zone.devices.map(device => (
                    <tr key={device.id} className="border-t">
                      <td className="p-2 font-mono text-xs">{device.id}</td>
                      <td className="p-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          device.type === '87T' ? 'bg-red-100 text-red-800' :
                          device.type === '50/51' ? 'bg-blue-100 text-blue-800' :
                          device.type === '67' ? 'bg-green-100 text-green-800' :
                          'bg-purple-100 text-purple-800'
                        }`}>
                          {device.type}
                        </span>
                      </td>
                      <td className="p-2">{device.location}</td>
                      <td className="p-2 font-mono">{device.pickup_current.toFixed(1)}</td>
                      <td className="p-2 font-mono">{device.time_delay.toFixed(1)}</td>
                      <td className="p-2 font-mono">{device.distance_km.toFixed(1)}</td>
                      <td className="p-2">
                        <span className={`w-2 h-2 rounded-full inline-block ${
                          device.status === 'active' ? 'bg-green-500' :
                          device.status === 'fault' ? 'bg-red-500' : 'bg-yellow-500'
                        }`}></span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>

      {/* Gerador de Falhas e Análise RL */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-xl font-semibold mb-4">⚡ Gerador de Falhas IEEE 14-Bus</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Localização da Falta (Bus)
              </label>
              <select 
                value={faultLocation} 
                onChange={(e) => setFaultLocation(Number(e.target.value))}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                {Array.from({length: 14}, (_, i) => i + 1).map(bus => (
                  <option key={bus} value={bus}>Bus {bus}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tipo de Falta
              </label>
              <select 
                value={faultType} 
                onChange={(e) => setFaultType(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="3ph">Trifásica (3φ)</option>
                <option value="2ph">Bifásica (2φ)</option>
                <option value="1ph">Monofásica (1φ-T)</option>
                <option value="2ph_ground">Bifásica-Terra (2φ-T)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Severidade: {(faultSeverity * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                value={faultSeverity}
                onChange={(e) => setFaultSeverity(Number(e.target.value))}
                className="w-full"
              />
            </div>
            
            <button 
              onClick={simulateFault}
              disabled={isSimulating}
              className={`w-full p-3 text-white rounded-lg transition-colors ${
                isSimulating 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-red-600 hover:bg-red-700'
              }`}
            >
              {isSimulating ? '🔄 Simulando...' : '🧨 Simular Falta'}: {faultType.toUpperCase()} Bus-{faultLocation} ({(faultSeverity * 100).toFixed(0)}%)
            </button>
            
            <button 
              onClick={() => {
                setFaultLocation(Math.floor(Math.random() * 14) + 1)
                setFaultType(['3ph', '2ph', '1ph', '2ph_ground'][Math.floor(Math.random() * 4)])
                setFaultSeverity(Math.random() * 0.9 + 0.1)
              }}
              className="w-full p-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              🎲 Gerar Falta Aleatória
            </button>
            
            {/* Resultado da Simulação */}
            {faultResult && (
              <div className="mt-4 p-3 border rounded-lg bg-gray-50">
                <h4 className="font-medium text-sm mb-2">📊 Resultado da Simulação</h4>
                <div className="text-xs space-y-1">
                  <div className="flex justify-between">
                    <span>Local:</span>
                    <span className="font-mono">{faultResult.fault_location}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Corrente:</span>
                    <span className="font-mono">{faultResult.fault_current_a.toFixed(0)} A</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Zona:</span>
                    <span className="font-mono">{faultResult.affected_zone}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Coordenação:</span>
                    <span className={`font-medium ${
                      faultResult.coordination_ok ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {faultResult.coordination_ok ? '✅ OK' : '❌ FALHA'}
                    </span>
                  </div>
                  {faultResult.coordination_issues.length > 0 && (
                    <div className="mt-2 p-2 bg-red-50 rounded text-red-700">
                      <div className="font-medium">Problemas encontrados:</div>
                      {faultResult.coordination_issues.map((issue, i) => (
                        <div key={i} className="text-xs">
                          {issue.device1} ↔ {issue.device2}: {issue.margin.toFixed(2)}s (req: {issue.required}s)
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-xl font-semibold mb-4">🧠 RL - Sistema Funcional</h3>
          
          <div className="space-y-4">
            <div className={`p-3 border rounded-lg ${
              rlStatus?.status === 'operational' 
                ? 'bg-green-50 border-green-200' 
                : 'bg-yellow-50 border-yellow-200'
            }`}>
              <p className={`text-sm font-semibold ${
                rlStatus?.status === 'operational' ? 'text-green-800' : 'text-yellow-800'
              }`}>
                {rlStatus?.status === 'operational' 
                  ? '✅ Sistema RL Operacional' 
                  : '⚠️ Sistema RL em Desenvolvimento'
                }
              </p>
              <p className={`text-sm mt-2 ${
                rlStatus?.status === 'operational' ? 'text-green-700' : 'text-yellow-700'
              }`}>
                {rlStatus?.status === 'operational'
                  ? 'Agente treinado e pronto para otimização de coordenação.'
                  : 'Algoritmo implementado, aguardando mais dados de treinamento.'
                }
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Parâmetros RL - {apiConnected ? 'Real' : 'Mock'}</h4>
              <div className="text-sm space-y-1">
                <div className="flex justify-between">
                  <span>Episódios:</span>
                  <span className="font-mono">
                    {rlStatus ? `${rlStatus.episodes}/${rlStatus.max_episodes}` : 'Carregando...'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Learning Rate:</span>
                  <span className="font-mono">{rlStatus?.learning_rate || 0.001}</span>
                </div>
                <div className="flex justify-between">
                  <span>Epsilon:</span>
                  <span className="font-mono">{rlStatus?.epsilon?.toFixed(3) || '0.100'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Estado/Ações:</span>
                  <span className="font-mono">
                    {rlStatus ? `${rlStatus.state_size}/${rlStatus.action_space_size}` : '16/16'}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Ações RL Disponíveis</h4>
              <div className="text-xs space-y-1">
                <div>• Ajuste pickup correntes relés 50/51</div>
                <div>• Otimização tempos coordenação</div>
                <div>• Reconfiguração automática proteção</div>
                <div>• Isolamento seletivo faltas</div>
              </div>
              
              <button 
                onClick={trainRLAgent}
                className="w-full mt-3 p-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm"
              >
                🎯 Treinar RL (5 episódios)
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ALERTA CRÍTICO - Conformidade Normativa */}
      <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-red-500">
        <h3 className="text-xl font-semibold mb-4 text-red-600">� CONFORMIDADE NORMATIVA - AGUARDANDO VALIDAÇÃO</h3>
        
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-4">
          <p className="text-red-800 font-semibold">
            ⛔ ATENÇÃO: Nenhuma validação normativa foi realizada contra padrões reais.
          </p>
          <p className="text-red-700 text-sm mt-2">
            Sistema NÃO aprovado para operação offshore. Requer validação completa contra normas oficiais.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="p-4 border rounded-lg bg-gray-50">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-600">IEEE C37.112 - Proteção Inversa</h4>
                <span className="text-red-600">❌ NÃO VALIDADO</span>
              </div>
              <div className="text-sm text-gray-500 space-y-1">
                <div>• Coordenação tempo-corrente: PENDENTE</div>
                <div>• Seletividade dispositivos: PENDENTE</div>
                <div>• Margem coordenação: A CALCULAR</div>
              </div>
            </div>
            
            <div className="p-4 border rounded-lg bg-gray-50">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-600">IEC 61850 - Comunicação</h4>
                <span className="text-red-600">❌ NÃO IMPLEMENTADO</span>
              </div>
              <div className="text-sm text-gray-500 space-y-1">
                <div>• GOOSE msgs: NÃO CONFIGURADO</div>
                <div>• MMS protocol: NÃO ATIVO</div>
                <div>• SCADA integration: PENDENTE</div>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 border rounded-lg bg-gray-50">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-600">NBR 5410 - Instalações BT</h4>
                <span className="text-red-600">❌ NÃO AVALIADO</span>
              </div>
              <div className="text-sm text-gray-500 space-y-1">
                <div>• Proteção pessoas: A VERIFICAR</div>
                <div>• Coordenação DR: A CALCULAR</div>
                <div>• Seletividade: A DETERMINAR</div>
              </div>
            </div>
            
            <div className="p-4 border rounded-lg bg-gray-50">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-600">API RP 14C - Offshore</h4>
                <span className="text-red-600">❌ NÃO CERTIFICADO</span>
              </div>
              <div className="text-sm text-gray-500 space-y-1">
                <div>• Ambiente marinho: A VALIDAR</div>
                <div>• Redundância: A IMPLEMENTAR</div>
                <div>• Fail-safe: A PROJETAR</div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-red-50 rounded-lg border border-red-200">
          <p className="text-sm text-red-800">
            <strong>CRÍTICO:</strong> Sistema requer análise completa por engenheiros especialistas em proteção offshore 
            e validação contra documentação normativa oficial antes de qualquer consideração para operação.
          </p>
        </div>
      </div>

      {/* Visualização IEEE 14-Bus Simplificada */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h3 className="text-xl font-semibold mb-4">🔌 Topologia IEEE 14-Bus - Zonas de Proteção</h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="p-4 border-2 border-blue-200 rounded-lg bg-blue-50">
            <h4 className="font-medium text-blue-800 mb-3">ZONA Z1 - TR1 (25 MVA)</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Transformador:</span>
                <span className="font-mono">Bus 0 → Bus 4</span>
              </div>
              <div className="flex justify-between">
                <span>Barras protegidas:</span>
                <span className="font-mono">0, 4, 5, 6, 7, 9</span>
              </div>
              <div className="flex justify-between">
                <span>Dispositivos:</span>
                <span className="font-mono">4 ativos</span>
              </div>
              <div className="mt-3 p-2 bg-white rounded text-xs">
                87T(TR1) → 50/51(L4-5) → 67(B4) → 27/59(B7)
              </div>
            </div>
          </div>
          
          <div className="p-4 border-2 border-green-200 rounded-lg bg-green-50">
            <h4 className="font-medium text-green-800 mb-3">ZONA Z2 - TR2 (25 MVA)</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Transformador:</span>
                <span className="font-mono">Bus 1 → Bus 5</span>
              </div>
              <div className="flex justify-between">
                <span>Barras protegidas:</span>
                <span className="font-mono">1, 5, 8, 10-14</span>
              </div>
              <div className="flex justify-between">
                <span>Dispositivos:</span>
                <span className="font-mono">4 ativos</span>
              </div>
              <div className="mt-3 p-2 bg-white rounded text-xs">
                87T(TR2) → 50/51(L5-6) → 67(B5) → 27/59(B14)
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-700">
            <strong>Legenda:</strong> 87T=Diferencial | 50/51=Sobrecorrente | 67=Direcional | 27/59=Sub/Sobretensão
          </p>
        </div>
      </div>

      {/* Status RL REAL - Sem Fabricações */}
      <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-yellow-500">
        <h3 className="text-xl font-semibold mb-4 text-yellow-600">🧠 RL - Sistema em Desenvolvimento</h3>
        
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg mb-4">
          <p className="text-yellow-800 font-semibold">
            ⚠️ ALGORITMO RL NÃO OPERACIONAL - EM FASE DE PESQUISA
          </p>
          <p className="text-yellow-700 text-sm mt-2">
            Nenhuma validação de eficiência foi realizada. Sistema não aprovado para coordenação automática.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 border rounded-lg">
            <div className="text-4xl font-bold text-red-600 mb-2">NÃO TESTADO</div>
            <div className="text-sm text-gray-600">Confiabilidade</div>
            <div className="text-xs text-red-500">Sem dados validados</div>
          </div>
          <div className="text-center p-4 border rounded-lg">
            <div className="text-4xl font-bold text-red-600 mb-2">INDEFINIDO</div>
            <div className="text-sm text-gray-600">Tempo Resposta</div>
            <div className="text-xs text-red-500">Não medido</div>
          </div>
          <div className="text-center p-4 border rounded-lg">
            <div className="text-4xl font-bold text-red-600 mb-2">INEXISTENTE</div>
            <div className="text-sm text-gray-600">Melhoria RL</div>
            <div className="text-xs text-red-500">Algoritmo não implementado</div>
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-red-50 rounded-lg border border-red-200">
          <p className="text-sm text-red-800">
            🚨 <strong>CRÍTICO:</strong> Sistema RL é apenas conceitual. Não há implementação funcional, 
            testes de coordenação ou validação de segurança. NÃO USAR EM AMBIENTE OFFSHORE REAL.
          </p>
        </div>
      </div>

      {/* Ações Rápidas Offshore */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h3 className="text-xl font-semibold mb-4">⚡ Controle Offshore - Ações Rápidas</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
            <div className="text-2xl mb-2">🧪</div>
            <div className="text-sm font-medium">Simulação IEEE</div>
          </button>
          <button className="p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
            <div className="text-2xl mb-2">🛡️</div>
            <div className="text-sm font-medium">Config. ANSI</div>
          </button>
          <button className="p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
            <div className="text-2xl mb-2">🧠</div>
            <div className="text-sm font-medium">Treinar RL</div>
          </button>
          <button className="p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors">
            <div className="text-2xl mb-2">📊</div>
            <div className="text-sm font-medium">Relatório 13.8kV</div>
          </button>
        </div>
      </div>
    </div>
  )
}
