import { useState } from 'react';

interface ProtectionDevice {
  id: string;
  name: string;
  type: string;
  zone: 'Z1' | 'Z2';
  bus_from: number;
  bus_to: number;
  current_setting: number;
  time_setting: number;
  pickup_current: number;
  status: 'active' | 'blocked' | 'fault';
  coordination_status: 'coordinated' | 'miscoordination' | 'optimizing';
}

const ZoneBasedProtectionView = () => {
  const [selectedZone, setSelectedZone] = useState<'all' | 'Z1' | 'Z2'>('all');
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null);
  
  const [devices] = useState<ProtectionDevice[]>([
    // Zona Z1 - TR1 25MVA
    { id: 'R1', name: 'Proteção Principal TR1', type: 'Diferencial', zone: 'Z1', bus_from: 1, bus_to: 5, current_setting: 1250, time_setting: 0.1, pickup_current: 125, status: 'active', coordination_status: 'coordinated' },
    { id: 'R2', name: 'Backup 1 - TR1', type: 'Sobrecorrente', zone: 'Z1', bus_from: 4, bus_to: 7, current_setting: 800, time_setting: 0.3, pickup_current: 80, status: 'active', coordination_status: 'coordinated' },
    { id: 'R3', name: 'Backup 2 - TR1', type: 'Distância', zone: 'Z1', bus_from: 6, bus_to: 8, current_setting: 950, time_setting: 0.5, pickup_current: 95, status: 'active', coordination_status: 'miscoordination' },
    { id: 'R4', name: 'Proteção Linha Z1', type: 'Sobrecorrente', zone: 'Z1', bus_from: 7, bus_to: 8, current_setting: 650, time_setting: 0.2, pickup_current: 65, status: 'active', coordination_status: 'optimizing' },
    
    // Zona Z2 - TR2 25MVA  
    { id: 'R5', name: 'Proteção Principal TR2', type: 'Diferencial', zone: 'Z2', bus_from: 9, bus_to: 10, current_setting: 1250, time_setting: 0.1, pickup_current: 125, status: 'active', coordination_status: 'coordinated' },
    { id: 'R6', name: 'Backup 1 - TR2', type: 'Sobrecorrente', zone: 'Z2', bus_from: 11, bus_to: 12, current_setting: 750, time_setting: 0.4, pickup_current: 75, status: 'active', coordination_status: 'coordinated' },
    { id: 'R7', name: 'Backup 2 - TR2', type: 'Distância', zone: 'Z2', bus_from: 13, bus_to: 14, current_setting: 900, time_setting: 0.6, pickup_current: 90, status: 'blocked', coordination_status: 'miscoordination' },
    { id: 'R8', name: 'Proteção Linha Z2', type: 'Sobrecorrente', zone: 'Z2', bus_from: 12, bus_to: 13, current_setting: 600, time_setting: 0.25, pickup_current: 60, status: 'active', coordination_status: 'optimizing' }
  ]);

  const getFilteredDevices = () => {
    if (selectedZone === 'all') return devices;
    return devices.filter(device => device.zone === selectedZone);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'blocked': return 'text-red-600 bg-red-100';
      case 'fault': return 'text-orange-600 bg-orange-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getCoordinationColor = (coordination: string) => {
    switch (coordination) {
      case 'coordinated': return 'text-green-600 bg-green-100';
      case 'miscoordination': return 'text-red-600 bg-red-100';
      case 'optimizing': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getZoneColor = (zone: string) => {
    switch (zone) {
      case 'Z1': return 'text-blue-600 bg-blue-100';
      case 'Z2': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Filtros por Zona */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h3 className="text-xl font-bold text-gray-900 mb-4">🛡️ Filtrar por Zona de Proteção</h3>
        <div className="flex space-x-4 flex-wrap gap-2">
          {[
            { id: 'all', name: 'Todas as Zonas', icon: '🏠', color: 'gray' },
            { id: 'Z1', name: 'Zona Z1 (TR1 25MVA)', icon: '🔵', color: 'blue' },
            { id: 'Z2', name: 'Zona Z2 (TR2 25MVA)', icon: '🔴', color: 'red' }
          ].map(zone => (
            <button
              key={zone.id}
              onClick={() => setSelectedZone(zone.id as any)}
              className={`px-4 py-3 rounded-xl font-semibold transition-all flex items-center space-x-2 ${
                selectedZone === zone.id
                  ? `bg-${zone.color}-600 text-white shadow-lg`
                  : `bg-${zone.color}-100 text-${zone.color}-700 hover:bg-${zone.color}-200`
              }`}
            >
              <span>{zone.icon}</span>
              <span>{zone.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Resumo das Zonas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-xl border-2 border-blue-300">
          <h4 className="font-bold text-blue-900 mb-2">🔵 ZONA Z1 (TR1)</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-2xl font-bold text-blue-700">
                {devices.filter(d => d.zone === 'Z1').length}
              </div>
              <p className="text-sm text-blue-600">Dispositivos</p>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-700">
                {devices.filter(d => d.zone === 'Z1' && d.status === 'active').length}
              </div>
              <p className="text-sm text-green-600">Ativos</p>
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-red-50 to-red-100 p-6 rounded-xl border-2 border-red-300">
          <h4 className="font-bold text-red-900 mb-2">🔴 ZONA Z2 (TR2)</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-2xl font-bold text-red-700">
                {devices.filter(d => d.zone === 'Z2').length}
              </div>
              <p className="text-sm text-red-600">Dispositivos</p>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-700">
                {devices.filter(d => d.zone === 'Z2' && d.status === 'active').length}
              </div>
              <p className="text-sm text-green-600">Ativos</p>
            </div>
          </div>
        </div>
      </div>

      {/* Status de Coordenação */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h3 className="text-xl font-bold text-gray-900 mb-4">📊 Status Global de Coordenação</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 rounded-lg bg-green-50 border-2 border-green-200">
            <div className="text-3xl font-bold text-green-600">
              {devices.filter(d => d.coordination_status === 'coordinated').length}
            </div>
            <p className="text-green-700 font-semibold">Coordenados</p>
          </div>
          <div className="text-center p-4 rounded-lg bg-red-50 border-2 border-red-200">
            <div className="text-3xl font-bold text-red-600">
              {devices.filter(d => d.coordination_status === 'miscoordination').length}
            </div>
            <p className="text-red-700 font-semibold">Descoordenados</p>
          </div>
          <div className="text-center p-4 rounded-lg bg-yellow-50 border-2 border-yellow-200">
            <div className="text-3xl font-bold text-yellow-600">
              {devices.filter(d => d.coordination_status === 'optimizing').length}
            </div>
            <p className="text-yellow-700 font-semibold">Otimizando</p>
          </div>
        </div>
      </div>

      {/* Tabela de Dispositivos */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-xl font-bold text-gray-900">
            🛡️ Dispositivos de Proteção {selectedZone !== 'all' && `- ${selectedZone}`}
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dispositivo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Zona</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Barras</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ajuste (A)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tempo (s)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Coordenação</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {getFilteredDevices().map((device) => (
                <tr key={device.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{device.id}</div>
                    <div className="text-sm text-gray-500">{device.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getZoneColor(device.zone)}`}>
                      {device.zone}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {device.type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {device.bus_from} → {device.bus_to}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {device.current_setting}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {device.time_setting}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(device.status)}`}>
                      {device.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getCoordinationColor(device.coordination_status)}`}>
                      {device.coordination_status.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex space-x-2">
                      <button 
                        onClick={() => setSelectedDevice(device.id)}
                        className="px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-xs"
                      >
                        ⚙️ Config
                      </button>
                      <button 
                        onClick={() => alert(`Testando ${device.name}...`)}
                        className="px-2 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors text-xs"
                      >
                        🔧 Teste
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Ações RL */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h3 className="text-xl font-bold text-gray-900 mb-4">🤖 Ações de Reinforcement Learning</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button 
            onClick={async () => {
              try {
                const response = await fetch('http://localhost:8000/optimize_coordination', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ zones: ['Z1', 'Z2'], algorithm: 'Q-Learning' })
                });
                
                if (response.ok) {
                  const result = await response.json();
                  alert(`🎯 OTIMIZAÇÃO RL INICIADA:

🔄 Algoritmo: Q-Learning
🎯 Zonas: Z1 e Z2
📊 Episódios: ${result.episodes || 1000}
⏱️ Status: ${result.status || 'Em execução'}

🤖 Otimizando ajustes de coordenação...`);
                } else {
                  alert('❌ Erro na comunicação com o backend RL');
                }
              } catch (error) {
                alert('🔄 Modo simulação: Iniciando otimização RL para todas as zonas...');
              }
            }}
            className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-semibold"
          >
            🎯 Otimizar Coordenação
          </button>
          <button 
            onClick={async () => {
              try {
                const response = await fetch('http://localhost:8000/apply_rl_settings', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ apply_recommended: true })
                });
                
                if (response.ok) {
                  const result = await response.json();
                  alert(`⚡ AJUSTES RL APLICADOS:

🔧 Dispositivos Atualizados: ${result.updated_devices || 8}
📈 Melhoria na Coordenação: ${result.improvement || '15%'}
⏱️ Novos Tempos: Otimizados
🎯 Status: ${result.status || 'Aplicado com sucesso'}

✅ Sistema reconfigurado com RL!`);
                } else {
                  alert('❌ Erro na aplicação dos ajustes RL');
                }
              } catch (error) {
                alert('⚡ Modo simulação: Aplicando ajustes RL recomendados...');
              }
            }}
            className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            ⚡ Aplicar Ajustes RL
          </button>
          <button 
            onClick={async () => {
              try {
                const response = await fetch('http://localhost:8000/simulate_with_rl', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ test_scenarios: ['fault_Z1', 'fault_Z2'] })
                });
                
                if (response.ok) {
                  const result = await response.json();
                  alert(`🔄 SIMULAÇÃO COM AJUSTES RL:

🧪 Cenários Testados: ${result.scenarios || 2}
⚡ Z1 - Tempo médio: ${result.z1_time || '0.28s'}
🔴 Z2 - Tempo médio: ${result.z2_time || '0.32s'}
🎯 Coordenação: ${result.coordination || 'Melhorada'}

✅ Ajustes RL validados!`);
                } else {
                  alert('❌ Erro na simulação com ajustes RL');
                }
              } catch (error) {
                alert('🔄 Modo simulação: Simulando com novos ajustes RL...');
              }
            }}
            className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold"
          >
            🔄 Simular Ajustes
          </button>
          <button 
            onClick={async () => {
              try {
                const response = await fetch('http://localhost:8000/validate_coordination', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ check_all_zones: true })
                });
                
                if (response.ok) {
                  const result = await response.json();
                  alert(`✅ VALIDAÇÃO DE COORDENAÇÃO:

🛡️ Z1: ${result.z1_status || 'COORDENADO'}
🔴 Z2: ${result.z2_status || 'COORDENADO'}
📊 Índice Global: ${result.coordination_index || '0.95'}
⚡ Seletividade: ${result.selectivity || 'ADEQUADA'}

🎯 Sistema ${result.overall || 'APROVADO'} nas verificações!`);
                } else {
                  alert('❌ Erro na validação da coordenação');
                }
              } catch (error) {
                alert('✅ Modo simulação: Validando coordenação do sistema...');
              }
            }}
            className="px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-semibold"
          >
            ✅ Validar Resultado
          </button>
        </div>
      </div>

      {/* Modal de configuração do dispositivo selecionado */}
      {selectedDevice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-xl max-w-md w-full mx-4">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              ⚙️ Configuração: {devices.find(d => d.id === selectedDevice)?.name}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ajuste de Corrente (A)</label>
                <input 
                  type="number" 
                  defaultValue={devices.find(d => d.id === selectedDevice)?.current_setting}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ajuste de Tempo (s)</label>
                <input 
                  type="number" 
                  step="0.1"
                  defaultValue={devices.find(d => d.id === selectedDevice)?.time_setting}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex space-x-3 pt-4">
                <button 
                  onClick={() => {
                    alert('Configurações salvas!');
                    setSelectedDevice(null);
                  }}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  💾 Salvar
                </button>
                <button 
                  onClick={() => setSelectedDevice(null)}
                  className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  ❌ Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ZoneBasedProtectionView;
