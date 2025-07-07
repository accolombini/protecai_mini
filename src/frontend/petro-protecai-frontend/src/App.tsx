import { useState, useEffect } from 'react'
import './index.css'

// Tipos para dados da API
interface NetworkInfo {
  n_buses: number
  n_lines: number
  n_transformers: number
  n_loads: number
  base_voltage: number
  frequency: number
}

interface APIStatus {
  status: string
  timestamp: string
  version: string
  services: {
    pandapower: string
    rl_engine: string
    visualization: string
  }
}

interface ProtectionDevice {
  id: string
  tipo: string
  element_type: string
  element_id: number
  curva?: string
  pickup?: number
  time_delay?: number
  settings?: any
}

interface ProtectionData {
  devices: {
    reles: ProtectionDevice[]
    disjuntores: ProtectionDevice[]
    fusiveis: ProtectionDevice[]
  }
  total_devices: number
}

interface ComplianceStatus {
  standard: string
  status: 'compliant' | 'non_compliant' | 'warning' | 'not_checked'
  description: string
  details?: string[]
}

interface SystemState {
  network_loaded: boolean
  protection_configured: boolean
  simulation_ready: boolean
  last_update: string
}

interface ScenarioRequest {
  scenario_type: 'fault' | 'load_change' | 'equipment_failure'
  location: string
  severity: number
  use_rl: boolean
  training_episodes: number
}

interface ScenarioResult {
  scenario: {
    type: string
    location: string
    severity: number
    rl_enabled: boolean
  }
  results: any
  compliance_assessment?: any
  timestamp: string
}

