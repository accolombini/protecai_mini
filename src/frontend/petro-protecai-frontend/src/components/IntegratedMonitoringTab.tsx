import { useState } from 'react';

interface ProtectionDevice {
  id: string;
  type: string;
  location: string;
  pickup: number;
  time_delay: number;
  status: 'normal' | 'alarm' | 'trip';
  zone: 'Z1' | 'Z2';
}

const IntegratedMonitoringTab = () => {
  const [activeView, setActiveView] = useState<'overview' | 'zones'>('overview');
  
  const [devices] = useState<ProtectionDevice[]>([
    { id: "87T-TR1", type: "87T", location: "Transformador TR1", pickup: 0.3, time_delay: 0.02, status: 'normal', zone: 'Z1' },
    { id: "50/51-L4-5", type: "50/51", location: "Linha Bus4-Bus5", pickup: 1.3, time_delay: 0.4, status: 'normal', zone: 'Z1' },
    { id: "67-B4", type: "67", location: "Bus 4", pickup: 1.2, time_delay: 0.35, status: 'normal', zone: 'Z1' },
    { id: "27/59-B7", type: "27/59", location: "Bus 7", pickup: 0.9, time_delay: 1.2, status: 'normal', zone: 'Z1' },
    { id: "87T-TR2", type: "87T", location: "Transformador TR2", pickup: 0.3, time_delay: 0.02, status: 'normal', zone: 'Z2' },
    { id: "50/51-L5-6", type: "50/51", location: "Linha Bus5-Bus6", pickup: 1.4, time_delay: 0.5, status: 'normal', zone: 'Z2' },
    { id: "67-B5", type: "67", location: "Bus 5", pickup: 1.3, time_delay: 0.45, status: 'normal', zone: 'Z2' },
    { id: "27/59-B14", type: "27/59", location: "Bus 14", pickup: 1.0, time_delay: 1.4, status: 'normal', zone: 'Z2' }
  ]);

  const getBusesForZone = (zone: 'Z1' | 'Z2') => {
    return zone === 'Z1' ? [1, 4, 5, 6, 7, 8] : [2, 6, 9, 10, 11, 12, 13, 14];
  };

  return (
    <div className="space-y-6">
      {/* Header com navegação */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-3xl font-bold text-gray-900 mb-4 flex items-center">
          <span className="text-4xl mr-3">📊</span>
          Sistema de Monitoramento e Controle Integrado
        </h2>
        
        {/* Sub-navegação */}
        <div className="flex space-x-4 mt-4">
          <button
            onClick={() => setActiveView('overview')}
            className={`px-6 py-3 rounded-xl font-semibold transition-all ${
              activeView === 'overview' 
                ? 'bg-blue-600 text-white shadow-lg' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            🏠 Visão Geral
          </button>
          <button
            onClick={() => setActiveView('zones')}
            className={`px-6 py-3 rounded-xl font-semibold transition-all ${
              activeView === 'zones' 
                ? 'bg-blue-600 text-white shadow-lg' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            🛡️ Zonas de Proteção
          </button>
        </div>
      </div>

      {/* Visão Geral */}
      {activeView === 'overview' && (
        <div className="space-y-6">
          {/* Status das Zonas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-xl border-2 border-blue-300">
              <h3 className="text-xl font-bold text-blue-900 mb-4">🔵 ZONA Z1 - TR1 (25 MVA)</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="font-medium">Barras Monitoradas:</span>
                  <span className="text-blue-700">{getBusesForZone('Z1').join(', ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Dispositivos Ativos:</span>
                  <span className="text-green-600">{devices.filter(d => d.zone === 'Z1' && d.status === 'normal').length}/4</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Status Geral:</span>
                  <span className="text-green-600 font-bold">✅ NORMAL</span>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-r from-red-50 to-red-100 p-6 rounded-xl border-2 border-red-300">
              <h3 className="text-xl font-bold text-red-900 mb-4">🔴 ZONA Z2 - TR2 (25 MVA)</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="font-medium">Barras Monitoradas:</span>
                  <span className="text-red-700">{getBusesForZone('Z2').join(', ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Dispositivos Ativos:</span>
                  <span className="text-green-600">{devices.filter(d => d.zone === 'Z2' && d.status === 'normal').length}/4</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Status Geral:</span>
                  <span className="text-green-600 font-bold">✅ NORMAL</span>
                </div>
              </div>
            </div>
          </div>

          {/* Métricas do Sistema */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-xl shadow-lg text-center">
              <div className="text-2xl font-bold text-blue-600">14</div>
              <div className="text-sm text-gray-600">Barras IEEE</div>
            </div>
            <div className="bg-white p-4 rounded-xl shadow-lg text-center">
              <div className="text-2xl font-bold text-green-600">8</div>
              <div className="text-sm text-gray-600">Dispositivos</div>
            </div>
            <div className="bg-white p-4 rounded-xl shadow-lg text-center">
              <div className="text-2xl font-bold text-purple-600">100%</div>
              <div className="text-sm text-gray-600">RL Performance</div>
            </div>
            <div className="bg-white p-4 rounded-xl shadow-lg text-center">
              <div className="text-2xl font-bold text-yellow-600">2</div>
              <div className="text-sm text-gray-600">Zonas Ativas</div>
            </div>
          </div>
        </div>
      )}

      {/* Zonas de Proteção */}
      {activeView === 'zones' && (
        <div className="space-y-6">
          {['Z1', 'Z2'].map((zone) => (
            <div key={zone} className={`bg-white p-6 rounded-xl shadow-lg border-l-8 ${
              zone === 'Z1' ? 'border-blue-500' : 'border-red-500'
            }`}>
              <h3 className={`text-2xl font-bold mb-4 ${
                zone === 'Z1' ? 'text-blue-900' : 'text-red-900'
              }`}>
                {zone === 'Z1' ? '🔵' : '🔴'} ZONA {zone} - TR{zone === 'Z1' ? '1' : '2'} (25 MVA)
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3">📍 Barras da Zona</h4>
                  <div className="grid grid-cols-4 gap-2">
                    {getBusesForZone(zone as 'Z1' | 'Z2').map(bus => (
                      <div key={bus} className={`p-2 rounded text-center text-sm font-medium ${
                        zone === 'Z1' ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'
                      }`}>
                        Bus {bus}
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3">🛡️ Dispositivos de Proteção</h4>
                  <div className="space-y-2">
                    {devices.filter(d => d.zone === zone).map(device => (
                      <div key={device.id} className={`p-3 rounded-lg border-2 ${
                        device.status === 'normal' 
                          ? 'bg-green-50 border-green-200' 
                          : 'bg-red-50 border-red-200'
                      }`}>
                        <div className="flex justify-between items-center">
                          <div>
                            <div className="font-semibold text-sm">{device.id}</div>
                            <div className="text-xs text-gray-600">{device.location}</div>
                          </div>
                          <div className="text-right text-xs">
                            <div>Pickup: {device.pickup} pu</div>
                            <div>Delay: {device.time_delay}s</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default IntegratedMonitoringTab;
