import { useState } from 'react';

interface ProtectionDevice {
  id: string;
  type: string;
  location: string;
  pickup: number;
  time_delay: number;
  status: 'normal' | 'alarm' | 'trip';
  last_operation?: string;
}

interface SimulationState {
  isRunning: boolean;
  current_fault?: {
    location: string;
    type: string;
    magnitude: number;
    time: string;
  };
  rl_recommendations: string[];
  system_status: 'normal' | 'fault' | 'recovering';
}

const ProtectionControlPanel = () => {
  const [simulationState, setSimulationState] = useState<SimulationState>({
    isRunning: false,
    rl_recommendations: [],
    system_status: 'normal'
  });
  
  const [devices, setDevices] = useState<ProtectionDevice[]>([
    { id: "87T-TR1", type: "87T", location: "Transformador TR1", pickup: 0.3, time_delay: 0.02, status: 'normal' },
    { id: "50/51-L4-5", type: "50/51", location: "Linha Bus4-Bus5", pickup: 1.3, time_delay: 0.4, status: 'normal' },
    { id: "67-B4", type: "67", location: "Bus 4", pickup: 1.2, time_delay: 0.35, status: 'normal' },
    { id: "27/59-B7", type: "27/59", location: "Bus 7", pickup: 0.9, time_delay: 1.2, status: 'normal' },
    { id: "87T-TR2", type: "87T", location: "Transformador TR2", pickup: 0.3, time_delay: 0.02, status: 'normal' },
    { id: "50/51-L5-6", type: "50/51", location: "Linha Bus5-Bus6", pickup: 1.4, time_delay: 0.5, status: 'normal' },
    { id: "67-B5", type: "67", location: "Bus 5", pickup: 1.3, time_delay: 0.45, status: 'normal' },
    { id: "27/59-B14", type: "27/59", location: "Bus 14", pickup: 1.0, time_delay: 1.4, status: 'normal' }
  ]);

  const startSimulation = async () => {
    setSimulationState(prev => ({ ...prev, isRunning: true, system_status: 'normal' }));
    
    try {
      const response = await fetch('http://localhost:8000/simulate_fault', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fault_type: 'three_phase',
          fault_location: 'bus_4',
          fault_magnitude: 2.5
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setSimulationState(prev => ({
          ...prev,
          current_fault: {
            location: 'Bus 4',
            type: 'Trifásica',
            magnitude: 2.5,
            time: new Date().toLocaleTimeString()
          },
          rl_recommendations: data.rl_recommendations || [],
          system_status: 'fault'
        }));
        
        // Simular atuação dos dispositivos
        setTimeout(() => {
          setDevices(prev => prev.map(device => 
            device.id === '67-B4' 
              ? { ...device, status: 'trip', last_operation: new Date().toLocaleTimeString() }
              : device
          ));
        }, 1000);
      }
    } catch (error) {
      console.error('Erro na simulação:', error);
    }
  };

  const stopSimulation = () => {
    setSimulationState({
      isRunning: false,
      rl_recommendations: [],
      system_status: 'normal'
    });
    
    setDevices(prev => prev.map(device => ({
      ...device,
      status: 'normal',
      last_operation: undefined
    })));
  };

  const resetSystem = () => {
    stopSimulation();
    setSimulationState(prev => ({ ...prev, system_status: 'recovering' }));
    
    setTimeout(() => {
      setSimulationState(prev => ({ ...prev, system_status: 'normal' }));
    }, 2000);
  };

  const getDeviceStatusColor = (status: string) => {
    switch (status) {
      case 'normal': return 'bg-green-100 text-green-800 border-green-200';
      case 'alarm': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'trip': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSystemStatusColor = (status: string) => {
    switch (status) {
      case 'normal': return 'text-green-600';
      case 'fault': return 'text-red-600';
      case 'recovering': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-xl border border-gray-200 hover:shadow-2xl transition-shadow duration-300">
      <div className="mb-6">
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-2 flex items-center justify-center">
            <span className="text-4xl mr-3">🛡️</span>
            Painel de Controle Inteligente
          </h2>
          <p className="text-gray-600">Sistema de Proteção com Otimização por Reinforcement Learning</p>
        </div>
        
        {/* Status do Sistema - Melhorado */}
        <div className="mb-6 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border-2 border-blue-200 hover:border-blue-300 transition-colors">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <div className="text-4xl animate-pulse">
                {simulationState.system_status === 'normal' ? '🟢' :
                 simulationState.system_status === 'fault' ? '🔴' : '🟡'}
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">Status do Sistema IEEE 14-Bus</h3>
                <p className={`text-2xl font-bold ${getSystemStatusColor(simulationState.system_status)}`}>
                  {simulationState.system_status === 'normal' ? '✅ SISTEMA NORMAL' :
                   simulationState.system_status === 'fault' ? '⚠️ FALTA DETECTADA' : '🔄 RECUPERANDO'}
                </p>
                <p className="text-sm text-gray-600">
                  Última atualização: {new Date().toLocaleTimeString()}
                </p>
              </div>
            </div>
            
            {/* Controles Principais */}
            <div className="flex flex-col space-y-3">
              <button
                onClick={startSimulation}
                disabled={simulationState.isRunning}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl disabled:from-gray-400 disabled:to-gray-500 hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-lg hover:shadow-xl font-semibold flex items-center space-x-2"
              >
                <span className="text-xl">🚀</span>
                <span>Iniciar Simulação de Falta</span>
              </button>
              
              <div className="flex space-x-2">
                <button
                  onClick={stopSimulation}
                  disabled={!simulationState.isRunning}
                  className="px-4 py-2 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg disabled:from-gray-400 disabled:to-gray-500 hover:from-red-700 hover:to-red-800 transition-all duration-200 shadow-md hover:shadow-lg font-medium flex items-center space-x-1"
                >
                  <span>⏹️</span>
                  <span>Parar</span>
                </button>
                <button
                  onClick={resetSystem}
                  className="px-4 py-2 bg-gradient-to-r from-yellow-600 to-yellow-700 text-white rounded-lg hover:from-yellow-700 hover:to-yellow-800 transition-all duration-200 shadow-md hover:shadow-lg font-medium flex items-center space-x-1"
                >
                  <span>🔄</span>
                  <span>Reset</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Informações da Falta Atual */}
        {simulationState.current_fault && (
          <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-400 rounded-lg">
            <h3 className="font-semibold text-red-900 mb-2">⚠️ Falta Detectada</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p><strong>Localização:</strong> {simulationState.current_fault.location}</p>
                <p><strong>Tipo:</strong> {simulationState.current_fault.type}</p>
              </div>
              <div>
                <p><strong>Magnitude:</strong> {simulationState.current_fault.magnitude} pu</p>
                <p><strong>Tempo:</strong> {simulationState.current_fault.time}</p>
              </div>
            </div>
          </div>
        )}

        {/* Recomendações do RL Agent */}
        {simulationState.rl_recommendations.length > 0 && (
          <div className="mb-4 p-4 bg-blue-50 border-l-4 border-blue-400 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">🤖 Recomendações do Agente RL</h3>
            <ul className="text-sm text-blue-800 list-disc list-inside">
              {simulationState.rl_recommendations.map((rec, idx) => (
                <li key={idx}>{rec}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Lista de Dispositivos de Proteção */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Dispositivos de Proteção</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {devices.map((device) => (
            <div key={device.id} className={`p-4 rounded-lg border-2 ${getDeviceStatusColor(device.status)}`}>
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-semibold text-sm">{device.id}</h4>
                  <p className="text-xs opacity-75">{device.location}</p>
                </div>
                <span className="px-2 py-1 text-xs font-bold rounded-full bg-opacity-20">
                  {device.status.toUpperCase()}
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <p><strong>Pickup:</strong> {device.pickup} pu</p>
                  <p><strong>Delay:</strong> {device.time_delay}s</p>
                </div>
                <div>
                  <p><strong>Tipo:</strong> {device.type}</p>
                  {device.last_operation && (
                    <p><strong>Operação:</strong> {device.last_operation}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Indicadores de Performance */}
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {devices.filter(d => d.status === 'normal').length}
          </div>
          <div className="text-sm text-blue-800">Dispositivos Normais</div>
        </div>
        
        <div className="text-center p-4 bg-yellow-50 rounded-lg">
          <div className="text-2xl font-bold text-yellow-600">
            {devices.filter(d => d.status === 'alarm').length}
          </div>
          <div className="text-sm text-yellow-800">Alarmes Ativos</div>
        </div>
        
        <div className="text-center p-4 bg-red-50 rounded-lg">
          <div className="text-2xl font-bold text-red-600">
            {devices.filter(d => d.status === 'trip').length}
          </div>
          <div className="text-sm text-red-800">Dispositivos Atuados</div>
        </div>
      </div>
    </div>
  );
};

export default ProtectionControlPanel;
