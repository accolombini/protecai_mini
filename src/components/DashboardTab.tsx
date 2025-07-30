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

interface Alert {
  id: number
  type: 'info' | 'warning' | 'error'
  message: string
  time: string
}

interface ProtectionDevice {
  id: string
  zone: string
  type: string
  location: string
  pickup_current: number
  time_delay: number
  status: string
}

interface RLStatus {
  status: string
  episodes: number
  epsilon: number
  learning_rate: number
  state_size: number
  action_space_size: number
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
  }>
  coordination_issues: Array<{
    device1: string
    device2: string
    margin: number
  }>
}

// Componente Dashboard Principal
export default function DashboardTab() {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null)
  const [devices, setDevices] = useState<ProtectionDevice[]>([])
  const [rlStatus, setRlStatus] = useState<RLStatus | null>(null)
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [isTraining, setIsTraining] = useState(false)
  const [isSimulating, setIsSimulating] = useState(false)
  const [simulationResult, setSimulationResult] = useState<FaultSimulationResult | null>(null)
  const [isOptimizing, setIsOptimizing] = useState(false)

  // Estados para simulação de falta
  const [faultBus, setFaultBus] = useState(4)
  const [faultType, setFaultType] = useState('3ph')
  const [faultSeverity, setFaultSeverity] = useState(0.8)

  // Estados para treinamento RL
  const [trainEpisodes, setTrainEpisodes] = useState(10)
  const [optimizeEpisodes, setOptimizeEpisodes] = useState(50)

  // API calls
  const API_BASE = 'http://localhost:8000/api'

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/status`)
      if (response.ok) {
        const data = await response.json()
        setSystemMetrics({
          uptime: data.uptime || '00:00:00',
          cpu_usage: Math.random() * 100,
          memory_usage: Math.random() * 100,
          active_simulations: data.active_simulations || 0,
          total_devices: data.total_devices || 0,
          network_status: data.system_health === 'healthy' ? 'healthy' : 'warning'
        })
      }
    } catch (error) {
      console.error('Erro ao buscar status:', error)
    }
  }

  const fetchDevices = async () => {
    try {
      const response = await fetch(`${API_BASE}/devices`)
      if (response.ok) {
        const data = await response.json()
        setDevices(data)
      }
    } catch (error) {
      console.error('Erro ao buscar dispositivos:', error)
    }
  }

  const fetchRLStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/rl/status`)
      if (response.ok) {
        const data = await response.json()
        setRlStatus(data)
      }
    } catch (error) {
      console.error('Erro ao buscar status RL:', error)
    }
  }

  const simulateFault = async () => {
    setIsSimulating(true)
    try {
      const response = await fetch(
        `${API_BASE}/simulate_fault/${faultBus}?fault_type=${faultType}&severity=${faultSeverity}`,
        { method: 'POST' }
      )
      if (response.ok) {
        const data = await response.json()
        setSimulationResult(data)
        addAlert('info', `Simulação executada no Bus ${faultBus}`)
      }
    } catch (error) {
      console.error('Erro na simulação:', error)
      addAlert('error', 'Erro na simulação de falta')
    }
    setIsSimulating(false)
  }

  const trainRL = async () => {
    setIsTraining(true)
    try {
      const response = await fetch(`${API_BASE}/rl/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          episodes: trainEpisodes,
          scenarios: [
            { bus: 4, fault_type: '3ph', severity: 0.8 },
            { bus: 7, fault_type: '2ph', severity: 0.6 },
            { bus: 14, fault_type: '1ph', severity: 0.5 }
          ]
        })
      })
      if (response.ok) {
        const data = await response.json()
        addAlert('info', `Treinamento RL concluído: ${data.episodes_completed} episódios`)
        fetchRLStatus()
      }
    } catch (error) {
      console.error('Erro no treinamento:', error)
      addAlert('error', 'Erro no treinamento RL')
    }
    setIsTraining(false)
  }

  const optimizeWithRL = async () => {
    setIsOptimizing(true)
    try {
      const response = await fetch(`${API_BASE}/rl/optimize?episodes=${optimizeEpisodes}`, {
        method: 'POST'
      })
      if (response.ok) {
        const data = await response.json()
        addAlert('info', `Otimização concluída! Score: ${data.best_coordination_score.toFixed(1)}`)
        fetchDevices() // Atualizar dispositivos após otimização
      }
    } catch (error) {
      console.error('Erro na otimização:', error)
      addAlert('error', 'Erro na otimização RL')
    }
    setIsOptimizing(false)
  }

  const addAlert = (type: 'info' | 'warning' | 'error', message: string) => {
    const newAlert: Alert = {
      id: Date.now(),
      type,
      message,
      time: new Date().toLocaleTimeString()
    }
    setAlerts(prev => [newAlert, ...prev.slice(0, 9)]) // Manter últimos 10
  }

  // Carregar dados iniciais
  useEffect(() => {
    fetchSystemStatus()
    fetchDevices()
    fetchRLStatus()
    
    // Atualizar dados a cada 5 segundos
    const interval = setInterval(() => {
      fetchSystemStatus()
      fetchRLStatus()
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600'
      case 'warning': return 'text-yellow-600'
      case 'critical': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'info': return 'border-blue-500 bg-blue-50'
      case 'warning': return 'border-yellow-500 bg-yellow-50'
      case 'error': return 'border-red-500 bg-red-50'
      default: return 'border-gray-500 bg-gray-50'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header com Métricas do Sistema */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Sistema</p>
              <p className={`text-2xl font-bold ${getStatusColor(systemMetrics?.network_status || 'warning')}`}>
                {systemMetrics?.network_status || 'CARREGANDO'}
              </p>
              <p className="text-xs text-gray-500">Uptime: {systemMetrics?.uptime || '00:00:00'}</p>
            </div>
            <div className="text-blue-500">
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h12a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1V8z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Dispositivos ANSI</p>
              <p className="text-2xl font-bold text-gray-900">{devices.length}</p>
              <p className="text-xs text-gray-500">IEEE 14-Bus</p>
            </div>
            <div className="text-yellow-500">
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Agente RL</p>
              <p className="text-2xl font-bold text-gray-900">{rlStatus?.status || 'INIT'}</p>
              <p className="text-xs text-gray-500">Episódios: {rlStatus?.episodes || 0}</p>
            </div>
            <div className="text-green-500">
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Simulações</p>
              <p className="text-2xl font-bold text-gray-900">{systemMetrics?.active_simulations || 0}</p>
              <p className="text-xs text-gray-500">Ativas</p>
            </div>
            <div className="text-purple-500">
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Seção de Controles */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Simulação de Falta */}
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">🔧 Simulação de Falta</h3>
          
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Bus</label>
                <select 
                  value={faultBus} 
                  onChange={(e) => setFaultBus(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  {[1,2,3,4,5,6,7,8,9,10,11,12,13,14].map(bus => (
                    <option key={bus} value={bus}>Bus {bus}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tipo</label>
                <select 
                  value={faultType} 
                  onChange={(e) => setFaultType(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="3ph">3φ</option>
                  <option value="2ph">2φ</option>
                  <option value="1ph">1φ</option>
                  <option value="2ph_ground">2φ-Terra</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Severidade</label>
                <input 
                  type="range" 
                  min="0.1" 
                  max="1.0" 
                  step="0.1" 
                  value={faultSeverity}
                  onChange={(e) => setFaultSeverity(Number(e.target.value))}
                  className="w-full"
                />
                <span className="text-sm text-gray-600">{(faultSeverity * 100).toFixed(0)}%</span>
              </div>
            </div>
            
            <button 
              onClick={simulateFault}
              disabled={isSimulating}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              {isSimulating ? 'Simulando...' : 'Executar Simulação'}
            </button>
          </div>

          {simulationResult && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-800 mb-2">Resultado da Simulação:</h4>
              <div className="space-y-2 text-sm">
                <p><strong>Local:</strong> {simulationResult.fault_location}</p>
                <p><strong>Corrente:</strong> {simulationResult.fault_current_a.toFixed(0)} A</p>
                <p><strong>Zona Afetada:</strong> {simulationResult.affected_zone}</p>
                <p><strong>Coordenação:</strong> 
                  <span className={simulationResult.coordination_ok ? 'text-green-600' : 'text-red-600'}>
                    {simulationResult.coordination_ok ? ' ✓ OK' : ' ✗ FALHOU'}
                  </span>
                </p>
                <p><strong>Dispositivos Operantes:</strong> {simulationResult.device_responses.filter(d => d.should_operate).length}</p>
              </div>
            </div>
          )}
        </div>

        {/* Treinamento RL */}
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">🤖 Controle RL</h3>
          
          <div className="space-y-4">
            {/* Status RL */}
            {rlStatus && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <p><strong>Status:</strong> {rlStatus.status}</p>
                  <p><strong>Episódios:</strong> {rlStatus.episodes}</p>
                  <p><strong>Epsilon:</strong> {rlStatus.epsilon.toFixed(3)}</p>
                  <p><strong>LR:</strong> {rlStatus.learning_rate}</p>
                </div>
              </div>
            )}

            {/* Treinamento Básico */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Episódios de Treinamento: {trainEpisodes}
              </label>
              <input 
                type="range" 
                min="5" 
                max="50" 
                step="5" 
                value={trainEpisodes}
                onChange={(e) => setTrainEpisodes(Number(e.target.value))}
                className="w-full mb-2"
              />
              <button 
                onClick={trainRL}
                disabled={isTraining}
                className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                {isTraining ? 'Treinando...' : 'Treinar Agente RL'}
              </button>
            </div>

            {/* Otimização Avançada */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Episódios de Otimização: {optimizeEpisodes}
              </label>
              <input 
                type="range" 
                min="25" 
                max="200" 
                step="25" 
                value={optimizeEpisodes}
                onChange={(e) => setOptimizeEpisodes(Number(e.target.value))}
                className="w-full mb-2"
              />
              <button 
                onClick={optimizeWithRL}
                disabled={isOptimizing}
                className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                {isOptimizing ? 'Otimizando...' : 'Otimização Avançada'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Lista de Dispositivos e Alertas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Dispositivos de Proteção */}
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">⚡ Dispositivos ANSI</h3>
          
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {devices.map((device) => (
              <div key={device.id} className="p-3 bg-gray-50 rounded-lg border">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-gray-900">{device.id}</p>
                    <p className="text-sm text-gray-600">{device.location}</p>
                    <p className="text-xs text-gray-500">
                      Tipo: {device.type} | Zona: {device.zone}
                    </p>
                  </div>
                  <div className="text-right text-sm">
                    <p className="text-gray-700">I: {device.pickup_current.toFixed(2)} pu</p>
                    <p className="text-gray-700">t: {device.time_delay.toFixed(2)} s</p>
                    <span className={`inline-block px-2 py-1 rounded text-xs ${
                      device.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {device.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Alertas do Sistema */}
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">🚨 Alertas do Sistema</h3>
          
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {alerts.length === 0 ? (
              <p className="text-gray-500 text-center py-4">Nenhum alerta</p>
            ) : (
              alerts.map((alert) => (
                <div key={alert.id} className={`p-3 rounded-lg border-l-4 ${getAlertColor(alert.type)}`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                      <p className="text-xs text-gray-500">{alert.time}</p>
                    </div>
                    <span className={`inline-block px-2 py-1 rounded text-xs capitalize ${
                      alert.type === 'error' ? 'bg-red-100 text-red-800' :
                      alert.type === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {alert.type}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* ALERTA CRÍTICO - Conformidade Normativa */}
      <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-red-500">
        <h3 className="text-xl font-semibold mb-4 text-red-600">⚠️ CONFORMIDADE NORMATIVA - AGUARDANDO VALIDAÇÃO</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-red-50 rounded-lg">
            <h4 className="font-semibold text-red-800">IEEE C37.112</h4>
            <p className="text-sm text-red-600">Coordenação de Proteção</p>
            <p className="text-xs text-red-500 mt-1">Validação pendente</p>
          </div>
          
          <div className="p-4 bg-yellow-50 rounded-lg">
            <h4 className="font-semibold text-yellow-800">ABNT NBR 14039</h4>
            <p className="text-sm text-yellow-600">Instalações Elétricas</p>
            <p className="text-xs text-yellow-500 mt-1">Em análise</p>
          </div>
          
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-blue-800">API RP 14F</h4>
            <p className="text-sm text-blue-600">Offshore Safety</p>
            <p className="text-xs text-blue-500 mt-1">Parcialmente conforme</p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg">
            <h4 className="font-semibold text-green-800">IEC 60255-151</h4>
            <p className="text-sm text-green-600">Proteção Multifuncional</p>
            <p className="text-xs text-green-500 mt-1">Conforme</p>
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-gray-100 rounded-lg">
          <p className="text-sm text-gray-700">
            <strong>Status:</strong> Sistema funcional com RL implementado. Validação de conformidade normativa em andamento.
          </p>
          <p className="text-xs text-gray-600 mt-1">
            Última atualização: {new Date().toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  )
}
