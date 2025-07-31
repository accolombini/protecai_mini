import { useState, useEffect } from 'react'
import './index.css'
import IEEE14BusSystem from './components/IEEE14BusSystem'
import ProtectionControlPanel from './components/ProtectionControlPanel'
import RealTimeDashboard from './components/RealTimeDashboard'
import IntegratedMonitoringTab from './components/IntegratedMonitoringTab'
import DashboardTab from './components/DashboardTab'
import SimulationTab from './components/SimulationTab'
import ReportsTab from './components/ReportsTab'
import EnhancedNetworkTab from './components/EnhancedNetworkTab'
import ZoneBasedProtectionView from './components/ZoneBasedProtectionView'

function App() {
  const [activeTab, setActiveTab] = useState('realtime')
  const [apiHealth, setApiHealth] = useState<'checking' | 'healthy' | 'error'>('checking')

  useEffect(() => {
    // Check API health
    fetch('http://localhost:8000/health')
      .then(response => response.ok ? setApiHealth('healthy') : setApiHealth('error'))
      .catch(() => setApiHealth('error'))
  }, [])

  const tabs = [
    { id: 'realtime', name: 'Tempo Real', icon: '📡' },
    { id: 'monitoring', name: 'Monitoramento Integrado', icon: '🎯' },
    { id: 'ieee14', name: 'IEEE 14-Bus', icon: '⚡' },
    { id: 'network', name: 'Status das Barras', icon: '🔌' },
    { id: 'protection', name: 'Coordenação', icon: '🛡️' },
    { id: 'simulation', name: 'Simulação RL', icon: '🧪' },
    { id: 'reports', name: 'Relatórios', icon: '📋' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold text-blue-600">🛢️ ProtecAI Mini</div>
              <div className="text-sm text-gray-500">Sistema IEEE 14-Bus | Coordenação Inteligente RL | Petrobras & UFF</div>
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
              <div className="px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                🤖 RL Agent Ativo
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-gradient-to-r from-blue-50 to-purple-50 shadow-sm border-b-2 border-blue-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 overflow-x-auto">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-3 px-4 rounded-t-lg font-medium text-sm transition-all duration-200 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-white text-blue-700 shadow-lg border-b-2 border-blue-500 transform -translate-y-1'
                    : 'text-gray-600 hover:text-blue-600 hover:bg-white hover:bg-opacity-50'
                }`}
              >
                <span className="text-lg mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 min-h-screen">
        <div className="mb-4">
          {activeTab === 'realtime' && (
            <div className="mb-4">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">📡 Monitoramento em Tempo Real</h1>
              <p className="text-gray-600">Sistema IEEE 14-Bus com otimização por Reinforcement Learning - Organizado por Zonas</p>
            </div>
          )}
          {activeTab === 'monitoring' && (
            <div className="mb-4">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">🎯 Centro de Controle Integrado</h1>
              <p className="text-gray-600">Visão completa das zonas de proteção, simulações e recomendações RL</p>
            </div>
          )}
          {activeTab === 'ieee14' && (
            <div className="mb-4">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">⚡ Sistema IEEE 14-Bus</h1>
              <p className="text-gray-600">Representação topológica completa com zonas de proteção</p>
            </div>
          )}
          {activeTab === 'network' && (
            <div className="mb-4">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">🔌 Status das Barras por Zona</h1>
              <p className="text-gray-600">Monitoramento individual das barras IEEE 14-Bus organizadas por zona de proteção</p>
            </div>
          )}
          {activeTab === 'protection' && (
            <div className="mb-4">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">🛡️ Proteção por Zonas</h1>
              <p className="text-gray-600">Coordenação inteligente dos dispositivos organizados por zonas de proteção Z1 e Z2</p>
            </div>
          )}
          {activeTab === 'simulation' && (
            <div className="mb-4">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">🧪 Simulação e Otimização RL</h1>
              <p className="text-gray-600">Simulações de falta e recomendações do agente de Reinforcement Learning</p>
            </div>
          )}
        </div>
        
        {activeTab === 'realtime' && <RealTimeDashboard />}
        {activeTab === 'monitoring' && <IntegratedMonitoringTab />}
        {activeTab === 'ieee14' && <IEEE14BusSystem />}
        {activeTab === 'network' && <EnhancedNetworkTab />}
        {activeTab === 'protection' && <ZoneBasedProtectionView />}
        {activeTab === 'simulation' && <SimulationTab />}
        {activeTab === 'reports' && <ReportsTab />}
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-blue-900 to-purple-900 text-white py-8 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">🛢️ ProtecAI Mini</h3>
              <p className="text-blue-100 text-sm">
                Sistema Inteligente de Coordenação de Proteção para redes IEEE 14-Bus 
                utilizando algoritmos de Reinforcement Learning.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">📊 Tecnologias</h3>
              <ul className="text-blue-100 text-sm space-y-1">
                <li>• Python + FastAPI Backend</li>
                <li>• React + TypeScript Frontend</li>
                <li>• Q-Learning Algorithm</li>
                <li>• IEEE 14-Bus System</li>
                <li>• PandaPower Simulation</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">🎯 Status do Sistema</h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-green-200">Backend API: Online</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-green-200">RL Agent: Ativo</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-green-200">IEEE 14-Bus: Operacional</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="border-t border-blue-800 mt-8 pt-8 text-center">
            <p className="text-blue-200 text-sm">
              © 2024 ProtecAI Mini - Projeto Petrobras & UFF | 
              <span className="font-semibold ml-2">Desenvolvido para Coordenação Inteligente de Proteção</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
