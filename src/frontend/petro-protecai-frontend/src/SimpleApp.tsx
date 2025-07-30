import { useState } from 'react'

interface SimulationResult {
  scenario: {
    type: string
    location: string
    severity: number
    rl_enabled: boolean
  }
  results: {
    fault_analysis: {
      current: number
      clearance_time: number
      severity_level: string
    }
    device_actions: Array<{
      device: string
      type: string
      action: string
      timing: string
    }>
    rl_optimization: {
      episodes_trained: number
      final_reward: number
      improvement: {
        response_time: string
        coordination_score: string
      }
    }
    compliance_assessment: {
      overall_score: number
      safety_level: string
    }
  }
}

export default function SimpleApp() {
  const [scenario, setScenario] = useState({
    type: 'fault',
    location: 'Bus_1',
    severity: 0.5,
    rl_enabled: true
  })
  const [results, setResults] = useState<SimulationResult | null>(null)
  const [loading, setLoading] = useState(false)

  const executeSimulation = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/protection/scenarios', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scenario)
      })
      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error('Erro na simulação:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 p-8">
      <h1 className="text-4xl font-bold text-gray-800 mb-2 flex items-center gap-3">
        🔋 ProtecAI Mini - Simulador
      </h1>
      <p className="text-gray-600 mb-8">Sistema de Coordenação de Proteção IEEE 14 Barras</p>

      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
          🚀 Configuração da Simulação
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium mb-2">Tipo de Cenário</label>
            <select 
              className="w-full p-3 border rounded-lg"
              value={scenario.type}
              onChange={(e) => setScenario({...scenario, type: e.target.value})}
            >
              <option value="fault">⚡ Curto-Circuito</option>
              <option value="load_change">📊 Mudança de Carga</option>
              <option value="equipment_failure">🔧 Falha de Equipamento</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Localização</label>
            <select 
              className="w-full p-3 border rounded-lg"
              value={scenario.location}
              onChange={(e) => setScenario({...scenario, location: e.target.value})}
            >
              {Array.from({length: 14}, (_, i) => (
                <option key={i} value={`Bus_${i+1}`}>Barra {i+1}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Severidade: {scenario.severity.toFixed(2)}</label>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.1"
              value={scenario.severity}
              onChange={(e) => setScenario({...scenario, severity: parseFloat(e.target.value)})}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={scenario.rl_enabled}
              onChange={(e) => setScenario({...scenario, rl_enabled: e.target.checked})}
              className="rounded"
            />
            🧠 Usar Reinforcement Learning
          </label>

          <button
            onClick={executeSimulation}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? '⏳' : '▶️'} Executar Simulação
          </button>
        </div>
      </div>

      {results && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
            📊 Resultados da Simulação
          </h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600">
                {Math.round(results.results.fault_analysis.clearance_time * 1000)}ms
              </div>
              <div className="text-sm text-gray-600">Tempo de Atuação</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-orange-600">
                {Math.round(results.results.fault_analysis.current)}A
              </div>
              <div className="text-sm text-gray-600">Corrente de Falha</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600">
                {results.results.device_actions.length}
              </div>
              <div className="text-sm text-gray-600">Dispositivos Acionados</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-purple-600">
                {(results.results.compliance_assessment.overall_score * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Score de Conformidade</div>
            </div>
          </div>

          {scenario.rl_enabled && (
            <div className="bg-pink-50 p-4 rounded-lg mb-6">
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                🧠 Otimização RL
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="font-medium">Episódios: </span>
                  {results.results.rl_optimization.episodes_trained}
                </div>
                <div>
                  <span className="font-medium">Reward Final: </span>
                  {results.results.rl_optimization.final_reward.toFixed(3)}
                </div>
                <div>
                  <span className="font-medium">Melhoria Tempo: </span>
                  {results.results.rl_optimization.improvement.response_time}
                </div>
                <div>
                  <span className="font-medium">Melhoria Coordenação: </span>
                  {results.results.rl_optimization.improvement.coordination_score}
                </div>
              </div>
            </div>
          )}

          <div>
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              🔌 Ações dos Dispositivos
            </h3>
            <div className="space-y-2">
              {results.results.device_actions.map((action, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div className="font-medium">{action.device}</div>
                  <div className="text-sm text-gray-600">({action.type})</div>
                  <div className="font-semibold text-blue-600">{action.action}</div>
                  <div className="text-sm text-gray-500">{action.timing}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