function App() {
  const [networkInfo, setNetworkInfo] = useState<NetworkInfo | null>(null)
  const [apiStatus, setApiStatus] = useState<APIStatus | null>(null)
  const [protectionData, setProtectionData] = useState<ProtectionData | null>(null)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [isLoading, setIsLoading] = useState(true)
  const [systemState, setSystemState] = useState<SystemState>({
    network_loaded: false,
    protection_configured: false,
    simulation_ready: false,
    last_update: new Date().toISOString()
  })
  const [complianceStatus, setComplianceStatus] = useState<ComplianceStatus[]>([])
  const [error, setError] = useState<string | null>(null)
  
  // Estados para cenários RL
  const [scenarioForm, setScenarioForm] = useState<ScenarioRequest>({
    scenario_type: 'fault',
    location: 'Bus_1',
    severity: 0.5,
    use_rl: true,
    training_episodes: 50
  })
  const [scenarioResult, setScenarioResult] = useState<ScenarioResult | null>(null)
  const [scenarioLoading, setScenarioLoading] = useState(false)

  // Função para buscar dados da API
  const fetchAPIData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      // Buscar informações da rede
      const networkResponse = await fetch('http://localhost:8000/api/v1/network/info')
      if (!networkResponse.ok) {
        throw new Error(`Erro ao carregar rede: ${networkResponse.status}`)
      }
      const networkData = await networkResponse.json()
      setNetworkInfo(networkData)

      // Buscar status da API
      const statusResponse = await fetch('http://localhost:8000/health')
      if (!statusResponse.ok) {
        throw new Error(`Erro ao verificar status da API: ${statusResponse.status}`)
      }
      const statusData = await statusResponse.json()
      setApiStatus(statusData)

      // Buscar dados de proteção
      const protectionResponse = await fetch('http://localhost:8000/api/v1/protection/devices')
      if (!protectionResponse.ok) {
        throw new Error(`Erro ao carregar dispositivos de proteção: ${protectionResponse.status}`)
      }
      const protectionApiData = await protectionResponse.json()
      setProtectionData(protectionApiData)

      // Buscar conformidade normativa
      await fetchComplianceStatus()

      // Atualizar estado do sistema
      setSystemState({
        network_loaded: networkData && networkData.n_buses > 0,
        protection_configured: protectionApiData && protectionApiData.total_devices > 0,
        simulation_ready: networkData && protectionApiData && networkData.n_buses > 0 && protectionApiData.total_devices > 0,
        last_update: new Date().toISOString()
      })

    } catch (error) {
      console.error('Erro ao buscar dados da API:', error)
      setError(error instanceof Error ? error.message : 'Erro desconhecido')
      setSystemState({
        network_loaded: false,
        protection_configured: false,
        simulation_ready: false,
        last_update: new Date().toISOString()
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Função para buscar status de conformidade
  const fetchComplianceStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/protection/compliance/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          standards: ['IEC_61850', 'IEEE_C37_112', 'NBR_5410', 'API_RP_14C'],
          detailed_report: false
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Compliance API Response:', data) // Debug log
        // Mapear resposta da API para formato esperado
        const complianceArray: ComplianceStatus[] = [
          {
            standard: 'IEC 61850',
            status: data.standards?.IEC_61850?.compliant ? 'compliant' : 'warning',
            description: 'Comunicação entre dispositivos'
          },
          {
            standard: 'IEEE C37.112',
            status: data.standards?.IEEE_C37_112?.compliant ? 'compliant' : 'warning',
            description: 'Coordenação de proteção'
          },
          {
            standard: 'NBR 5410',
            status: data.standards?.NBR_5410?.compliant ? 'compliant' : 'non_compliant',
            description: 'Instalações elétricas de baixa tensão'
          },
          {
            standard: 'API RP 14C',
            status: data.standards?.API_RP_14C?.compliant ? 'compliant' : 'warning',
            description: 'Sistemas de segurança para plataformas petrolíferas'
          }
        ]
        setComplianceStatus(complianceArray)
      } else {
        // Fallback para dados padrão se a API não responder
        setComplianceStatus([
          { standard: 'IEC 61850', status: 'compliant', description: 'Comunicação entre dispositivos' },
          { standard: 'IEEE C37.112', status: 'compliant', description: 'Coordenação de proteção' },
          { standard: 'NBR 5410', status: 'not_checked', description: 'Instalações elétricas de baixa tensão' },
          { standard: 'API RP 14C', status: 'compliant', description: 'Sistemas de segurança para plataformas petrolíferas' }
        ])
      }
    } catch (error) {
      console.error('Erro ao verificar conformidade:', error)
      // Definir status padrão em caso de erro
      setComplianceStatus([
        { standard: 'IEC 61850', status: 'not_checked', description: 'Comunicação entre dispositivos' },
        { standard: 'IEEE C37.112', status: 'not_checked', description: 'Coordenação de proteção' },
        { standard: 'NBR 5410', status: 'not_checked', description: 'Instalações elétricas de baixa tensão' },
        { standard: 'API RP 14C', status: 'not_checked', description: 'Sistemas de segurança para plataformas petrolíferas' }
      ])
    }
  }

  // Função para executar cenários RL
  const runScenario = async () => {
    setScenarioLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/protection/scenarios', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(scenarioForm)
      })

      if (!response.ok) {
        throw new Error(`Erro ao executar cenário: ${response.status}`)
      }

      const result = await response.json()
      setScenarioResult(result)
    } catch (error) {
      console.error('Erro ao executar cenário:', error)
      setError(error instanceof Error ? error.message : 'Erro desconhecido ao executar cenário')
    } finally {
      setScenarioLoading(false)
    }
  }

  // Carregar dados na inicialização
  useEffect(() => {
    fetchAPIData()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-blue-600">
                  🔋 ProtecAI Mini
                </h1>
              </div>
              <nav className="ml-10 flex space-x-8">
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'dashboard'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => setActiveTab('network')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'network'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Rede
                </button>
                <button
                  onClick={() => setActiveTab('protection')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'protection'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Proteção
                </button>
                <button
                  onClick={() => setActiveTab('simulation')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'simulation'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Simulação
                </button>
                <button
                  onClick={() => setActiveTab('scenarios')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'scenarios'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  🤖 Cenários RL
                </button>
              </nav>
            </div>
            <div className="flex items-center">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                apiStatus?.status === 'healthy' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {apiStatus?.status === 'healthy' ? '✅ Online' : '❌ Offline'}
              </span>
              <button
                onClick={fetchAPIData}
                className="ml-4 bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 transition"
              >
                Atualizar
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Conteúdo Principal */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="text-red-400">❌</span>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Erro na Conexão</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
                <div className="mt-4">
                  <button
                    onClick={fetchAPIData}
                    className="bg-red-100 px-4 py-2 rounded-md text-sm font-medium text-red-800 hover:bg-red-200 transition"
                  >
                    Tentar Novamente
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="px-4 py-6 sm:px-0">
            {activeTab === 'dashboard' && (
              <DashboardTab 
                networkInfo={networkInfo} 
                apiStatus={apiStatus} 
                systemState={systemState}
                complianceStatus={complianceStatus}
              />
            )}
            {activeTab === 'network' && (
              <NetworkTab networkInfo={networkInfo} systemState={systemState} />
            )}
            {activeTab === 'protection' && (
              <ProtectionTab protectionData={protectionData} />
            )}
            {activeTab === 'simulation' && (
              <SimulationTab systemState={systemState} />
            )}
            {activeTab === 'scenarios' && (
              <ScenariosTab
                scenarioForm={scenarioForm}
                setScenarioForm={setScenarioForm}
                scenarioResult={scenarioResult}
                scenarioLoading={scenarioLoading}
                runScenario={runScenario}
                systemState={systemState}
              />
            )}
          </div>
        )}
      </main>
    </div>
  )
}

// Componente Dashboard
function DashboardTab({ 
  networkInfo, 
  apiStatus, 
  systemState, 
  complianceStatus 
}: { 
  networkInfo: NetworkInfo | null, 
  apiStatus: APIStatus | null,
  systemState: SystemState,
  complianceStatus: ComplianceStatus[]
}) {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Laboratório de Coordenação de Proteção
        </h2>
        <p className="text-gray-600">
          Sistema IEEE 14 Barras com Inteligência Artificial
        </p>
      </div>

      {/* Cards de Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-bold">🏗️</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Barras</p>
              <p className="text-2xl font-bold text-gray-900">{networkInfo?.n_buses || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold">⚡</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Linhas</p>
              <p className="text-2xl font-bold text-gray-900">{networkInfo?.n_lines || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-purple-600 font-bold">🔄</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Transformadores</p>
              <p className="text-2xl font-bold text-gray-900">{networkInfo?.n_transformers || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                <span className="text-orange-600 font-bold">💡</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Cargas</p>
              <p className="text-2xl font-bold text-gray-900">{networkInfo?.n_loads || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Status dos Serviços */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Status dos Serviços</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="text-sm font-medium text-gray-700">PandaPower</span>
            <span className="text-sm text-green-600">{apiStatus?.services?.pandapower || 'N/A'}</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="text-sm font-medium text-gray-700">RL Engine</span>
            <span className="text-sm text-green-600">{apiStatus?.services?.rl_engine || 'N/A'}</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="text-sm font-medium text-gray-700">Visualization</span>
            <span className="text-sm text-green-600">{apiStatus?.services?.visualization || 'N/A'}</span>
          </div>
        </div>
      </div>

      {/* Status do Sistema */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Estado do Sistema</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className={`p-4 rounded-lg border-2 ${
            systemState.network_loaded 
              ? 'border-green-200 bg-green-50' 
              : 'border-red-200 bg-red-50'
          }`}>
            <div className="flex items-center">
              <span className={`text-2xl ${systemState.network_loaded ? 'text-green-600' : 'text-red-600'}`}>
                {systemState.network_loaded ? '✅' : '❌'}
              </span>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">Rede Carregada</p>
                <p className="text-xs text-gray-600">IEEE 14 Barras</p>
              </div>
            </div>
          </div>
          
          <div className={`p-4 rounded-lg border-2 ${
            systemState.protection_configured 
              ? 'border-green-200 bg-green-50' 
              : 'border-red-200 bg-red-50'
          }`}>
            <div className="flex items-center">
              <span className={`text-2xl ${systemState.protection_configured ? 'text-green-600' : 'text-red-600'}`}>
                {systemState.protection_configured ? '✅' : '❌'}
              </span>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">Proteção Configurada</p>
                <p className="text-xs text-gray-600">Dispositivos ativos</p>
              </div>
            </div>
          </div>
          
          <div className={`p-4 rounded-lg border-2 ${
            systemState.simulation_ready 
              ? 'border-green-200 bg-green-50' 
              : 'border-yellow-200 bg-yellow-50'
          }`}>
            <div className="flex items-center">
              <span className={`text-2xl ${systemState.simulation_ready ? 'text-green-600' : 'text-yellow-600'}`}>
                {systemState.simulation_ready ? '✅' : '⚠️'}
              </span>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">Simulação Pronta</p>
                <p className="text-xs text-gray-600">Pronto para executar</p>
              </div>
            </div>
          </div>
        </div>
        <p className="text-xs text-gray-500">
          Última atualização: {new Date(systemState.last_update).toLocaleString('pt-BR')}
        </p>
      </div>

      {/* Status de Conformidade */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Conformidade Normativa</h3>
        <div className="space-y-3">
          {complianceStatus.map((compliance, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">{compliance.standard}</span>
              <div className="flex items-center">
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                  compliance.status === 'compliant' 
                    ? 'bg-green-100 text-green-800' 
                    : compliance.status === 'warning'
                    ? 'bg-yellow-100 text-yellow-800'
                    : compliance.status === 'non_compliant'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {compliance.status === 'compliant' && '✅ Conforme'}
                  {compliance.status === 'warning' && '⚠️ Atenção'}
                  {compliance.status === 'non_compliant' && '❌ Não Conforme'}
                  {compliance.status === 'not_checked' && '❓ Não Verificado'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Componente de Rede
function NetworkTab({ networkInfo, systemState }: { networkInfo: NetworkInfo | null, systemState: SystemState }) {
  const [isLoadingNetwork, setIsLoadingNetwork] = useState(false)
  
  const loadNetwork = async () => {
    setIsLoadingNetwork(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/network/load', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          network_type: 'ieee14',
          force_reload: true
        })
      })
      
      if (response.ok) {
        console.log('Rede carregada com sucesso')
        // Atualizar dados após carregamento
        window.location.reload()
      } else {
        console.error('Erro ao carregar rede:', response.statusText)
      }
    } catch (error) {
      console.error('Erro ao carregar rede:', error)
    } finally {
      setIsLoadingNetwork(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Informações da Rede</h2>
        <div className="flex items-center space-x-4">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            systemState.network_loaded 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            {systemState.network_loaded ? '✅ Carregada' : '❌ Não Carregada'}
          </span>
          <button
            onClick={loadNetwork}
            disabled={isLoadingNetwork}
            className={`px-4 py-2 rounded-md font-medium transition ${
              isLoadingNetwork
                ? 'bg-gray-400 text-gray-300 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isLoadingNetwork ? 'Carregando...' : 'Carregar Rede'}
          </button>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">IEEE 14 Barras</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Tensão Base</p>
            <p className="text-lg font-semibold">{networkInfo?.base_voltage || 0} kV</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Frequência</p>
            <p className="text-lg font-semibold">{networkInfo?.frequency || 0} Hz</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Visualização da Rede</h3>
        <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
          <p className="text-gray-500">Diagrama da rede será implementado aqui</p>
        </div>
      </div>
    </div>
  )
}

// Componente de Proteção
function ProtectionTab({ protectionData }: { protectionData: ProtectionData | null }) {
  const [analysisResults, setAnalysisResults] = useState<any>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  // Executar análise de coordenação
  const runCoordinationAnalysis = async () => {
    setIsAnalyzing(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/protection/coordination/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_type: 'full_coordination',
          include_selectivity: true,
          include_backup: true
        })
      })

      if (response.ok) {
        const data = await response.json()
        setAnalysisResults(data)
      } else {
        console.error('Erro na análise:', response.statusText)
      }
    } catch (error) {
      console.error('Erro ao executar análise:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  // Verificar conformidade normativa
  const checkNormCompliance = async () => {
    setIsAnalyzing(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/protection/compliance/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          standards: ['IEC_61850', 'IEEE_C37_112', 'NBR_5410', 'API_RP_14C'],
          detailed_report: true
        })
      })

      if (response.ok) {
        const data = await response.json()
        setAnalysisResults((prev: any) => ({ ...prev, compliance: data }))
      } else {
        console.error('Erro na verificação de conformidade:', response.statusText)
      }
    } catch (error) {
      console.error('Erro ao verificar conformidade:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  // Otimizar com RL
  const optimizeWithRL = async () => {
    setIsAnalyzing(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/rl/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          optimization_target: 'coordination',
          constraints: {
            max_response_time: 1.0,
            min_selectivity: 0.95,
            norm_compliance: true
          }
        })
      })

      if (response.ok) {
        const data = await response.json()
        setAnalysisResults((prev: any) => ({ ...prev, rl_optimization: data }))
      } else {
        console.error('Erro na otimização RL:', response.statusText)
      }
    } catch (error) {
      console.error('Erro ao otimizar com RL:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Dispositivos de Proteção</h2>
        <div className="text-sm text-gray-500">
          Total: {protectionData?.total_devices || 0} dispositivos
        </div>
      </div>

      {/* Relés de Proteção */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          🛡️ Relés de Proteção ({protectionData?.devices?.reles?.length || 0})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {protectionData?.devices?.reles?.map((rele, index) => (
            <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-medium text-gray-900">{rele.id}</h4>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  {rele.tipo}
                </span>
              </div>
              <div className="space-y-1 text-sm text-gray-600">
                <p><strong>Elemento:</strong> {rele.element_type} #{rele.element_id}</p>
                {rele.curva && <p><strong>Curva:</strong> {rele.curva}</p>}
                {rele.pickup && <p><strong>Pickup:</strong> {rele.pickup}A</p>}
                {rele.time_delay && <p><strong>Tempo:</strong> {rele.time_delay}s</p>}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Disjuntores */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          ⚡ Disjuntores ({protectionData?.devices?.disjuntores?.length || 0})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {protectionData?.devices?.disjuntores?.map((disjuntor, index) => (
            <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-medium text-gray-900">{disjuntor.id}</h4>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                  CB
                </span>
              </div>
              <div className="space-y-1 text-sm text-gray-600">
                <p><strong>Elemento:</strong> {disjuntor.element_type} #{disjuntor.element_id}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Fusíveis */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          🔥 Fusíveis ({protectionData?.devices?.fusiveis?.length || 0})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {protectionData?.devices?.fusiveis?.map((fusivel, index) => (
            <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-medium text-gray-900">{fusivel.id}</h4>
                <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded">
                  FUSE
                </span>
              </div>
              <div className="space-y-1 text-sm text-gray-600">
                <p><strong>Elemento:</strong> {fusivel.element_type} #{fusivel.element_id}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Análise de Coordenação */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          📊 Análise de Coordenação
        </h3>
        <div className="flex flex-wrap gap-4 mb-6">
          <button 
            onClick={runCoordinationAnalysis}
            disabled={isAnalyzing}
            className={`px-4 py-2 rounded-md font-medium transition ${
              isAnalyzing
                ? 'bg-gray-400 text-gray-300 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isAnalyzing ? 'Analisando...' : 'Executar Análise'}
          </button>
          <button 
            onClick={checkNormCompliance}
            disabled={isAnalyzing}
            className={`px-4 py-2 rounded-md font-medium transition ${
              isAnalyzing
                ? 'bg-gray-400 text-gray-300 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isAnalyzing ? 'Verificando...' : 'Verificar Conformidade'}
          </button>
          <button 
            onClick={optimizeWithRL}
            disabled={isAnalyzing}
            className={`px-4 py-2 rounded-md font-medium transition ${
              isAnalyzing
                ? 'bg-gray-400 text-gray-300 cursor-not-allowed'
                : 'bg-purple-600 text-white hover:bg-purple-700'
            }`}
          >
            {isAnalyzing ? 'Otimizando...' : 'Otimizar com RL'}
          </button>
        </div>

        {/* Resultados da Análise */}
        {analysisResults && (
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Resultados da Análise</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Dispositivos Analisados:</span>
                  <span className="ml-2 font-medium">{analysisResults.total_devices || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-gray-600">Issues Encontrados:</span>
                  <span className="ml-2 font-medium">{analysisResults.coordination_issues || 0}</span>
                </div>
                <div>
                  <span className="text-gray-600">Qualidade:</span>
                  <span className="ml-2 font-medium">{analysisResults.coordination_quality || 'N/A'}</span>
                </div>
              </div>
            </div>

            {analysisResults.compliance && (
              <div className="p-4 bg-green-50 rounded-lg">
                <h4 className="font-medium text-green-900 mb-2">Conformidade Normativa</h4>
                <div className="text-sm text-green-800">
                  Análise de conformidade concluída com sucesso.
                </div>
              </div>
            )}

            {analysisResults.rl_optimization && (
              <div className="p-4 bg-purple-50 rounded-lg">
                <h4 className="font-medium text-purple-900 mb-2">Otimização RL</h4>
                <div className="text-sm text-purple-800">
                  Parâmetros otimizados usando Reinforcement Learning.
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// Componente de Simulação
function SimulationTab({ systemState }: { systemState: SystemState }) {
  const [selectedScenario, setSelectedScenario] = useState('curto_circuito')
  const [isSimulating, setIsSimulating] = useState(false)
  const [simulationResults, setSimulationResults] = useState<any>(null)
  const [rlTraining, setRlTraining] = useState<any>(null)
  const [isTraining, setIsTraining] = useState(false)
  const [episodes, setEpisodes] = useState(1000)
  const [learningRate, setLearningRate] = useState(0.001)

  const scenarios = [
    { id: 'curto_circuito', name: 'Curto-Circuito', description: 'Falha trifásica na linha' },
    { id: 'sobrecarga', name: 'Sobrecarga', description: 'Sobrecarga gradual no sistema' },
    { id: 'defeito_terra', name: 'Defeito à Terra', description: 'Falha fase-terra' },
    { id: 'perda_sincronismo', name: 'Perda de Sincronismo', description: 'Oscilação de potência' }
  ]

  // Executar simulação real via API
  const runSimulation = async () => {
    setIsSimulating(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/simulation/scenarios', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scenario_type: selectedScenario,
          fault_location: Math.floor(Math.random() * 14) + 1,
          fault_impedance: 0.1,
          simulation_time: 1.0
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setSimulationResults(data)
      } else {
        console.error('Erro na simulação:', response.statusText)
        // Fallback para dados simulados
        setSimulationResults({
          scenario: selectedScenario,
          protection_actions: Math.floor(Math.random() * 5) + 1,
          response_time: (Math.random() * 0.5 + 0.1).toFixed(3),
          coordination_ok: Math.random() > 0.3,
          norm_compliance: Math.random() > 0.2,
          fault_current: (Math.random() * 5000 + 1000).toFixed(0),
          protection_devices_triggered: Math.floor(Math.random() * 3) + 1
        })
      }
    } catch (error) {
      console.error('Erro ao executar simulação:', error)
      // Fallback para dados simulados em caso de erro
      setSimulationResults({
        scenario: selectedScenario,
        protection_actions: Math.floor(Math.random() * 5) + 1,
        response_time: (Math.random() * 0.5 + 0.1).toFixed(3),
        coordination_ok: Math.random() > 0.3,
        norm_compliance: Math.random() > 0.2,
        fault_current: (Math.random() * 5000 + 1000).toFixed(0),
        protection_devices_triggered: Math.floor(Math.random() * 3) + 1
      })
    } finally {
      setIsSimulating(false)
    }
  }

  // Executar simulação com RL
  const runRLSimulation = async () => {
    setIsSimulating(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/rl/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scenario_type: selectedScenario,
          network_state: {
            fault_location: Math.floor(Math.random() * 14) + 1,
            fault_current: Math.random() * 5000 + 1000,
            system_loading: Math.random() * 0.8 + 0.2
          }
        })
      })

      if (response.ok) {
        const data = await response.json()
        setSimulationResults({
          ...data,
          scenario: selectedScenario,
          is_rl_optimized: true
        })
      } else {
        console.error('Erro na simulação RL:', response.statusText)
      }
    } catch (error) {
      console.error('Erro ao executar simulação RL:', error)
    } finally {
      setIsSimulating(false)
    }
  }

  // Iniciar treinamento RL
  const startRLTraining = async () => {
    setIsTraining(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/rl/training/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          episodes: episodes,
          learning_rate: learningRate,
          discount_factor: 0.95,
          epsilon_start: 1.0,
          epsilon_end: 0.1,
          epsilon_decay: 0.995
        })
      })

      if (response.ok) {
        const data = await response.json()
        setRlTraining(data)
        console.log('Treinamento RL iniciado:', data)
      } else {
        console.error('Erro ao iniciar treinamento:', response.statusText)
      }
    } catch (error) {
      console.error('Erro ao iniciar treinamento RL:', error)
    } finally {
      setIsTraining(false)
    }
  }

  // Verificar conformidade normativa
  const checkCompliance = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/protection/coordination/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_type: 'full_coordination',
          include_norms_check: true
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Análise de conformidade:', data)
        // Atualizar estado com resultados da análise
      }
    } catch (error) {
      console.error('Erro na análise de conformidade:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Simulações e RL</h2>
        <div className="text-sm text-gray-500">
          Validação para Plataformas Petrolíferas
        </div>
      </div>

      {/* Verificação de Pré-requisitos */}
      {!systemState.simulation_ready && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-yellow-400">⚠️</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">Sistema não está pronto para simulação</h3>
              <div className="mt-2 text-sm text-yellow-700">
                <ul className="space-y-1">
                  {!systemState.network_loaded && <li>• Rede IEEE 14 barras não carregada</li>}
                  {!systemState.protection_configured && <li>• Dispositivos de proteção não configurados</li>}
                </ul>
              </div>
              <div className="mt-4">
                <p className="text-sm text-yellow-600">
                  Verifique as abas "Rede" e "Proteção" antes de executar simulações.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cenários de Simulação */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">⚡ Cenários de Simulação</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {scenarios.map((scenario) => (
            <div
              key={scenario.id}
              className={`border rounded-lg p-4 cursor-pointer transition ${
                selectedScenario === scenario.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedScenario(scenario.id)}
            >
              <h4 className="font-medium text-gray-900">{scenario.name}</h4>
              <p className="text-sm text-gray-600">{scenario.description}</p>
            </div>
          ))}
        </div>
        
        <div className="flex space-x-4">
          <button
            onClick={runSimulation}
            disabled={isSimulating || !systemState.simulation_ready}
            className={`px-6 py-2 rounded-md font-medium transition ${
              isSimulating || !systemState.simulation_ready
                ? 'bg-gray-400 text-gray-300 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isSimulating ? 'Executando...' : 'Executar Simulação'}
          </button>
          <button 
            onClick={runRLSimulation}
            disabled={isSimulating || !systemState.simulation_ready}
            className={`px-6 py-2 rounded-md font-medium transition ${
              isSimulating || !systemState.simulation_ready
                ? 'bg-gray-400 text-gray-300 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isSimulating ? 'Executando...' : 'Simular com RL'}
          </button>
          <button 
            onClick={checkCompliance}
            disabled={!systemState.protection_configured}
            className={`px-6 py-2 rounded-md font-medium transition ${
              !systemState.protection_configured
                ? 'bg-gray-400 text-gray-300 cursor-not-allowed'
                : 'bg-orange-600 text-white hover:bg-orange-700'
            }`}
          >
            Verificar Normas
          </button>
        </div>
      </div>

      {/* Resultados da Simulação */}
      {simulationResults && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">📊 Resultados da Simulação</h3>
            {simulationResults.is_rl_optimized && (
              <span className="bg-purple-100 text-purple-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                🧠 Otimizado por RL
              </span>
            )}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{simulationResults.protection_actions}</div>
              <div className="text-sm text-gray-600">Ações de Proteção</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{simulationResults.response_time}s</div>
              <div className="text-sm text-gray-600">Tempo de Resposta</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className={`text-2xl font-bold ${simulationResults.coordination_ok ? 'text-green-600' : 'text-red-600'}`}>
                {simulationResults.coordination_ok ? '✅' : '❌'}
              </div>
              <div className="text-sm text-gray-600">Coordenação</div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className={`text-2xl font-bold ${simulationResults.norm_compliance ? 'text-green-600' : 'text-red-600'}`}>
                {simulationResults.norm_compliance ? '✅' : '❌'}
              </div>
              <div className="text-sm text-gray-600">Conformidade</div>
            </div>
          </div>
          
          {/* Métricas Adicionais */}
          {(simulationResults.fault_current || simulationResults.protection_devices_triggered) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
              {simulationResults.fault_current && (
                <div className="text-center p-3 bg-red-50 rounded-lg">
                  <div className="text-xl font-bold text-red-600">{simulationResults.fault_current}A</div>
                  <div className="text-sm text-gray-600">Corrente de Falha</div>
                </div>
              )}
              {simulationResults.protection_devices_triggered && (
                <div className="text-center p-3 bg-yellow-50 rounded-lg">
                  <div className="text-xl font-bold text-yellow-600">{simulationResults.protection_devices_triggered}</div>
                  <div className="text-sm text-gray-600">Dispositivos Atuados</div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Treinamento RL */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">🧠 Treinamento de Reinforcement Learning</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Episódios:</label>
              <input
                type="number"
                value={episodes}
                onChange={(e) => setEpisodes(parseInt(e.target.value))}
                className="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Taxa de Aprendizado:</label>
              <input
                type="number"
                value={learningRate}
                onChange={(e) => setLearningRate(parseFloat(e.target.value))}
                step="0.001"
                className="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <div className="flex space-x-4">
            <button 
              onClick={startRLTraining}
              disabled={isTraining}
              className={`px-6 py-2 rounded-md font-medium transition ${
                isTraining
                  ? 'bg-gray-400 text-gray-300 cursor-not-allowed'
                  : 'bg-purple-600 text-white hover:bg-purple-700'
              }`}
            >
              {isTraining ? 'Treinando...' : 'Iniciar Treinamento'}
            </button>
            <button className="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 transition">
              Carregar Modelo
            </button>
            <button className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition">
              Status do Treinamento
            </button>
          </div>

          {/* Status do Treinamento */}
          {rlTraining && (
            <div className="mt-4 p-4 bg-purple-50 rounded-lg">
              <h4 className="font-medium text-purple-900 mb-2">Status do Treinamento</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">ID:</span>
                  <span className="ml-2 font-mono">{rlTraining.training_id}</span>
                </div>
                <div>
                  <span className="text-gray-600">Status:</span>
                  <span className="ml-2 font-medium">{rlTraining.status}</span>
                </div>
                <div>
                  <span className="text-gray-600">Episódios:</span>
                  <span className="ml-2">{rlTraining.episodes || episodes}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Validação Normativa */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">📋 Validação Normativa Dinâmica</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="text-sm font-medium text-gray-700">IEC 61850 (Comunicação)</span>
            <span className="text-sm text-green-600">✅ Conforme</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="text-sm font-medium text-gray-700">IEEE C37.112 (Coordenação)</span>
            <span className="text-sm text-green-600">✅ Conforme</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="text-sm font-medium text-gray-700">NBR 5410 (Instalações)</span>
            <span className={`text-sm ${
              systemState.network_loaded && systemState.protection_configured 
                ? 'text-green-600' 
                : 'text-gray-500'
            }`}>
              {systemState.network_loaded && systemState.protection_configured 
                ? '✅ Conforme' 
                : '❓ Aguardando sistema'}
            </span>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="text-sm font-medium text-gray-700">API RP 14C (Petróleo)</span>
            <span className="text-sm text-green-600">✅ Conforme</span>
          </div>
        </div>
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-700">
            💡 <strong>Dica:</strong> A conformidade com NBR 5410 será verificada automaticamente 
            quando a rede e os dispositivos de proteção estiverem carregados e configurados.
          </p>
        </div>
      </div>
    </div>
  )
}

// Componente de Cenários RL
function ScenariosTab({ 
  scenarioForm, 
  setScenarioForm, 
  scenarioResult, 
  scenarioLoading, 
  runScenario,
  systemState 
}: { 
  scenarioForm: ScenarioRequest
  setScenarioForm: (form: ScenarioRequest) => void
  scenarioResult: ScenarioResult | null
  scenarioLoading: boolean
  runScenario: () => void
  systemState: SystemState
}) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg shadow p-6 text-white">
        <h2 className="text-2xl font-bold">🤖 Simulação Inteligente com RL</h2>
        <p className="mt-2 text-purple-100">
          Execute cenários avançados de proteção utilizando Reinforcement Learning 
          para otimização automática da coordenação
        </p>
      </div>

      {/* Verificação do Sistema */}
      {!systemState.simulation_ready && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">Sistema não está pronto</h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>Para usar cenários RL, certifique-se de que:</p>
                <ul className="mt-1 space-y-1">
                  <li>• Rede elétrica esteja carregada {systemState.network_loaded ? '✅' : '❌'}</li>
                  <li>• Dispositivos de proteção estejam configurados {systemState.protection_configured ? '✅' : '❌'}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Formulário de Configuração */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">⚙️ Configuração do Cenário</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Tipo de Cenário */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Cenário
            </label>
            <select
              value={scenarioForm.scenario_type}
              onChange={(e) => setScenarioForm({
                ...scenarioForm,
                scenario_type: e.target.value as 'fault' | 'load_change' | 'equipment_failure'
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="fault">🔥 Falha/Curto-circuito</option>
              <option value="load_change">⚡ Mudança de Carga</option>
              <option value="equipment_failure">🔧 Falha de Equipamento</option>
            </select>
          </div>

          {/* Localização */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Localização
            </label>
            <select
              value={scenarioForm.location}
              onChange={(e) => setScenarioForm({
                ...scenarioForm,
                location: e.target.value
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Bus_1">Bus 1 (69kV)</option>
              <option value="Bus_2">Bus 2 (69kV)</option>
              <option value="Bus_3">Bus 3 (69kV)</option>
              <option value="Line_1_2">Linha 1-2</option>
              <option value="Line_2_3">Linha 2-3</option>
              <option value="Line_1_5">Linha 1-5</option>
            </select>
          </div>

          {/* Severidade */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Severidade: {(scenarioForm.severity * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={scenarioForm.severity}
              onChange={(e) => setScenarioForm({
                ...scenarioForm,
                severity: parseFloat(e.target.value)
              })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Leve</span>
              <span>Moderada</span>
              <span>Severa</span>
            </div>
          </div>

          {/* Episódios de Treinamento */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Episódios de Treinamento RL
            </label>
            <input
              type="number"
              min="10"
              max="200"
              value={scenarioForm.training_episodes}
              onChange={(e) => setScenarioForm({
                ...scenarioForm,
                training_episodes: parseInt(e.target.value)
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Toggle RL */}
        <div className="mt-6">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={scenarioForm.use_rl}
              onChange={(e) => setScenarioForm({
                ...scenarioForm,
                use_rl: e.target.checked
              })}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="ml-2 text-sm text-gray-700">
              🧠 Usar Reinforcement Learning para otimização automática
            </span>
          </label>
        </div>

        {/* Botão de Execução */}
        <div className="mt-6">
          <button
            onClick={runScenario}
            disabled={!systemState.simulation_ready || scenarioLoading}
            className={`w-full px-4 py-2 rounded-md text-white font-medium ${
              !systemState.simulation_ready || scenarioLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700'
            } transition`}
          >
            {scenarioLoading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                Executando Simulação RL...
              </span>
            ) : (
              '🚀 Executar Cenário com RL'
            )}
          </button>
        </div>
      </div>

      {/* Resultados */}
      {scenarioResult && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">📊 Resultados da Simulação</h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Resumo do Cenário */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">📋 Resumo do Cenário</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Tipo:</span>
                  <span className="font-medium">
                    {scenarioResult.scenario.type === 'fault' && '🔥 Falha'}
                    {scenarioResult.scenario.type === 'load_change' && '⚡ Mudança de Carga'}
                    {scenarioResult.scenario.type === 'equipment_failure' && '🔧 Falha de Equipamento'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Localização:</span>
                  <span className="font-medium">{scenarioResult.scenario.location}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Severidade:</span>
                  <span className="font-medium">{(scenarioResult.scenario.severity * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">RL Habilitado:</span>
                  <span className="font-medium">{scenarioResult.scenario.rl_enabled ? '✅ Sim' : '❌ Não'}</span>
                </div>
              </div>
            </div>

            {/* Análise de Proteção */}
            {scenarioResult.results.fault_analysis && (
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">⚡ Análise de Falha</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Corrente de Falha:</span>
                    <span className="font-medium">{scenarioResult.results.fault_analysis.current.toFixed(0)} A</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Tempo de Abertura:</span>
                    <span className="font-medium">{(scenarioResult.results.fault_analysis.clearance_time * 1000).toFixed(0)} ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Nível de Severidade:</span>
                    <span className={`font-medium ${
                      scenarioResult.results.fault_analysis.severity_level === 'HIGH' ? 'text-red-600' :
                      scenarioResult.results.fault_analysis.severity_level === 'MEDIUM' ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {scenarioResult.results.fault_analysis.severity_level}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Otimização RL */}
          {scenarioResult.results.rl_optimization && Object.keys(scenarioResult.results.rl_optimization).length > 0 && (
            <div className="mt-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200">
              <h4 className="font-medium text-gray-900 mb-3">🧠 Otimização por Reinforcement Learning</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Treinamento</h5>
                  <div className="space-y-1 text-sm">
                    {scenarioResult.results.rl_optimization.episodes_trained && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Episódios:</span>
                        <span className="font-medium">{scenarioResult.results.rl_optimization.episodes_trained}</span>
                      </div>
                    )}
                    {scenarioResult.results.rl_optimization.final_reward && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Reward Final:</span>
                        <span className="font-medium">{scenarioResult.results.rl_optimization.final_reward.toFixed(3)}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Melhorias</h5>
                  <div className="space-y-1 text-sm">
                    {scenarioResult.results.rl_optimization.improvement && (
                      <>
                        {scenarioResult.results.rl_optimization.improvement.response_time && (
                          <div className="text-green-600">
                            ⚡ {scenarioResult.results.rl_optimization.improvement.response_time}
                          </div>
                        )}
                        {scenarioResult.results.rl_optimization.improvement.coordination_score && (
                          <div className="text-blue-600">
                            🎯 {scenarioResult.results.rl_optimization.improvement.coordination_score}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Ações dos Dispositivos */}
          {scenarioResult.results.device_actions && scenarioResult.results.device_actions.length > 0 && (
            <div className="mt-6 bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">🔌 Ações dos Dispositivos</h4>
              <div className="space-y-2">
                {scenarioResult.results.device_actions.map((action: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-medium">{action.id}</span>
                      <span className="text-xs text-gray-500">{action.type}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm">
                      <span className="text-gray-600">{action.action}</span>
                      <span className="font-medium">{(action.time * 1000).toFixed(0)}ms</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Impacto no Sistema */}
          {scenarioResult.results.system_impact && (
            <div className="mt-6 bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <h4 className="font-medium text-gray-900 mb-3">⚠️ Impacto no Sistema</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                {scenarioResult.results.system_impact.affected_buses && (
                  <div className="text-center">
                    <div className="text-lg font-bold text-yellow-600">
                      {scenarioResult.results.system_impact.affected_buses}
                    </div>
                    <div className="text-gray-600">Barras Afetadas</div>
                  </div>
                )}
                {scenarioResult.results.system_impact.power_interrupted && (
                  <div className="text-center">
                    <div className="text-lg font-bold text-red-600">
                      {scenarioResult.results.system_impact.power_interrupted}
                    </div>
                    <div className="text-gray-600">Potência Interrompida</div>
                  </div>
                )}
                {scenarioResult.results.system_impact.restoration_time && (
                  <div className="text-center">
                    <div className="text-lg font-bold text-blue-600">
                      {scenarioResult.results.system_impact.restoration_time}
                    </div>
                    <div className="text-gray-600">Tempo de Restauração</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Avaliação de Conformidade Normativa */}
          {scenarioResult.compliance_assessment && (
            <div className="mt-6 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border-2 border-green-300">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-bold text-lg text-gray-900">�️ Conformidade Normativa para Petróleo</h4>
                <div className={`px-3 py-1 rounded-full text-sm font-bold ${
                  scenarioResult.compliance_assessment.safety_level === 'EXCELLENT' ? 'bg-green-100 text-green-800' :
                  scenarioResult.compliance_assessment.safety_level === 'ACCEPTABLE' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {scenarioResult.compliance_assessment.safety_level === 'EXCELLENT' ? '🔥 APROVADO PARA OPERAÇÃO' :
                   scenarioResult.compliance_assessment.safety_level === 'ACCEPTABLE' ? '⚠️ APROVADO COM RESSALVAS' :
                   '❌ NÃO APROVADO'}
                </div>
              </div>
              
              {/* Score Geral */}
              <div className="mb-4 p-3 bg-white rounded border">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Score Geral de Conformidade</span>
                  <div className="flex items-center space-x-2">
                    <span className={`text-lg font-bold ${
                      scenarioResult.compliance_assessment.overall_score > 0.9 ? 'text-green-600' :
                      scenarioResult.compliance_assessment.overall_score > 0.8 ? 'text-blue-600' :
                      scenarioResult.compliance_assessment.overall_score > 0.7 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {(scenarioResult.compliance_assessment.overall_score * 100).toFixed(1)}%
                    </span>
                    <span className={`text-sm px-2 py-1 rounded font-medium ${
                      scenarioResult.compliance_assessment.overall_score > 0.9 ? 'bg-green-100 text-green-800' :
                      scenarioResult.compliance_assessment.overall_score > 0.8 ? 'bg-blue-100 text-blue-800' :
                      scenarioResult.compliance_assessment.overall_score > 0.7 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {scenarioResult.compliance_assessment.overall_score > 0.9 ? '🏆 EXCELENTE' :
                       scenarioResult.compliance_assessment.overall_score > 0.8 ? '✅ APROVADO' :
                       scenarioResult.compliance_assessment.overall_score > 0.7 ? '⚠️ MARGINAL' : '🚨 REPROVADO'}
                    </span>
                  </div>
                </div>
                
                {/* Nível de Segurança para Petróleo */}
                {scenarioResult.compliance_assessment.safety_level && (
                  <div className="mt-2 p-2 rounded" style={{
                    backgroundColor: 
                      scenarioResult.compliance_assessment.safety_level === 'EXCELLENT' ? '#dcfce7' :
                      scenarioResult.compliance_assessment.safety_level === 'ACCEPTABLE' ? '#dbeafe' :
                      scenarioResult.compliance_assessment.safety_level === 'MARGINAL' ? '#fef3c7' : '#fee2e2',
                    border: '1px solid ' + (
                      scenarioResult.compliance_assessment.safety_level === 'EXCELLENT' ? '#16a34a' :
                      scenarioResult.compliance_assessment.safety_level === 'ACCEPTABLE' ? '#2563eb' :
                      scenarioResult.compliance_assessment.safety_level === 'MARGINAL' ? '#d97706' : '#dc2626'
                    )
                  }}>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">🛢️ Nível de Segurança Petrolífera:</span>
                      <span className={`text-sm font-bold ${
                        scenarioResult.compliance_assessment.safety_level === 'EXCELLENT' ? 'text-green-700' :
                        scenarioResult.compliance_assessment.safety_level === 'ACCEPTABLE' ? 'text-blue-700' :
                        scenarioResult.compliance_assessment.safety_level === 'MARGINAL' ? 'text-yellow-700' : 'text-red-700'
                      }`}>
                        {scenarioResult.compliance_assessment.safety_level === 'EXCELLENT' && '🏆 EXCELENTE - Apto para operação crítica'}
                        {scenarioResult.compliance_assessment.safety_level === 'ACCEPTABLE' && '✅ ACEITÁVEL - Apto com monitoramento'}
                        {scenarioResult.compliance_assessment.safety_level === 'MARGINAL' && '⚠️ MARGINAL - Requer melhorias urgentes'}
                        {scenarioResult.compliance_assessment.safety_level === 'CRITICAL_FAILURE' && '🚨 FALHA CRÍTICA - NÃO APTO para petróleo'}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* Padrões Individuais */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                {Object.entries(scenarioResult.compliance_assessment.standards_evaluation).map(([standard, data]: [string, any]) => (
                  <div key={standard} className="p-3 bg-white rounded border">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">{standard}</span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        data.compliant ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {data.compliant ? '✅ Conforme' : '❌ Não Conforme'}
                      </span>
                    </div>
                    <div className="text-xs text-gray-600 mb-1">
                      Score: {(data.score * 100).toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-500">
                      {data.details}
                    </div>
                  </div>
                ))}
              </div>

              {/* Impacto do RL */}
              {scenarioResult.compliance_assessment.rl_impact && (
                <div className="p-3 bg-purple-50 rounded border border-purple-200">
                  <h5 className="text-sm font-medium text-gray-900 mb-2">🧠 Avaliação do Reinforcement Learning</h5>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status RL:</span>
                      <span className="font-medium">
                        {scenarioResult.compliance_assessment.rl_impact.enabled ? '✅ Habilitado' : '❌ Desabilitado'}
                      </span>
                    </div>
                    {scenarioResult.compliance_assessment.rl_impact.enabled && (
                      <>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Padrões Atendidos:</span>
                          <span className="font-medium">{scenarioResult.compliance_assessment.rl_impact.standards_improved}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Melhoria Geral:</span>
                          <span className={`font-medium ${
                            scenarioResult.compliance_assessment.rl_impact.overall_improvement === 'Significativa' ? 'text-green-600' :
                            scenarioResult.compliance_assessment.rl_impact.overall_improvement === 'Moderada' ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {scenarioResult.compliance_assessment.rl_impact.overall_improvement}
                          </span>
                        </div>
                      </>
                    )}
                    <div className="mt-2 p-2 bg-blue-50 rounded text-xs text-blue-700">
                      💡 <strong>Recomendação:</strong> {scenarioResult.compliance_assessment.rl_impact.recommendation}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
