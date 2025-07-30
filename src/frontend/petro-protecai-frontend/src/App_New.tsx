import { useState, useEffect } from 'react'
import './index.css'
import DashboardTab from './components/DashboardTab'
import NetworkTab from './components/NetworkTab'
import ProtectionTab from './components/ProtectionTab'
import SimulationTab from './components/SimulationTab'
import ReportsTab from './components/ReportsTab'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [apiHealth, setApiHealth] = useState<'checking' | 'healthy' | 'error'>('checking')

  useEffect(() => {
    // Check API health
    fetch('http://localhost:8000/health')
      .then(response => response.ok ? setApiHealth('healthy') : setApiHealth('error'))
      .catch(() => setApiHealth('error'))
  }, [])

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: '📊' },
    { id: 'network', name: 'Rede', icon: '🔌' },
    { id: 'protection', name: 'Proteção', icon: '🛡️' },
    { id: 'simulation', name: 'Simulação', icon: '🧪' },
    { id: 'reports', name: 'Relatórios', icon: '📋' }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold text-blue-600">⚡ ProtecAI Mini</div>
              <div className="text-sm text-gray-500">Sistema IEEE 14-Bus | Petrobras</div>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                apiHealth === 'healthy' 
                  ? 'bg-green-100 text-green-800' 
                  : apiHealth === 'error'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {apiHealth === 'healthy' ? '✅ API Online' : 
                 apiHealth === 'error' ? '❌ API Offline' : '⏳ Verificando...'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.icon} {tab.name}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {activeTab === 'dashboard' && <DashboardTab />}
        {activeTab === 'network' && <NetworkTab />}
        {activeTab === 'protection' && <ProtectionTab />}
        {activeTab === 'simulation' && <SimulationTab />}
        {activeTab === 'reports' && <ReportsTab />}
      </main>
    </div>
  )
}

export default App
