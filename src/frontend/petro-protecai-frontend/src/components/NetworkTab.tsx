import { useState } from 'react'

interface BusData {
  id: number
  name: string
  voltage: number
  angle: number
  load_p: number
  load_q: number
  status: 'normal' | 'warning' | 'fault'
}

export default function NetworkTab() {
  const [selectedBus, setSelectedBus] = useState<number | null>(null)

  const busData: BusData[] = [
    { id: 1, name: 'Bus 1 (Slack)', voltage: 1.06, angle: 0, load_p: 0, load_q: 0, status: 'normal' },
    { id: 2, name: 'Bus 2 (Gen)', voltage: 1.045, angle: -4.98, load_p: 21.7, load_q: 12.7, status: 'normal' },
    { id: 3, name: 'Bus 3 (Gen)', voltage: 1.01, angle: -12.72, load_p: 94.2, load_q: 19.0, status: 'normal' },
    { id: 4, name: 'Bus 4', voltage: 1.019, angle: -10.33, load_p: 47.8, load_q: -3.9, status: 'normal' },
    { id: 5, name: 'Bus 5', voltage: 1.020, angle: -8.78, load_p: 7.6, load_q: 1.6, status: 'normal' },
    { id: 6, name: 'Bus 6 (Gen)', voltage: 1.07, angle: -14.22, load_p: 11.2, load_q: 7.5, status: 'warning' },
    { id: 7, name: 'Bus 7', voltage: 1.062, angle: -13.37, load_p: 0, load_q: 0, status: 'normal' },
    { id: 8, name: 'Bus 8 (Gen)', voltage: 1.09, angle: -13.36, load_p: 0, load_q: 0, status: 'normal' },
    { id: 9, name: 'Bus 9', voltage: 1.056, angle: -14.94, load_p: 29.5, load_q: 16.6, status: 'normal' },
    { id: 10, name: 'Bus 10', voltage: 1.051, angle: -15.10, load_p: 9.0, load_q: 5.8, status: 'normal' },
    { id: 11, name: 'Bus 11', voltage: 1.057, angle: -14.79, load_p: 3.5, load_q: 1.8, status: 'normal' },
    { id: 12, name: 'Bus 12', voltage: 1.055, angle: -15.07, load_p: 6.1, load_q: 1.6, status: 'normal' },
    { id: 13, name: 'Bus 13', voltage: 1.050, angle: -15.16, load_p: 13.5, load_q: 5.8, status: 'normal' },
    { id: 14, name: 'Bus 14', voltage: 1.036, angle: -16.04, load_p: 14.9, load_q: 5.0, status: 'normal' }
  ]

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'normal': return 'bg-green-500'
      case 'warning': return 'bg-yellow-500'
      case 'fault': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
            {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">⚡ Sistema Elétrico IEEE 14-Bus</h1>
        <div className="flex space-x-3">
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            🔄 Executar Load Flow
          </button>
          <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
            📊 Análise de Estabilidade
          </button>
          <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700">
            ⚡ Simular Falta
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Diagrama da Rede */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-lg">
                    <h3 className="text-xl font-semibold mb-4">📊 Análise Elétrica das Barras</h3>
          
          {/* SVG Diagram Placeholder - Simplified IEEE 14-bus */}
          <div className="relative bg-gray-50 rounded-lg p-4 h-96 overflow-hidden">
            <svg viewBox="0 0 800 600" className="w-full h-full">
              {/* Linhas de Transmissão */}
              <g stroke="#374151" strokeWidth="2" fill="none">
                <line x1="100" y1="100" x2="200" y2="100" />
                <line x1="200" y1="100" x2="300" y2="100" />
                <line x1="300" y1="100" x2="400" y2="100" />
                <line x1="100" y1="100" x2="100" y2="200" />
                <line x1="200" y1="100" x2="200" y2="200" />
                <line x1="300" y1="100" x2="300" y2="200" />
                <line x1="400" y1="100" x2="400" y2="200" />
                <line x1="100" y1="200" x2="200" y2="200" />
                <line x1="200" y1="200" x2="300" y2="200" />
                <line x1="300" y1="200" x2="400" y2="200" />
                <line x1="100" y1="200" x2="100" y2="300" />
                <line x1="200" y1="200" x2="200" y2="300" />
                <line x1="300" y1="200" x2="300" y2="300" />
                <line x1="400" y1="200" x2="400" y2="300" />
              </g>

              {/* Barras (Buses) */}
              {busData.slice(0, 14).map((bus, index) => {
                const x = 100 + (index % 4) * 100
                const y = 100 + Math.floor(index / 4) * 100
                return (
                  <g key={bus.id}>
                    <circle
                      cx={x}
                      cy={y}
                      r="20"
                      className={`${getStatusColor(bus.status)} cursor-pointer hover:opacity-80 transition-opacity`}
                      onClick={() => setSelectedBus(bus.id)}
                    />
                    <text
                      x={x}
                      y={y + 5}
                      textAnchor="middle"
                      className="text-white text-sm font-bold"
                    >
                      {bus.id}
                    </text>
                    <text
                      x={x}
                      y={y + 35}
                      textAnchor="middle"
                      className="text-xs text-gray-600"
                    >
                      {bus.voltage.toFixed(2)}pu
                    </text>
                  </g>
                )
              })}

              {/* Geradores */}
              <g fill="#10B981">
                <rect x="85" y="85" width="30" height="15" rx="3" />
                <rect x="185" y="85" width="30" height="15" rx="3" />
                <rect x="285" y="85" width="30" height="15" rx="3" />
                <rect x="385" y="185" width="30" height="15" rx="3" />
                <rect x="385" y="285" width="30" height="15" rx="3" />
              </g>

              {/* Cargas */}
              <g fill="#EF4444">
                {busData.filter(bus => bus.load_p > 0).map((bus) => {
                  const x = 100 + (busData.indexOf(bus) % 4) * 100
                  const y = 100 + Math.floor(busData.indexOf(bus) / 4) * 100
                  return (
                    <polygon
                      key={bus.id}
                      points={`${x-8},${y+25} ${x+8},${y+25} ${x},${y+35}`}
                    />
                  )
                })}
              </g>
            </svg>
          </div>

          {/* Legenda */}
          <div className="flex justify-center mt-4 space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-500 rounded-full"></div>
              <span>Normal</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
              <span>Atenção</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-500 rounded-full"></div>
              <span>Falha</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-600 rounded"></div>
              <span>Gerador</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-0 h-0 border-l-4 border-r-4 border-b-4 border-l-transparent border-r-transparent border-b-red-500"></div>
              <span>Carga</span>
            </div>
          </div>
        </div>

        {/* Informações da Barra Selecionada */}
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-xl font-semibold mb-4">📊 Informações da Barra</h3>
          
          {selectedBus ? (
            <>
              {(() => {
                const bus = busData.find(b => b.id === selectedBus)!
                return (
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-lg">{bus.name}</h4>
                      <span className={`px-2 py-1 rounded text-sm font-medium ${
                        bus.status === 'normal' ? 'bg-green-100 text-green-800' :
                        bus.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {bus.status === 'normal' ? 'Normal' : 
                         bus.status === 'warning' ? 'Atenção' : 'Falha'}
                      </span>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tensão:</span>
                        <span className="font-semibold">{bus.voltage.toFixed(3)} pu</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Ângulo:</span>
                        <span className="font-semibold">{bus.angle.toFixed(2)}°</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Carga P:</span>
                        <span className="font-semibold">{bus.load_p.toFixed(1)} MW</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Carga Q:</span>
                        <span className="font-semibold">{bus.load_q.toFixed(1)} MVAr</span>
                      </div>
                    </div>

                    <div className="pt-4 border-t">
                      <h5 className="font-semibold mb-2">Dispositivos de Proteção:</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Relé Principal:</span>
                          <span className="text-green-600">R-{bus.id}A ✅</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Relé Backup:</span>
                          <span className="text-green-600">R-{bus.id}B ✅</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Disjuntor:</span>
                          <span className="text-green-600">CB-{bus.id} ✅</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })()}
            </>
          ) : (
            <p className="text-gray-500 text-center py-8">
              Selecione uma barra no diagrama para ver detalhes
            </p>
          )}
        </div>
      </div>

      {/* Tabela de Status das Barras */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h3 className="text-xl font-semibold mb-4">📋 Status Geral das Barras</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Barra</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tensão (pu)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ângulo (°)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Carga P (MW)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Carga Q (MVAr)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {busData.map((bus) => (
                <tr key={bus.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {bus.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {bus.voltage.toFixed(3)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {bus.angle.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {bus.load_p.toFixed(1)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {bus.load_q.toFixed(1)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      bus.status === 'normal' ? 'bg-green-100 text-green-800' :
                      bus.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {bus.status === 'normal' ? 'Normal' : 
                       bus.status === 'warning' ? 'Atenção' : 'Falha'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
