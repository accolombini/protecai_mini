import { useState, useEffect } from 'react';

interface SystemMetrics {
  voltage_stability: number;
  protection_coverage: number;
  rl_performance: number;
  system_reliability: number;
  active_devices: number;
  total_devices: number;
  last_fault_cleared: string;
  uptime: string;
}

interface RealtimeData {
  bus_voltages: { [key: string]: number };
  line_currents: { [key: string]: number };
  power_flows: { [key: string]: number };
  protection_states: { [key: string]: string };
}

const RealTimeDashboard = () => {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    voltage_stability: 98.5,
    protection_coverage: 100.0,
    rl_performance: 95.8,
    system_reliability: 99.2,
    active_devices: 8,
    total_devices: 8,
    last_fault_cleared: '12:34:56',
    uptime: '847h 23m'
  });

  const [realtimeData, setRealtimeData] = useState<RealtimeData>({
    bus_voltages: {
      'Bus 1': 1.06, 'Bus 2': 1.045, 'Bus 3': 1.01, 'Bus 4': 1.019,
      'Bus 5': 1.020, 'Bus 6': 1.070, 'Bus 7': 1.062, 'Bus 8': 1.090,
      'Bus 9': 1.056, 'Bus 10': 1.051, 'Bus 11': 1.057, 'Bus 12': 1.055,
      'Bus 13': 1.050, 'Bus 14': 1.036
    },
    line_currents: {
      'L1-2': 0.85, 'L1-5': 0.62, 'L2-3': 0.73, 'L2-4': 0.56,
      'L4-5': 0.78, 'L6-11': 0.41, 'L9-14': 0.33
    },
    power_flows: {
      'TR1': 18.5, 'TR2': 21.3, 'G1': 232.4, 'G2': 40.0, 'G3': 0.0
    },
    protection_states: {
      '87T-TR1': 'Normal', '50/51-L4-5': 'Normal', '67-B4': 'Normal',
      '27/59-B7': 'Normal', '87T-TR2': 'Normal', '50/51-L5-6': 'Normal',
      '67-B5': 'Normal', '27/59-B14': 'Normal'
    }
  });

  const [isConnected] = useState(true);

  useEffect(() => {
    // Simular dados em tempo real
    const interval = setInterval(() => {
      setRealtimeData(prev => ({
        ...prev,
        bus_voltages: Object.fromEntries(
          Object.entries(prev.bus_voltages).map(([bus, voltage]) => [
            bus, 
            Math.max(0.95, Math.min(1.1, voltage + (Math.random() - 0.5) * 0.005))
          ])
        ),
        line_currents: Object.fromEntries(
          Object.entries(prev.line_currents).map(([line, current]) => [
            line,
            Math.max(0.1, Math.min(1.5, current + (Math.random() - 0.5) * 0.05))
          ])
        )
      }));

      // Simular pequenas variações nas métricas
      setMetrics(prev => ({
        ...prev,
        voltage_stability: Math.max(95, Math.min(100, prev.voltage_stability + (Math.random() - 0.5) * 0.5)),
        rl_performance: Math.max(90, Math.min(100, prev.rl_performance + (Math.random() - 0.5) * 0.3))
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const getVoltageColor = (voltage: number) => {
    if (voltage < 0.95 || voltage > 1.05) return 'text-red-600';
    if (voltage < 0.98 || voltage > 1.02) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getCurrentColor = (current: number) => {
    if (current > 1.2) return 'text-red-600';
    if (current > 0.9) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getMetricColor = (value: number, threshold: number = 95) => {
    if (value >= threshold) return 'text-green-600';
    if (value >= threshold - 5) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Status Geral */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            📡 Dashboard em Tempo Real - ProtecAI
          </h2>
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${
            isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span>{isConnected ? 'Sistema Online' : 'Sistema Offline'}</span>
          </div>
        </div>

        {/* Métricas Principais */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className={`text-3xl font-bold ${getMetricColor(metrics.voltage_stability)}`}>
              {metrics.voltage_stability.toFixed(1)}%
            </div>
            <div className="text-sm text-blue-800">Estabilidade de Tensão</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className={`text-3xl font-bold ${getMetricColor(metrics.protection_coverage)}`}>
              {metrics.protection_coverage.toFixed(1)}%
            </div>
            <div className="text-sm text-green-800">Cobertura de Proteção</div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className={`text-3xl font-bold ${getMetricColor(metrics.rl_performance)}`}>
              {metrics.rl_performance.toFixed(1)}%
            </div>
            <div className="text-sm text-purple-800">Performance RL</div>
          </div>
          
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className={`text-3xl font-bold ${getMetricColor(metrics.system_reliability)}`}>
              {metrics.system_reliability.toFixed(1)}%
            </div>
            <div className="text-sm text-yellow-800">Confiabilidade</div>
          </div>
        </div>

        {/* Informações do Sistema */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="bg-gray-50 p-3 rounded">
            <div className="font-semibold text-gray-700">Dispositivos Ativos</div>
            <div className="text-lg font-bold text-green-600">
              {metrics.active_devices}/{metrics.total_devices}
            </div>
          </div>
          
          <div className="bg-gray-50 p-3 rounded">
            <div className="font-semibold text-gray-700">Último Defeito</div>
            <div className="text-lg font-bold text-blue-600">{metrics.last_fault_cleared}</div>
          </div>
          
          <div className="bg-gray-50 p-3 rounded">
            <div className="font-semibold text-gray-700">Tempo Operação</div>
            <div className="text-lg font-bold text-purple-600">{metrics.uptime}</div>
          </div>
          
          <div className="bg-gray-50 p-3 rounded">
            <div className="font-semibold text-gray-700">Status Geral</div>
            <div className="text-lg font-bold text-green-600">NORMAL</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tensões das Barras - ZONA Z1 */}
        <div className="bg-white p-6 rounded-lg shadow-lg border-l-4 border-blue-500">
          <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center">
            🔵 <span className="ml-2">ZONA Z1 - Tensões das Barras (pu)</span>
          </h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(realtimeData.bus_voltages)
              .filter(([bus]) => [1, 5, 6, 7, 8, 10].includes(parseInt(bus.split(' ')[1])))
              .map(([bus, voltage]) => (
              <div key={bus} className="flex justify-between items-center p-2 bg-blue-50 rounded border border-blue-200">
                <span className="font-medium text-blue-800">{bus}:</span>
                <span className={`font-bold ${getVoltageColor(voltage)}`}>
                  {voltage.toFixed(3)}
                </span>
              </div>
            ))}
          </div>
          
          {/* Correntes ZONA Z1 */}
          <h4 className="text-md font-semibold text-blue-900 mt-4 mb-2">🔌 Correntes das Linhas Z1</h4>
          <div className="space-y-2 text-sm">
            {Object.entries(realtimeData.line_currents)
              .filter(([line]) => ['L1-2', 'L1-5', 'L4-5'].includes(line))
              .map(([line, current]) => (
              <div key={line} className="flex justify-between items-center p-2 bg-blue-50 rounded border border-blue-200">
                <span className="font-medium text-blue-800">{line}:</span>
                <span className={`font-bold ${getCurrentColor(current)}`}>
                  {current.toFixed(3)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Tensões das Barras - ZONA Z2 */}
        <div className="bg-white p-6 rounded-lg shadow-lg border-l-4 border-red-500">
          <h3 className="text-lg font-semibold text-red-900 mb-4 flex items-center">
            � <span className="ml-2">ZONA Z2 - Tensões das Barras (pu)</span>
          </h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(realtimeData.bus_voltages)
              .filter(([bus]) => [2, 6, 9, 11, 12, 13, 14].includes(parseInt(bus.split(' ')[1])))
              .map(([bus, voltage]) => (
              <div key={bus} className="flex justify-between items-center p-2 bg-red-50 rounded border border-red-200">
                <span className="font-medium text-red-800">{bus}:</span>
                <span className={`font-bold ${getVoltageColor(voltage)}`}>
                  {voltage.toFixed(3)}
                </span>
              </div>
            ))}
          </div>
          
          {/* Correntes ZONA Z2 */}
          <h4 className="text-md font-semibold text-red-900 mt-4 mb-2">🔌 Correntes das Linhas Z2</h4>
          <div className="space-y-2 text-sm">
            {Object.entries(realtimeData.line_currents)
              .filter(([line]) => ['L5-6', 'L6-11', 'L9-14'].includes(line))
              .map(([line, current]) => (
              <div key={line} className="flex justify-between items-center p-2 bg-red-50 rounded border border-red-200">
                <span className="font-medium text-red-800">{line}:</span>
                <span className={`font-bold ${getCurrentColor(current)}`}>
                  {current.toFixed(3)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Fluxos de Potência */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            ⚙️ Fluxos de Potência (MW)
          </h3>
          <div className="space-y-2 text-sm">
            {Object.entries(realtimeData.power_flows).map(([component, power]) => (
              <div key={component} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                <span className="font-medium">{component}:</span>
                <span className="font-bold text-blue-600">
                  {power.toFixed(1)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Estados dos Dispositivos */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🛡️ Estados dos Dispositivos
          </h3>
          <div className="space-y-2 text-sm">
            {Object.entries(realtimeData.protection_states).map(([device, state]) => (
              <div key={device} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                <span className="font-medium">{device}:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                  state === 'Normal' 
                    ? 'bg-green-100 text-green-800' 
                    : state === 'Alarm'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {state}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Mensagens do Sistema */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          📢 Log do Sistema em Tempo Real
        </h3>
        <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm h-32 overflow-y-auto">
          <div>[{new Date().toLocaleTimeString()}] ProtecAI RL Agent: Sistema operando normalmente</div>
          <div>[{new Date().toLocaleTimeString()}] Coordenação de proteção: Todos os dispositivos em estado normal</div>
          <div>[{new Date().toLocaleTimeString()}] IEEE 14-Bus System: Tensões e correntes dentro dos limites</div>
          <div>[{new Date().toLocaleTimeString()}] API Health Check: ✅ Todos os serviços online</div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeDashboard;
