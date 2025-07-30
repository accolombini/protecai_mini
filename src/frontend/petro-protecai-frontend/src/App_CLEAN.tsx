import { useState, useEffect } from 'react'
import './index.css'
import DashboardTab from './components/DashboardTab'
import NetworkTab from './components/NetworkTab'
import ProtectionTab from './components/ProtectionTab'
import SimulationTab from './components/SimulationTab'
import ReportsTab from './components/ReportsTab'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [networkInfo, setNetworkInfo] = useState(null)
  const [apiStatus, setApiStatus] = useState({ backend: false })
  const [systemState, setSystemState] = useState({ status: 'initializing' })

  useEffect(() => {
    // Simula verificação de status da API
    const checkApiStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/')
        if (response.ok) {
          setApiStatus({ backend: true })
        }
      } catch (error) {
        setApiStatus({ backend: false })
      }
    }

    checkApiStatus()
    const interval = setInterval(checkApiStatus, 10000)
    return () => clearInterval(interval)
  }, [])

  const handleRunOptimization = async () => {
    try {
      const response = await fetch('http://localhost:8000/rl/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ episodes: 50 })
      })
      if (response.ok) {
        const result = await response.json()
        alert(`Otimização RL concluída! Score: ${result.best_coordination_score?.toFixed(2)}`)
      }
    } catch (error) {
      alert('Erro na otimização RL')
    }
  }

  const handleRunSimulation = async () => {
    try {
      const response = await fetch('http://localhost:8000/simulate_fault', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bus: 4, fault_type: '3ph', severity: 0.8 })
      })
      if (response.ok) {
        const result = await response.json()
        alert(`Simulação concluída! Coordenação: ${result.coordination_ok ? 'OK' : 'FALHA'}`)
      }
    } catch (error) {
      alert('Erro na simulação')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-lg border-b-4 border-blue-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">⚡</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ProtecAI Mini</h1>
                <p className="text-sm text-gray-600">IEEE 14-Bus Protection Coordination with RL</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                apiStatus.backend ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {apiStatus.backend ? '🟢 API Online' : '🔴 API Offline'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'dashboard', name: 'Dashboard', icon: '📊' },
              { id: 'network', name: 'Network', icon: '🔌' },
              { id: 'protection', name: 'Protection', icon: '🛡️' },
              { id: 'simulation', name: 'Simulation', icon: '⚡' },
              { id: 'reports', name: 'Reports', icon: '📋' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {activeTab === 'dashboard' && (
          <DashboardTab 
            networkInfo={networkInfo}
            apiStatus={apiStatus}
            systemState={systemState}
            onRunOptimization={handleRunOptimization}
            onRunSimulation={handleRunSimulation}
          />
        )}
        {activeTab === 'network' && <NetworkTab />}
        {activeTab === 'protection' && <ProtectionTab />}
        {activeTab === 'simulation' && <SimulationTab />}
        {activeTab === 'reports' && <ReportsTab />}
      </main>
    </div>
  )
}

export default App
