import { useState } from 'react'

interface Report {
  id: string
  name: string
  type: 'ieee_compliance' | 'fault_analysis' | 'protection_coordination' | 'rl_optimization' | 'system_overview'
  date: string
  status: 'generating' | 'ready' | 'error'
  size?: string
  pages?: number
}

export default function ReportsTab() {
  const [selectedReport, setSelectedReport] = useState<string | null>(null)
  const [reportType, setReportType] = useState<string>('all')

  const reports: Report[] = [
    {
      id: 'rpt-001',
      name: 'Relatório IEEE 14-Bus Compliance',
      type: 'ieee_compliance',
      date: '2025-07-30 14:30',
      status: 'ready',
      size: '2.4 MB',
      pages: 24
    },
    {
      id: 'rpt-002',
      name: 'Análise de Faltas Completa',
      type: 'fault_analysis',
      date: '2025-07-30 13:15',
      status: 'ready',
      size: '5.8 MB',
      pages: 47
    },
    {
      id: 'rpt-003',
      name: 'Coordenação de Proteção',
      type: 'protection_coordination',
      date: '2025-07-30 12:00',
      status: 'ready',
      size: '3.2 MB',
      pages: 31
    },
    {
      id: 'rpt-004',
      name: 'Otimização RL - Sessão 1247',
      type: 'rl_optimization',
      date: '2025-07-30 11:45',
      status: 'generating',
      size: '',
      pages: undefined
    },
    {
      id: 'rpt-005',
      name: 'Visão Geral do Sistema',
      type: 'system_overview',
      date: '2025-07-30 10:30',
      status: 'ready',
      size: '1.8 MB',
      pages: 18
    }
  ]

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'generating': return '⏳'
      case 'ready': return '✅'
      case 'error': return '❌'
      default: return '❓'
    }
  }

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'generating': return 'bg-yellow-100 text-yellow-800'
      case 'ready': return 'bg-green-100 text-green-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeIcon = (type: string) => {
    switch(type) {
      case 'ieee_compliance': return '📋'
      case 'fault_analysis': return '⚡'
      case 'protection_coordination': return '🛡️'
      case 'rl_optimization': return '🤖'
      case 'system_overview': return '📊'
      default: return '📄'
    }
  }

  const getTypeName = (type: string) => {
    switch(type) {
      case 'ieee_compliance': return 'IEEE Compliance'
      case 'fault_analysis': return 'Análise de Faltas'
      case 'protection_coordination': return 'Coordenação de Proteção'
      case 'rl_optimization': return 'Otimização RL'
      case 'system_overview': return 'Visão Geral'
      default: return 'Relatório'
    }
  }

  const filteredReports = reportType === 'all' 
    ? reports 
    : reports.filter(report => report.type === reportType)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">📊 Relatórios Técnicos</h1>
        <div className="flex space-x-3">
          <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
            ➕ Novo Relatório
          </button>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            📤 Exportar IEEE
          </button>
          <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700">
            🔄 Atualizar Lista
          </button>
        </div>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Relatórios Prontos</p>
              <p className="text-3xl font-bold text-green-600">
                {reports.filter(r => r.status === 'ready').length}
              </p>
            </div>
            <div className="text-4xl">✅</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Gerando</p>
              <p className="text-3xl font-bold text-yellow-600">
                {reports.filter(r => r.status === 'generating').length}
              </p>
            </div>
            <div className="text-4xl">⏳</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total de Páginas</p>
              <p className="text-3xl font-bold text-blue-600">
                {reports.filter(r => r.pages).reduce((acc, r) => acc + (r.pages || 0), 0)}
              </p>
            </div>
            <div className="text-4xl">📄</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Tamanho Total</p>
              <p className="text-3xl font-bold text-purple-600">13.2</p>
              <p className="text-xs text-gray-500">MB</p>
            </div>
            <div className="text-4xl">💾</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lista de Relatórios */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold">📋 Relatórios Disponíveis</h3>
            <select 
              value={reportType} 
              onChange={(e) => setReportType(e.target.value)}
              className="px-3 py-2 border rounded-lg"
            >
              <option value="all">Todos</option>
              <option value="ieee_compliance">IEEE Compliance</option>
              <option value="fault_analysis">Análise de Faltas</option>
              <option value="protection_coordination">Coordenação</option>
              <option value="rl_optimization">Otimização RL</option>
              <option value="system_overview">Visão Geral</option>
            </select>
          </div>

          <div className="space-y-3">
            {filteredReports.map(report => (
              <div 
                key={report.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  selectedReport === report.id 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedReport(report.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">{getTypeIcon(report.type)}</div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{report.name}</h4>
                      <p className="text-sm text-gray-600">{getTypeName(report.type)}</p>
                      <p className="text-xs text-gray-500">{report.date}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(report.status)}`}>
                      {getStatusIcon(report.status)} {report.status}
                    </span>
                    {report.status === 'ready' && (
                      <button className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700">
                        📥 Download
                      </button>
                    )}
                  </div>
                </div>
                
                {report.status === 'ready' && (
                  <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-gray-50 p-2 rounded">
                      <span className="text-gray-600">Tamanho:</span>
                      <span className="font-semibold ml-1">{report.size}</span>
                    </div>
                    <div className="bg-gray-50 p-2 rounded">
                      <span className="text-gray-600">Páginas:</span>
                      <span className="font-semibold ml-1">{report.pages}</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Detalhes do Relatório */}
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-xl font-semibold mb-4">📄 Detalhes</h3>
          
          {selectedReport ? (
            <>
              {(() => {
                const report = reports.find(r => r.id === selectedReport)!
                return (
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-lg">{report.name}</h4>
                      <p className="text-gray-600">{getTypeName(report.type)}</p>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(report.status)}`}>
                        {getStatusIcon(report.status)} {report.status}
                      </span>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Data:</span>
                        <span className="font-semibold">{report.date}</span>
                      </div>
                      
                      {report.size && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Tamanho:</span>
                          <span className="font-semibold">{report.size}</span>
                        </div>
                      )}
                      
                      {report.pages && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Páginas:</span>
                          <span className="font-semibold">{report.pages}</span>
                        </div>
                      )}
                    </div>

                    <div className="pt-4 border-t">
                      <h5 className="font-semibold mb-2">Conteúdo:</h5>
                      <div className="text-sm text-gray-600 space-y-1">
                        {report.type === 'ieee_compliance' && (
                          <>
                            <p>• Verificação de conformidade IEEE</p>
                            <p>• Análise de parâmetros do sistema</p>
                            <p>• Recomendações de adequação</p>
                          </>
                        )}
                        {report.type === 'fault_analysis' && (
                          <>
                            <p>• Análise de correntes de falta</p>
                            <p>• Perfis de tensão durante faltas</p>
                            <p>• Tempo de atuação da proteção</p>
                          </>
                        )}
                        {report.type === 'protection_coordination' && (
                          <>
                            <p>• Curvas de coordenação</p>
                            <p>• Análise de seletividade</p>
                            <p>• Recomendações de ajustes</p>
                          </>
                        )}
                        {report.type === 'rl_optimization' && (
                          <>
                            <p>• Resultados do treinamento RL</p>
                            <p>• Política neural otimizada</p>
                            <p>• Métricas de performance</p>
                          </>
                        )}
                        {report.type === 'system_overview' && (
                          <>
                            <p>• Estado geral do sistema</p>
                            <p>• Indicadores de performance</p>
                            <p>• Resumo executivo</p>
                          </>
                        )}
                      </div>
                    </div>

                    <div className="pt-4 border-t">
                      <h5 className="font-semibold mb-2">Ações:</h5>
                      <div className="space-y-2">
                        {report.status === 'ready' && (
                          <>
                            <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                              📥 Download PDF
                            </button>
                            <button className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700">
                              👁️ Visualizar
                            </button>
                            <button className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700">
                              📤 Compartilhar
                            </button>
                          </>
                        )}
                        {report.status === 'generating' && (
                          <div className="text-center py-4">
                            <div className="animate-spin text-2xl mb-2">⏳</div>
                            <p className="text-gray-600">Gerando relatório...</p>
                          </div>
                        )}
                        <button className="w-full bg-red-600 text-white py-2 rounded-lg hover:bg-red-700">
                          🗑️ Excluir
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })()}
            </>
          ) : (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">📋</div>
              <p className="text-gray-500">Selecione um relatório para ver detalhes</p>
            </div>
          )}
        </div>
      </div>

      {/* Templates de Relatórios */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h3 className="text-xl font-semibold mb-4">📝 Templates Disponíveis</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div className="p-4 border border-dashed border-gray-300 rounded-lg text-center hover:border-blue-500 cursor-pointer">
            <div className="text-3xl mb-2">📋</div>
            <h4 className="font-semibold">IEEE Compliance</h4>
            <p className="text-sm text-gray-600">Relatório de conformidade</p>
          </div>
          
          <div className="p-4 border border-dashed border-gray-300 rounded-lg text-center hover:border-blue-500 cursor-pointer">
            <div className="text-3xl mb-2">⚡</div>
            <h4 className="font-semibold">Análise de Faltas</h4>
            <p className="text-sm text-gray-600">Relatório técnico detalhado</p>
          </div>
          
          <div className="p-4 border border-dashed border-gray-300 rounded-lg text-center hover:border-blue-500 cursor-pointer">
            <div className="text-3xl mb-2">🛡️</div>
            <h4 className="font-semibold">Coordenação</h4>
            <p className="text-sm text-gray-600">Proteção e seletividade</p>
          </div>
          
          <div className="p-4 border border-dashed border-gray-300 rounded-lg text-center hover:border-blue-500 cursor-pointer">
            <div className="text-3xl mb-2">🤖</div>
            <h4 className="font-semibold">RL Optimization</h4>
            <p className="text-sm text-gray-600">Resultados de IA</p>
          </div>
          
          <div className="p-4 border border-dashed border-gray-300 rounded-lg text-center hover:border-blue-500 cursor-pointer">
            <div className="text-3xl mb-2">📊</div>
            <h4 className="font-semibold">Executivo</h4>
            <p className="text-sm text-gray-600">Resumo gerencial</p>
          </div>
        </div>
      </div>

      {/* Configurações de Exportação */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl shadow-lg border">
        <h3 className="text-xl font-semibold mb-4 text-blue-800">⚙️ Configurações de Exportação</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg">
            <h4 className="font-semibold text-blue-700">Formato Padrão</h4>
            <select className="w-full mt-2 p-2 border rounded">
              <option>PDF (Recomendado)</option>
              <option>Word (.docx)</option>
              <option>Excel (.xlsx)</option>
              <option>PowerPoint (.pptx)</option>
            </select>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <h4 className="font-semibold text-blue-700">Qualidade</h4>
            <select className="w-full mt-2 p-2 border rounded">
              <option>Alta (Recomendado)</option>
              <option>Média</option>
              <option>Comprimido</option>
            </select>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <h4 className="font-semibold text-blue-700">Marca d'água</h4>
            <div className="mt-2">
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" defaultChecked />
                <span className="text-sm">Incluir marca Petrobras</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
