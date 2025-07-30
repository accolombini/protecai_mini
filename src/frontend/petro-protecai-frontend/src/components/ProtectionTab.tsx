import { useState } from 'react'

interface ProtectionDevice {
  id: string
  type: 'relay' | 'breaker' | 'fuse'
  name: string
  bus: number
  status: 'active' | 'standby' | 'fault' | 'maintenance'
  settings: {
    pickup?: number
    time_delay?: number
    curve_type?: string
  }
  last_operation?: string
}

export default function ProtectionTab() {
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null)
  const [filterType, setFilterType] = useState<'all' | 'relay' | 'breaker' | 'fuse'>('all')

  const devices: ProtectionDevice[] = [
    {
      id: 'R-01A',
      type: 'relay',
      name: 'Relé Principal Bus 1',
      bus: 1,
      status: 'active',
      settings: { pickup: 1250, time_delay: 0.1, curve_type: 'IEC Normal Inverse' },
      last_operation: '2025-07-29 14:30'
    },
    {
      id: 'R-01B',
      type: 'relay',
      name: 'Relé Backup Bus 1',
      bus: 1,
      status: 'standby',
      settings: { pickup: 1000, time_delay: 0.3, curve_type: 'IEC Very Inverse' }
    },
    {
      id: 'CB-01',
      type: 'breaker',
      name: 'Disjuntor Bus 1',
      bus: 1,
      status: 'active',
      settings: {},
      last_operation: '2025-07-29 14:30'
    },
    {
      id: 'R-02A',
      type: 'relay',
      name: 'Relé Principal Bus 2',
      bus: 2,
      status: 'active',
      settings: { pickup: 800, time_delay: 0.15, curve_type: 'IEEE Moderate Inverse' }
    },
    {
      id: 'R-02B',
      type: 'relay',
      name: 'Relé Backup Bus 2',
      bus: 2,
      status: 'maintenance',
      settings: { pickup: 650, time_delay: 0.4, curve_type: 'IEC Very Inverse' }
    },
    {
      id: 'F-12',
      type: 'fuse',
      name: 'Fusível Linha 1-2',
      bus: 12,
      status: 'fault',
      settings: { pickup: 500 },
      last_operation: '2025-07-30 09:15'
    }
  ]

  const filteredDevices = filterType === 'all' 
    ? devices 
    : devices.filter(device => device.type === filterType)

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'active': return '✅'
      case 'standby': return '⏸️'
      case 'fault': return '❌'
      case 'maintenance': return '🔧'
      default: return '❓'
    }
  }

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'standby': return 'bg-blue-100 text-blue-800'
      case 'fault': return 'bg-red-100 text-red-800'
      case 'maintenance': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeIcon = (type: string) => {
    switch(type) {
      case 'relay': return '🔄'
      case 'breaker': return '⚡'
      case 'fuse': return '🔒'
      default: return '❓'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">🛡️ Sistema de Proteção Elétrica</h1>
        <div className="flex space-x-3">
          <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
            ➕ Novo Relé
          </button>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            🔄 Coordenação
          </button>
          <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700">
            📊 Curvas de Atuação
          </button>
        </div>
      </div>

      {/* Estatísticas Rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Dispositivos Ativos</p>
              <p className="text-3xl font-bold text-green-600">
                {devices.filter(d => d.status === 'active').length}
              </p>
            </div>
            <div className="text-4xl">✅</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Em Standby</p>
              <p className="text-3xl font-bold text-blue-600">
                {devices.filter(d => d.status === 'standby').length}
              </p>
            </div>
            <div className="text-4xl">⏸️</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-red-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Com Falha</p>
              <p className="text-3xl font-bold text-red-600">
                {devices.filter(d => d.status === 'fault').length}
              </p>
            </div>
            <div className="text-4xl">❌</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Manutenção</p>
              <p className="text-3xl font-bold text-yellow-600">
                {devices.filter(d => d.status === 'maintenance').length}
              </p>
            </div>
            <div className="text-4xl">🔧</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lista de Dispositivos */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold">🛡️ Dispositivos de Proteção</h3>
            <select 
              value={filterType} 
              onChange={(e) => setFilterType(e.target.value as any)}
              className="px-3 py-2 border rounded-lg"
            >
              <option value="all">Todos</option>
              <option value="relay">Relés</option>
              <option value="breaker">Disjuntores</option>
              <option value="fuse">Fusíveis</option>
            </select>
          </div>

          <div className="space-y-3">
            {filteredDevices.map(device => (
              <div 
                key={device.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  selectedDevice === device.id 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedDevice(device.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">{getTypeIcon(device.type)}</div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{device.name}</h4>
                      <p className="text-sm text-gray-600">ID: {device.id} | Bus {device.bus}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(device.status)}`}>
                      {getStatusIcon(device.status)} {device.status}
                    </span>
                  </div>
                </div>
                
                {device.last_operation && (
                  <p className="text-xs text-gray-500 mt-2">
                    Última operação: {device.last_operation}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Detalhes do Dispositivo Selecionado */}
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-xl font-semibold mb-4">🔧 Configurações</h3>
          
          {selectedDevice ? (
            <>
              {(() => {
                const device = devices.find(d => d.id === selectedDevice)!
                return (
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-lg">{device.name}</h4>
                      <p className="text-gray-600">ID: {device.id}</p>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(device.status)}`}>
                        {getStatusIcon(device.status)} {device.status}
                      </span>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tipo:</span>
                        <span className="font-semibold capitalize">{device.type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Barra:</span>
                        <span className="font-semibold">Bus {device.bus}</span>
                      </div>
                      
                      {device.settings.pickup && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Pickup (A):</span>
                          <span className="font-semibold">{device.settings.pickup}</span>
                        </div>
                      )}
                      
                      {device.settings.time_delay && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Time Delay (s):</span>
                          <span className="font-semibold">{device.settings.time_delay}</span>
                        </div>
                      )}
                      
                      {device.settings.curve_type && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Curva:</span>
                          <span className="font-semibold text-sm">{device.settings.curve_type}</span>
                        </div>
                      )}
                    </div>

                    <div className="pt-4 border-t">
                      <h5 className="font-semibold mb-2">Ações:</h5>
                      <div className="space-y-2">
                        <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                          ⚙️ Configurar
                        </button>
                        <button className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700">
                          🧪 Testar
                        </button>
                        <button className="w-full bg-yellow-600 text-white py-2 rounded-lg hover:bg-yellow-700">
                          🔧 Manutenção
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })()}
            </>
          ) : (
            <p className="text-gray-500 text-center py-8">
              Selecione um dispositivo para ver detalhes
            </p>
          )}
        </div>
      </div>

      {/* Gráfico de Coordenação */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h3 className="text-xl font-semibold mb-4">📈 Curvas de Coordenação</h3>
        <div className="bg-gray-50 rounded-lg p-8 h-64 flex items-center justify-center">
          <div className="text-center text-gray-500">
            <div className="text-4xl mb-2">📊</div>
            <p>Gráfico de coordenação de proteção será exibido aqui</p>
            <p className="text-sm">Tempo vs Corrente para análise de seletividade</p>
          </div>
        </div>
      </div>

      {/* Alertas de Coordenação */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h3 className="text-xl font-semibold mb-4">⚠️ Alertas de Coordenação</h3>
        <div className="space-y-3">
          <div className="p-3 bg-yellow-50 border-l-4 border-yellow-400 rounded-lg">
            <p className="font-medium text-yellow-800">Possível perda de coordenação</p>
            <p className="text-sm text-yellow-700">Relés R-02A e R-02B podem ter sobreposição de atuação</p>
          </div>
          <div className="p-3 bg-red-50 border-l-4 border-red-400 rounded-lg">
            <p className="font-medium text-red-800">Dispositivo em falha</p>
            <p className="text-sm text-red-700">Fusível F-12 precisa ser substituído</p>
          </div>
          <div className="p-3 bg-blue-50 border-l-4 border-blue-400 rounded-lg">
            <p className="font-medium text-blue-800">Otimização sugerida</p>
            <p className="text-sm text-blue-700">RL sugere ajuste nos tempos de R-01A para melhor coordenação</p>
          </div>
        </div>
      </div>
    </div>
  )
}
