import { useState } from 'react';

interface BusPosition {
  x: number;
  y: number;
}

interface BusPositions {
  [key: number]: BusPosition;
}

interface Connection {
  from: number;
  to: number;
}

// Componente para representar o Sistema IEEE 14-Bus real
const IEEE14BusSystem = () => {
  const [selectedBus, setSelectedBus] = useState<number | null>(null);

  // Configuração real do IEEE 14-Bus baseada na documentação
  const busConfiguration = {
    // Zona Z1 - Transformador TR1 (25 MVA)
    zone_z1: {
      transformer: "TR1 (25 MVA, 13.8 kV)",
      buses: [0, 4, 5, 6, 7, 9],
      devices: [
        { id: "87T-TR1", type: "87T", location: "Transformador TR1", pickup: 0.3, time_delay: 0.02 },
        { id: "50/51-L4-5", type: "50/51", location: "Linha Bus4-Bus5", pickup: 1.3, time_delay: 0.4 },
        { id: "67-B4", type: "67", location: "Bus 4", pickup: 1.2, time_delay: 0.35 },
        { id: "27/59-B7", type: "27/59", location: "Bus 7", pickup: 0.9, time_delay: 1.2 }
      ]
    },
    // Zona Z2 - Transformador TR2 (25 MVA)  
    zone_z2: {
      transformer: "TR2 (25 MVA, 13.8 kV)",
      buses: [1, 5, 8, 10, 11, 12, 13, 14],
      devices: [
        { id: "87T-TR2", type: "87T", location: "Transformador TR2", pickup: 0.3, time_delay: 0.02 },
        { id: "50/51-L5-6", type: "50/51", location: "Linha Bus5-Bus6", pickup: 1.4, time_delay: 0.5 },
        { id: "67-B5", type: "67", location: "Bus 5", pickup: 1.3, time_delay: 0.45 },
        { id: "27/59-B14", type: "27/59", location: "Bus 14", pickup: 1.0, time_delay: 1.4 }
      ]
    }
  };

  // Posições das barras no diagrama IEEE 14-Bus
  const busPositions: BusPositions = {
    1: { x: 100, y: 50 },   // Gerador Slack
    2: { x: 300, y: 50 },   // Gerador PV
    3: { x: 500, y: 50 },   // Gerador PV
    4: { x: 200, y: 150 },  // Barra de carga
    5: { x: 400, y: 150 },  // Barra de carga
    6: { x: 600, y: 150 },  // Barra de carga
    7: { x: 150, y: 250 },  // Barra de carga
    8: { x: 300, y: 250 },  // Barra de carga
    9: { x: 450, y: 250 },  // Barra de carga
    10: { x: 550, y: 250 }, // Barra de carga
    11: { x: 650, y: 250 }, // Barra de carga
    12: { x: 700, y: 200 }, // Barra de carga
    13: { x: 750, y: 150 }, // Barra de carga
    14: { x: 550, y: 350 }  // Barra de carga
  };

  // Conexões entre barras (linhas de transmissão)
  const connections: Connection[] = [
    { from: 1, to: 2 }, { from: 1, to: 5 }, { from: 2, to: 3 }, { from: 2, to: 4 },
    { from: 2, to: 5 }, { from: 3, to: 4 }, { from: 4, to: 5 }, { from: 4, to: 7 },
    { from: 4, to: 9 }, { from: 5, to: 6 }, { from: 6, to: 11 }, { from: 6, to: 12 },
    { from: 6, to: 13 }, { from: 7, to: 8 }, { from: 7, to: 9 }, { from: 9, to: 10 },
    { from: 9, to: 14 }, { from: 10, to: 11 }, { from: 12, to: 13 }, { from: 13, to: 14 }
  ];

  const getBusColor = (busNumber: number): string => {
    if (busConfiguration.zone_z1.buses.includes(busNumber - 1)) {
      return '#3B82F6'; // Azul para Z1
    } else if (busConfiguration.zone_z2.buses.includes(busNumber - 1)) {
      return '#EF4444'; // Vermelho para Z2
    }
    return '#10B981'; // Verde para geradores
  };

  const getBusType = (busNumber: number): string => {
    if ([1, 2, 3].includes(busNumber)) return 'GER';
    return 'LOAD';
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-xl border border-gray-200 hover:shadow-2xl transition-shadow duration-300">
      <div className="mb-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-xl border-2 border-blue-200 hover:border-blue-300 transition-colors">
            <h3 className="font-bold text-blue-900 mb-3 text-lg">🔵 Zona Z1 - Transformador TR1</h3>
            <div className="space-y-2 text-sm">
              <p className="text-blue-800"><strong>Potência:</strong> 25 MVA | <strong>Tensão:</strong> 13.8 kV</p>
              <p className="text-blue-700"><strong>Barras:</strong> 1, 5, 6, 7, 8, 10</p>
              <div className="mt-3">
                <p className="text-blue-900 font-semibold mb-1">Dispositivos de Proteção:</p>
                <div className="grid grid-cols-2 gap-1 text-xs">
                  <span className="bg-blue-200 px-2 py-1 rounded">87T-TR1</span>
                  <span className="bg-blue-200 px-2 py-1 rounded">50/51-L4-5</span>
                  <span className="bg-blue-200 px-2 py-1 rounded">67-B4</span>
                  <span className="bg-blue-200 px-2 py-1 rounded">27/59-B7</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-gradient-to-r from-red-50 to-red-100 p-6 rounded-xl border-2 border-red-200 hover:border-red-300 transition-colors">
            <h3 className="font-bold text-red-900 mb-3 text-lg">🔴 Zona Z2 - Transformador TR2</h3>
            <div className="space-y-2 text-sm">
              <p className="text-red-800"><strong>Potência:</strong> 25 MVA | <strong>Tensão:</strong> 13.8 kV</p>
              <p className="text-red-700"><strong>Barras:</strong> 2, 6, 9, 11, 12, 13, 14, 15</p>
              <div className="mt-3">
                <p className="text-red-900 font-semibold mb-1">Dispositivos de Proteção:</p>
                <div className="grid grid-cols-2 gap-1 text-xs">
                  <span className="bg-red-200 px-2 py-1 rounded">87T-TR2</span>
                  <span className="bg-red-200 px-2 py-1 rounded">50/51-L5-6</span>
                  <span className="bg-red-200 px-2 py-1 rounded">67-B5</span>
                  <span className="bg-red-200 px-2 py-1 rounded">27/59-B14</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* SVG do Sistema IEEE 14-Bus */}
      <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-xl border-2 border-gray-200 hover:border-gray-300 transition-all duration-300">
        <div className="mb-4 text-center">
          <h3 className="text-xl font-bold text-gray-900 mb-2">⚡ Diagrama Unifilar IEEE 14-Bus</h3>
          <p className="text-gray-600 text-sm">Sistema de 14 barras com 2 zonas de proteção coordenadas por RL</p>
        </div>
        
        <div className="overflow-x-auto">
          <svg width="900" height="500" viewBox="0 0 900 500" className="w-full h-auto min-w-[800px]">
            {/* Fundo com grid */}
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e5e7eb" strokeWidth="0.5"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
            
            {/* Desenhar conexões (linhas) com animação */}
            {connections.map((conn, idx) => {
              const fromPos = busPositions[conn.from];
              const toPos = busPositions[conn.to];
              return (
                <g key={idx}>
                  <line
                    x1={fromPos.x}
                    y1={fromPos.y}
                    x2={toPos.x}
                    y2={toPos.y}
                    stroke="#6B7280"
                    strokeWidth="3"
                    className="opacity-70 hover:opacity-100 transition-opacity cursor-pointer"
                  />
                  <line
                    x1={fromPos.x}
                    y1={fromPos.y}
                    x2={toPos.x}
                    y2={toPos.y}
                    stroke="#3B82F6"
                    strokeWidth="1"
                    className="opacity-30"
                    strokeDasharray="5,5"
                  >
                    <animate attributeName="stroke-dashoffset" values="0;10" dur="2s" repeatCount="indefinite"/>
                  </line>
                </g>
              );
            })}

            {/* Desenhar barras com efeitos */}
            {Object.entries(busPositions).map(([busNum, pos]) => (
              <g key={busNum} className="cursor-pointer hover:opacity-90 transition-all duration-200">
                {/* Círculo de fundo com glow */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="20"
                  fill={getBusColor(parseInt(busNum))}
                  opacity="0.2"
                  className="animate-pulse"
                />
                
                {/* Círculo principal */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="18"
                  fill={getBusColor(parseInt(busNum))}
                  stroke="#1F2937"
                  strokeWidth="2"
                  onClick={() => setSelectedBus(parseInt(busNum))}
                  className="drop-shadow-lg hover:drop-shadow-xl transition-all duration-200"
                />
                
                {/* Número da barra */}
                <text
                  x={pos.x}
                  y={pos.y + 6}
                  textAnchor="middle"
                  className="fill-white text-sm font-bold pointer-events-none drop-shadow-sm"
                >
                  {busNum}
                </text>
                
                {/* Tipo da barra */}
                <text
                  x={pos.x}
                  y={pos.y - 30}
                  textAnchor="middle"
                  className="fill-gray-800 text-xs font-bold drop-shadow-sm"
                >
                  {getBusType(parseInt(busNum))}
                </text>
                
                {/* Voltagem (se selecionada) */}
                {selectedBus === parseInt(busNum) && (
                  <text
                    x={pos.x}
                    y={pos.y + 35}
                    textAnchor="middle"
                    className="fill-green-600 text-xs font-semibold animate-pulse"
                  >
                    1.05 pu
                  </text>
                )}
              </g>
            ))}

            {/* Indicar Transformadores com melhor design */}
            <g>
              {/* TR1 */}
              <rect x="170" y="110" width="60" height="30" rx="5" fill="#3B82F6" stroke="#1E40AF" strokeWidth="2" className="drop-shadow-lg" />
              <text x="200" y="130" textAnchor="middle" className="fill-white text-sm font-bold">TR1</text>
              <text x="200" y="100" textAnchor="middle" className="fill-blue-900 text-sm font-bold">25 MVA</text>
              
              {/* TR2 */}
              <rect x="370" y="110" width="60" height="30" rx="5" fill="#EF4444" stroke="#DC2626" strokeWidth="2" className="drop-shadow-lg" />
              <text x="400" y="130" textAnchor="middle" className="fill-white text-sm font-bold">TR2</text>
              <text x="400" y="100" textAnchor="middle" className="fill-red-900 text-sm font-bold">25 MVA</text>
            </g>
            
            {/* Indicadores de Zona */}
            <g>
              <rect x="50" y="20" width="350" height="280" fill="none" stroke="#3B82F6" strokeWidth="3" strokeDasharray="10,5" opacity="0.5" rx="10"/>
              <text x="60" y="40" className="fill-blue-600 text-lg font-bold">ZONA Z1</text>
              
              <rect x="320" y="20" width="400" height="280" fill="none" stroke="#EF4444" strokeWidth="3" strokeDasharray="10,5" opacity="0.5" rx="10"/>
              <text x="330" y="40" className="fill-red-600 text-lg font-bold">ZONA Z2</text>
            </g>
          </svg>
        </div>
      </div>

      {/* Legenda Profissional */}
      <div className="mt-6 bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-xl border border-gray-200">
        <h4 className="font-semibold text-gray-900 mb-3 text-center">🏷️ Legenda do Sistema</h4>
        <div className="flex justify-center space-x-8 flex-wrap gap-4">
          <div className="flex items-center space-x-3 bg-white px-4 py-2 rounded-lg shadow-sm">
            <div className="w-6 h-6 bg-green-500 rounded-full shadow-md"></div>
            <span className="text-sm font-medium text-gray-700">Geradores (Slack + PV)</span>
          </div>
          <div className="flex items-center space-x-3 bg-white px-4 py-2 rounded-lg shadow-sm">
            <div className="w-6 h-6 bg-blue-500 rounded-full shadow-md"></div>
            <span className="text-sm font-medium text-gray-700">Zona Z1 (TR1 - 25 MVA)</span>
          </div>
          <div className="flex items-center space-x-3 bg-white px-4 py-2 rounded-lg shadow-sm">
            <div className="w-6 h-6 bg-red-500 rounded-full shadow-md"></div>
            <span className="text-sm font-medium text-gray-700">Zona Z2 (TR2 - 25 MVA)</span>
          </div>
        </div>
      </div>

      {/* Informações da barra selecionada - Melhoradas */}
      {selectedBus && (
        <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border-2 border-blue-200 shadow-lg animate-fadeIn">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-900 flex items-center">
              <span className="text-2xl mr-3">📊</span>
              Informações Detalhadas - Barra {selectedBus}
            </h3>
            <button 
              onClick={() => setSelectedBus(null)}
              className="text-gray-500 hover:text-gray-700 text-xl font-bold"
            >
              ✕
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-4 rounded-lg shadow-md">
              <h4 className="font-semibold text-gray-800 mb-2 flex items-center">
                <span className="text-lg mr-2">⚡</span>
                Características Elétricas
              </h4>
              <div className="space-y-1 text-sm">
                <p><strong>Tipo:</strong> <span className="text-blue-600">{getBusType(selectedBus)}</span></p>
                <p><strong>Tensão Nominal:</strong> <span className="text-green-600">13.8 kV</span></p>
                <p><strong>Tensão Atual:</strong> <span className="text-green-600">1.05 pu</span></p>
                <p><strong>Frequência:</strong> <span className="text-blue-600">60 Hz</span></p>
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-md">
              <h4 className="font-semibold text-gray-800 mb-2 flex items-center">
                <span className="text-lg mr-2">🏗️</span>
                Informações Topológicas
              </h4>
              <div className="space-y-1 text-sm">
                <p><strong>Zona:</strong> <span className={`font-bold ${
                  busConfiguration.zone_z1.buses.includes(selectedBus - 1) ? 'text-blue-600' :
                  busConfiguration.zone_z2.buses.includes(selectedBus - 1) ? 'text-red-600' : 'text-green-600'
                }`}>
                  {busConfiguration.zone_z1.buses.includes(selectedBus - 1) ? 'Z1 (TR1)' :
                   busConfiguration.zone_z2.buses.includes(selectedBus - 1) ? 'Z2 (TR2)' : 'Geração'}
                </span></p>
                <p><strong>Conexões:</strong> <span className="text-purple-600">
                  {connections.filter(c => c.from === selectedBus || c.to === selectedBus).length} linhas
                </span></p>
                <p><strong>Coordenadas:</strong> <span className="text-gray-600">
                  ({busPositions[selectedBus]?.x}, {busPositions[selectedBus]?.y})
                </span></p>
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-md">
              <h4 className="font-semibold text-gray-800 mb-2 flex items-center">
                <span className="text-lg mr-2">🛡️</span>
                Status Operacional
              </h4>
              <div className="space-y-1 text-sm">
                <p><strong>Status:</strong> <span className="text-green-600 font-bold">🟢 NORMAL</span></p>
                <p><strong>Carga:</strong> <span className="text-blue-600">85% nominal</span></p>
                <p><strong>Última Verificação:</strong> <span className="text-gray-600">{new Date().toLocaleTimeString()}</span></p>
                <p><strong>Proteção:</strong> <span className="text-green-600">Ativa</span></p>
              </div>
            </div>
          </div>
          
          {/* Dispositivos de Proteção para a barra selecionada */}
          <div className="mt-4 bg-white p-4 rounded-lg shadow-md">
            <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
              <span className="text-lg mr-2">🔧</span>
              Dispositivos de Proteção Associados
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {(busConfiguration.zone_z1.buses.includes(selectedBus - 1) 
                ? busConfiguration.zone_z1.devices 
                : busConfiguration.zone_z2.devices
              ).map((device, idx) => (
                <div key={idx} className="bg-gray-50 px-3 py-2 rounded-lg text-xs">
                  <div className="font-semibold text-gray-700">{device.id}</div>
                  <div className="text-gray-500">{device.pickup} pu / {device.time_delay}s</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IEEE14BusSystem;
