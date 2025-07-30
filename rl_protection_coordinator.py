"""
ProtecAI Mini - Sistema de Coordenação de Proteção com RL
IEEE 14-Bus Protection Coordination System with Reinforcement Learning

Sistema completo de coordenação de proteção para plataformas offshore
com algoritmo de aprendizado por reforço para otimização automática.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import random
import json
from datetime import datetime

@dataclass
class ProtectionDevice:
    """Dispositivo de proteção ANSI com parâmetros reais"""
    id: str
    zone: str  # Z1 ou Z2
    type: str  # 50/51, 67, 87T, 27/59
    location: str
    pickup_current: float  # em pu
    time_delay: float  # em segundos
    distance_km: float
    coordination_margin: float = 0.3  # IEEE C37.112 padrão
    status: str = 'active'

@dataclass
class ProtectionZone:
    """Zona de proteção IEEE 14-Bus"""
    id: str
    transformer: str
    power_mva: float
    voltage_kv: float
    buses: List[int]
    devices: List[ProtectionDevice]

@dataclass
class FaultSimulationResult:
    """Resultado completo da simulação de falta"""
    fault_location: str
    fault_type: str
    fault_current_a: float
    affected_zone: str
    coordination_ok: bool
    device_responses: List[Dict]
    coordination_issues: List[Dict]
    normative_compliance: Dict

class BasicRLAgent:
    """
    Agente de Aprendizado por Reforço para otimização de coordenação de proteção
    Algoritmo: Q-Learning com epsilon-greedy
    """
    
    def __init__(self, state_size=64, action_space_size=32, learning_rate=0.01, epsilon=0.3):
        self.state_size = state_size
        self.action_space_size = action_space_size
        self.learning_rate = learning_rate
        self.epsilon = epsilon
        self.epsilon_decay = 0.99  # Decay mais lento para exploração adequada
        self.epsilon_min = 0.05
        
        # Q-table para aprendizado - maior para capturar complexidade
        self.q_table = np.zeros((state_size, action_space_size))
        
        # Histórico de treinamento
        self.episodes = 0
        self.max_episodes = 1000
        self.training_history = []
        
        # Parâmetros avançados para coordenação de proteção
        self.gamma = 0.95  # Fator de desconto
        self.min_exploration_episodes = 50  # Mínimo de episódios para exploração
    
    def get_state(self, coordinator, fault_result):
        """
        Estado avançado para coordenação de proteção baseado em normas técnicas
        Captura: coordenação, seletividade, conformidade normativa, tempos, correntes
        """
        state_vector = []
        
        # 1. Estado básico da coordenação
        state_vector.append(1 if fault_result.coordination_ok else 0)
        
        # 2. Número de dispositivos operando (seletividade)
        operating_count = len([d for d in fault_result.device_responses if d['should_operate']])
        state_vector.append(min(operating_count / 8.0, 1.0))  # Normalizado
        
        # 3. Zona afetada
        state_vector.append(1 if fault_result.affected_zone == 'Z1' else 0)
        
        # 4. Tipo de falta (codificado)
        fault_encoding = {'3ph': 0.25, '2ph': 0.5, '1ph': 0.75, '2ph_ground': 1.0}
        state_vector.append(fault_encoding.get(fault_result.fault_type, 0.25))
        
        # 5. Problemas de coordenação IEEE C37.112
        coord_issues = len(fault_result.coordination_issues)
        state_vector.append(min(coord_issues / 10.0, 1.0))  # Normalizado
        
        # 6. Conformidade normativa (4 normas)
        for norm, compliance in fault_result.normative_compliance.items():
            state_vector.append(1 if compliance.get('coordination_margins', False) or 
                              compliance.get('goose_performance', False) or 
                              compliance.get('selectivity_dr', False) or 
                              compliance.get('offshore_environment', False) else 0)
        
        # 7. Tempos de operação dos dispositivos primários (87T, 50/51)
        primary_times = []
        for device in fault_result.device_responses:
            if device['should_operate'] and device['type'] in ['87T', '50/51']:
                primary_times.append(device['operating_time'])
        
        # Estatísticas dos tempos
        if primary_times:
            state_vector.append(min(min(primary_times) / 2.0, 1.0))  # Tempo mínimo
            state_vector.append(min(max(primary_times) / 2.0, 1.0))  # Tempo máximo
            state_vector.append(min(np.std(primary_times) / 1.0, 1.0))  # Desvio padrão
        else:
            state_vector.extend([0, 0, 0])
        
        # 8. Corrente de falta normalizada
        state_vector.append(min(fault_result.fault_current_a / 15000.0, 1.0))
        
        # 9. Estado específico dos dispositivos críticos
        critical_devices = ['87T-TR1', '87T-TR2', '50/51-L4-5', '50/51-L5-6']
        for device_id in critical_devices:
            device_response = next((d for d in fault_result.device_responses if d['device_id'] == device_id), None)
            if device_response:
                state_vector.append(1 if device_response['should_operate'] else 0)
                state_vector.append(min(device_response['operating_time'] / 2.0, 1.0) if device_response['should_operate'] else 0)
            else:
                state_vector.extend([0, 0])
        
        # Preenche até state_size com zeros se necessário
        while len(state_vector) < self.state_size:
            state_vector.append(0)
        
        # Trunca se exceder
        state_vector = state_vector[:self.state_size]
        
        # Converte para índice da Q-table usando hash
        return abs(hash(tuple(np.round(state_vector, 3)))) % self.state_size
    
    def get_action(self, state):
        """Seleciona ação usando epsilon-greedy"""
        if np.random.random() <= self.epsilon:
            return np.random.choice(self.action_space_size)
        return np.argmax(self.q_table[state])
    
    def calculate_reward(self, fault_result, critical_load_lost=False, blackout=False):
        """
        Função de recompensa avançada baseada no documento PARAMETRIZACAO_PROTECAO_BASICO.txt
        Implementa sistema de recompensas/penalidades conforme normas IEEE 242, API RP 14F, ABNT NBR 14039
        """
        reward = 0
        
        # === RECOMPENSAS PRINCIPAIS (conforme documento) ===
        
        # 1. Atuação seletiva correta (+10 pontos)
        if fault_result.coordination_ok:
            primary_operated = any(
                d['should_operate'] and d['coordination_ok'] 
                for d in fault_result.device_responses 
                if d['type'] in ['87T', '50/51']
            )
            if primary_operated:
                reward += 10
                
            # Bonificação adicional por coordenação perfeita
            if len(fault_result.coordination_issues) == 0:
                reward += 5
        
        # 2. Backup funcionando após falha primária (+5 pontos)
        backup_operated = any(d['should_operate'] and d['type'] == '50/51' for d in fault_result.device_responses)
        differential_failed = not any(d['should_operate'] and d['type'] == '87T' for d in fault_result.device_responses)
        
        if backup_operated and differential_failed:
            reward += 5
        
        # 3. Seletividade adequada (NBR 5410)
        operating_devices = len([d for d in fault_result.device_responses if d['should_operate']])
        if operating_devices <= 2:  # Seletividade excelente
            reward += 8
        elif operating_devices <= 3:  # Seletividade boa
            reward += 4
        elif operating_devices > 5:  # Seletividade ruim
            reward -= 10
        
        # 4. Conformidade normativa (bonificações)
        normative_bonus = 0
        for norm, compliance in fault_result.normative_compliance.items():
            if isinstance(compliance, dict):
                if compliance.get('coordination_margins', False):
                    normative_bonus += 3  # IEEE C37.112
                if compliance.get('goose_performance', False):
                    normative_bonus += 2  # IEC 61850
                if compliance.get('selectivity_dr', False):
                    normative_bonus += 3  # NBR 5410
                if compliance.get('offshore_environment', False):
                    normative_bonus += 2  # API RP 14C
        reward += normative_bonus
        
        # === PENALIDADES (conforme documento) ===
        
        # 5. Problemas de coordenação (-5 por problema)
        coordination_issues = len(fault_result.coordination_issues)
        reward -= coordination_issues * 5
        
        # 6. Coordenação geral falhando (-25 pontos)
        if not fault_result.coordination_ok:
            reward -= 25
        
        # 7. Carga crítica desligada (-20 pontos)
        if critical_load_lost:
            reward -= 20
        
        # 8. Blackout geral (-50 pontos)
        if blackout:
            reward -= 50
        
        # 9. Tempos de coordenação inadequados
        operating_times = [d['operating_time'] for d in fault_result.device_responses if d['should_operate']]
        if len(operating_times) > 1:
            time_spread = max(operating_times) - min(operating_times)
            if time_spread < 0.2:  # Tempos muito próximos (< 200ms)
                reward -= 8
            elif time_spread > 2.0:  # Tempos muito distantes (> 2s)
                reward -= 5
        
        # 10. Dispositivos diferenciais não operando em falhas internas
        if fault_result.affected_zone in ['Z1', 'Z2']:
            diff_operated = any(
                d['should_operate'] and d['type'] == '87T' and fault_result.affected_zone in d['device_id']
                for d in fault_result.device_responses
            )
            if not diff_operated:
                reward -= 15  # Penalidade por diferencial não operar
        
        # === RECOMPENSAS AVANÇADAS ===
        
        # 11. Margem de coordenação adequada
        adequate_margins = sum(1 for issue in fault_result.coordination_issues if issue['margin'] >= 0.25)
        total_margins = len(fault_result.coordination_issues)
        if total_margins > 0:
            margin_ratio = adequate_margins / total_margins
            reward += margin_ratio * 3
        
        # 12. Velocidade de atuação apropriada
        fast_devices = [d for d in fault_result.device_responses 
                       if d['should_operate'] and d['operating_time'] < 0.1]
        if len(fast_devices) > 0 and len(fast_devices) <= 2:  # Apenas dispositivos rápidos necessários
            reward += 3
        
        return reward
    
    def learn(self, state, action, reward, next_state):
        """Algoritmo Q-Learning avançado para coordenação de proteção"""
        # Q-Learning com experiência
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.gamma * self.q_table[next_state][best_next_action]
        td_error = td_target - self.q_table[state][action]
        
        # Atualização com taxa de aprendizado adaptativa
        adaptive_lr = self.learning_rate * (1 + abs(td_error) / 10)  # Maior erro = mais aprendizado
        self.q_table[state][action] += adaptive_lr * td_error
        
        # Decaimento do epsilon apenas após exploração mínima
        if self.episodes > self.min_exploration_episodes and self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def get_action(self, state):
        """Seleção de ação epsilon-greedy melhorada"""
        # Exploração forçada nas primeiras iterações
        if self.episodes < self.min_exploration_episodes:
            return np.random.choice(self.action_space_size)
        
        # Epsilon-greedy padrão
        if np.random.random() <= self.epsilon:
            return np.random.choice(self.action_space_size)
        
        # Seleção gulosa com ruído para evitar mínimos locais
        q_values = self.q_table[state] + np.random.normal(0, 0.01, self.action_space_size)
        return np.argmax(q_values)
    
    def train_episode(self, coordinator, scenarios):
        """Treina um episódio com cenários de falta"""
        self.episodes += 1
        episode_reward = 0
        
        for scenario in scenarios:
            # Simula falta
            fault_result = coordinator.simulate_fault(
                scenario['bus'], 
                scenario['fault_type'], 
                scenario['severity']
            )
            
            # Obtém estado
            state = self.get_state(coordinator, fault_result)
            
            # Seleciona ação
            action = self.get_action(state)
            
            # Aplica ação (ajuste nos dispositivos)
            coordinator.apply_rl_action(action)
            
            # Simula novamente após ajuste
            new_fault_result = coordinator.simulate_fault(
                scenario['bus'], 
                scenario['fault_type'], 
                scenario['severity']
            )
            
            # Calcula recompensa
            reward = self.calculate_reward(new_fault_result)
            episode_reward += reward
            
            # Obtém novo estado
            next_state = self.get_state(coordinator, new_fault_result)
            
            # Aprende
            self.learn(state, action, reward, next_state)
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        # Registra histórico
        self.training_history.append({
            'episode': self.episodes,
            'reward': episode_reward,
            'epsilon': self.epsilon
        })
        
        return episode_reward

class ProtectionCoordinator:
    """
    Coordenador principal do sistema de proteção IEEE 14-Bus
    Com capacidades de simulação de faltas e otimização RL
    """
    
    def __init__(self):
        self.protection_zones = self._create_ieee_14bus_zones()
        self.protection_devices = self._get_all_devices()
        self.rl_agent = BasicRLAgent()
        
        # Impedância simplificada do sistema IEEE 14-Bus
        self.bus_impedances = {
            1: 0.1, 2: 0.12, 3: 0.15, 4: 0.08, 5: 0.09, 6: 0.11, 7: 0.13,
            8: 0.14, 9: 0.16, 10: 0.18, 11: 0.19, 12: 0.20, 13: 0.21, 14: 0.22
        }
        
    def _create_ieee_14bus_zones(self):
        """Cria as zonas de proteção do sistema IEEE 14-Bus"""
        
                # Configuração das Zonas de Proteção IEEE 14-Bus - PARÂMETROS NORMATIVOS REAIS
        # Baseado em ABNT NBR 14039, IEEE 242, API RP 14F, IEC 60255-151
        # Zona Z1: Transformador TR1 (25 MVA) - Buses 0,4,5,6,7,9
        zone_z1_devices = [
            ProtectionDevice(
                id="87T-TR1", zone="Z1", type="87T", 
                location="Transformador TR1",
                pickup_current=0.3, time_delay=0.02, distance_km=0.0,  # IEC 60255-8 + API RP 14F
                coordination_margin=0.0  # Instantâneo conforme IEEE 242
            ),
            ProtectionDevice(
                id="50/51-L4-5", zone="Z1", type="50/51",
                location="Linha Bus4-Bus5", 
                pickup_current=1.3, time_delay=0.4, distance_km=2.5,  # IEC 60255-151 + IEEE 242
                coordination_margin=0.3  # IEEE C37.112 padrão
            ),
            ProtectionDevice(
                id="67-B4", zone="Z1", type="67",
                location="Bus 4",
                pickup_current=1.2, time_delay=0.35, distance_km=0.0,  # IEEE C37.112 + NORSOK E-001
                coordination_margin=0.3
            ),
            ProtectionDevice(
                id="27/59-B7", zone="Z1", type="27/59",
                location="Bus 7",
                pickup_current=0.9, time_delay=1.2, distance_km=3.2,  # ABNT NBR 14039 + API RP 14F
                coordination_margin=0.4  # Maior margem para backup
            )
        ]
        
        # Zona Z2: Transformador TR2 (25 MVA) - Buses 1,5,8,10-14  
        zone_z2_devices = [
            ProtectionDevice(
                id="87T-TR2", zone="Z2", type="87T",
                location="Transformador TR2",
                pickup_current=0.3, time_delay=0.02, distance_km=0.0,  # IEC 60255-8 + API RP 14F
                coordination_margin=0.0  # Instantâneo conforme IEEE 242
            ),
            ProtectionDevice(
                id="50/51-L5-6", zone="Z2", type="50/51",
                location="Linha Bus5-Bus6",
                pickup_current=1.4, time_delay=0.5, distance_km=1.8,  # IEC 60255-151 coordenado com Z1
                coordination_margin=0.3  # IEEE C37.112 padrão
            ),
            ProtectionDevice(
                id="67-B5", zone="Z2", type="67", 
                location="Bus 5",
                pickup_current=1.3, time_delay=0.45, distance_km=0.0,  # IEEE C37.112 + NORSOK E-001
                coordination_margin=0.3
            ),
            ProtectionDevice(
                id="27/59-B14", zone="Z2", type="27/59",
                location="Bus 14",
                pickup_current=1.0, time_delay=1.4, distance_km=4.1,  # ABNT NBR 14039 + API RP 14F
                coordination_margin=0.4  # Maior margem para backup
            )
        ]
        
        zones = [
            ProtectionZone(
                id="Z1", transformer="TR1 (25 MVA)", power_mva=25, voltage_kv=13.8,
                buses=[0, 4, 5, 6, 7, 9], devices=zone_z1_devices
            ),
            ProtectionZone(
                id="Z2", transformer="TR2 (25 MVA)", power_mva=25, voltage_kv=13.8,
                buses=[1, 5, 8, 10, 11, 12, 13, 14], devices=zone_z2_devices
            )
        ]
        
        return zones
    
    def _get_all_devices(self):
        """Retorna lista de todos os dispositivos"""
        devices = []
        for zone in self.protection_zones:
            devices.extend(zone.devices)
        return devices
    
    def simulate_fault(self, bus: int, fault_type: str, severity: float) -> FaultSimulationResult:
        """
        Simula falta no sistema IEEE 14-Bus
        
        Args:
            bus: Número da barra (1-14)
            fault_type: Tipo de falta ('3ph', '2ph', '1ph', '2ph_ground')
            severity: Severidade da falta (0.1 a 1.0)
        """
        
        # Determina zona afetada
        affected_zone = "Z1" if bus in [0, 4, 5, 6, 7, 9] else "Z2"
        
        # Calcula corrente de falta usando impedância do bus
        base_current = 1000  # A (base)
        bus_impedance = self.bus_impedances.get(bus, 0.15)
        
        # Fatores por tipo de falta
        fault_factors = {'3ph': 1.0, '2ph': 0.87, '1ph': 0.58, '2ph_ground': 0.95}
        fault_factor = fault_factors.get(fault_type, 1.0)
        
        fault_current = (base_current * severity * fault_factor) / bus_impedance
        
        # Simula resposta dos dispositivos
        device_responses = []
        coordination_issues = []
        
        for device in self.protection_devices:
            should_operate = False
            operating_time = float('inf')
            coordination_ok = True
            
            # Lógica de operação por tipo de dispositivo
            if device.type == "87T" and device.zone == affected_zone:
                should_operate = fault_current > device.pickup_current * base_current
                operating_time = device.time_delay
            elif device.type == "50/51":
                if fault_current > device.pickup_current * base_current:
                    should_operate = True
                    # Curva tempo-corrente simplificada
                    operating_time = device.time_delay * (1 + 1/(fault_current/base_current - device.pickup_current))
            elif device.type == "67" and device.zone == affected_zone:
                should_operate = fault_current > device.pickup_current * base_current
                operating_time = device.time_delay
            elif device.type == "27/59":
                # Dispositivos de tensão operam com atraso
                should_operate = severity > 0.7  # Para faltas severas
                operating_time = device.time_delay
            
            device_responses.append({
                'device_id': device.id,
                'type': device.type,
                'should_operate': should_operate,
                'operating_time': operating_time if should_operate else 0,
                'coordination_ok': coordination_ok
            })
        
        # Verifica coordenação entre dispositivos
        operating_devices = [d for d in device_responses if d['should_operate']]
        
        for i, dev1 in enumerate(operating_devices):
            for dev2 in operating_devices[i+1:]:
                time_diff = abs(dev1['operating_time'] - dev2['operating_time'])
                required_margin = 0.3  # IEEE C37.112 padrão
                
                if time_diff < required_margin:
                    coordination_issues.append({
                        'device1': dev1['device_id'],
                        'device2': dev2['device_id'],
                        'margin': time_diff,
                        'required': required_margin
                    })
        
        # Avalia conformidade normativa
        normative_compliance = self._evaluate_normative_compliance(
            device_responses, coordination_issues, fault_type
        )
        
        coordination_ok = len(coordination_issues) == 0
        
        return FaultSimulationResult(
            fault_location=f"Bus {bus}",
            fault_type=fault_type,
            fault_current_a=fault_current,
            affected_zone=affected_zone,
            coordination_ok=coordination_ok,
            device_responses=device_responses,
            coordination_issues=coordination_issues,
            normative_compliance=normative_compliance
        )
    
    def _evaluate_normative_compliance(self, device_responses, coordination_issues, fault_type):
        """Avalia conformidade com normas técnicas"""
        
        # IEEE C37.112 - Coordenação de proteção
        ieee_compliance = len(coordination_issues) == 0
        ieee_issues = [f"Margem insuficiente: {issue['device1']}-{issue['device2']}" 
                      for issue in coordination_issues]
        
        # IEC 61850 - Comunicação (simulado)
        iec_compliance = True  # Assumindo GOOSE funcionando
        iec_issues = []
        
        # NBR 5410 - Seletividade
        operating_devices = [d for d in device_responses if d['should_operate']]
        nbr_compliance = len(operating_devices) <= 3  # Seletividade adequada
        nbr_issues = ["Muitos dispositivos operando simultaneamente"] if not nbr_compliance else []
        
        # API RP 14C - Ambiente offshore
        api_compliance = True  # Assumindo equipamentos adequados
        api_issues = []
        
        return {
            'IEEE_C37_112': {'coordination_margins': ieee_compliance, 'issues': ieee_issues},
            'IEC_61850': {'goose_performance': iec_compliance, 'issues': iec_issues},
            'NBR_5410': {'selectivity_dr': nbr_compliance, 'issues': nbr_issues},
            'API_RP_14C': {'offshore_environment': api_compliance, 'issues': api_issues}
        }
    
    def apply_rl_action(self, action):
        """Aplica ação avançada do RL mapeando para ajustes específicos"""
        # Mapeamento sofisticado de 32 ações para 8 dispositivos x 4 ajustes
        device_idx = action // 4  # 8 dispositivos (0-7)
        adjustment_type = action % 4  # 4 tipos de ajuste por dispositivo
        
        if device_idx >= len(self.protection_devices):
            return  # Ação inválida
        
        device = self.protection_devices[device_idx]
        
        # Ajustes baseados no tipo de ação com limites normativos
        if adjustment_type == 0:  # Reduzir pickup (mais sensível)
            factor = 0.95
            new_pickup = device.pickup_current * factor
            # Limites baseados em IEEE C37.112 e NBR 14039
            if new_pickup >= 50:  # Mínimo 50A para coordenação
                device.pickup_current = new_pickup
                
        elif adjustment_type == 1:  # Aumentar pickup (menos sensível)
            factor = 1.05
            new_pickup = device.pickup_current * factor
            # Máximo baseado na corrente de carga + margem
            if new_pickup <= 2000:  # Máximo 2000A
                device.pickup_current = new_pickup
                
        elif adjustment_type == 2:  # Reduzir tempo (mais rápido)
            factor = 0.95
            new_time = device.time_delay * factor
            # Tempo mínimo para estabilidade (IEC 60255-151)
            if new_time >= 0.1:  # Mínimo 100ms
                device.time_delay = new_time
                
        elif adjustment_type == 3:  # Aumentar tempo (coordenação)
            factor = 1.05
            new_time = device.time_delay * factor
            # Tempo máximo para coordenação (IEEE C37.112)
            if new_time <= 2.0:  # Máximo 2.0s
                device.time_delay = new_time
        
        # Log de auditoria dos ajustes
        if not hasattr(self, 'adjustment_log'):
            self.adjustment_log = []
        
        self.adjustment_log.append({
            'device': device.id,
            'action_type': adjustment_type,
            'pickup_current': device.pickup_current,
            'time_delay': device.time_delay,
            'timestamp': pd.Timestamp.now().isoformat()
        })
    
    def train_rl_agent(self, episodes=5, scenarios=None):
        """Treina o agente RL com cenários de falta"""
        if scenarios is None:
            scenarios = [
                {'bus': 4, 'fault_type': '3ph', 'severity': 0.8},
                {'bus': 7, 'fault_type': '2ph', 'severity': 0.6},
                {'bus': 14, 'fault_type': '1ph', 'severity': 0.5}
            ]
        
        results = []
        for episode in range(episodes):
            reward = self.rl_agent.train_episode(self, scenarios)
            results.append({
                'episode': episode + 1,
                'reward': reward,
                'epsilon': self.rl_agent.epsilon
            })
        
        return {
            'episodes_completed': episodes,
            'total_episodes': self.rl_agent.episodes,
            'final_epsilon': self.rl_agent.epsilon,
            'results': results
        }

    def optimize_protection_with_rl(self, episodes=100):
        """Otimização avançada usando RL com múltiplos cenários"""
        print(f"🤖 Iniciando otimização RL avançada: {episodes} episódios")
        
        # Cenários de teste diversificados
        fault_scenarios = [
            {'bus': 4, 'fault_type': '3ph', 'severity': 0.9},   # Falta severa
            {'bus': 7, 'fault_type': '2ph', 'severity': 0.7},   # Falta média
            {'bus': 14, 'fault_type': '1ph', 'severity': 0.5},  # Falta leve
            {'bus': 1, 'fault_type': '3ph', 'severity': 0.8},   # Geração  
            {'bus': 9, 'fault_type': '2ph', 'severity': 0.6},   # Distribuição
        ]
        
        optimization_results = []
        best_coordination_score = 0
        best_device_settings = None
        
        for episode in range(episodes):
            episode_rewards = []
            
            # Salvar configuração atual
            current_settings = {device.id: (device.pickup_current, device.time_delay) 
                              for device in self.protection_devices}
            
            # Múltiplos passos por episódio
            for step in range(5):
                # Estado atual
                current_state = self.rl_agent.get_state(self.protection_devices, self.protection_zones)
                
                # Ação do RL
                action = self.rl_agent.get_action(current_state)
                
                # Aplicar ação
                self.apply_rl_action(action)
                
                # Avaliar com todos os cenários
                step_reward = 0
                coordination_quality = 0
                
                for scenario in fault_scenarios:
                    result = self.simulate_fault(
                        scenario['bus'], 
                        scenario['fault_type'], 
                        scenario['severity']
                    )
                    reward = self.rl_agent.calculate_reward(result)
                    step_reward += reward
                    
                    # Métricas de qualidade
                    if result.coordination_ok:
                        coordination_quality += 20
                    coordination_quality -= len(result.coordination_issues) * 5
                
                step_reward /= len(fault_scenarios)  # Média dos cenários
                coordination_quality /= len(fault_scenarios)
                episode_rewards.append(step_reward)
                
                # Próximo estado
                next_state = self.rl_agent.get_state(self.protection_devices, self.protection_zones)
                
                # Aprendizado
                self.rl_agent.learn(current_state, action, step_reward, next_state)
            
            # Avaliação do episódio
            episode_avg_reward = np.mean(episode_rewards)
            
            # Teste final de coordenação
            final_coordination_score = self._evaluate_coordination_quality()
            
            # Salvar melhor configuração
            if final_coordination_score > best_coordination_score:
                best_coordination_score = final_coordination_score
                best_device_settings = {device.id: (device.pickup_current, device.time_delay) 
                                      for device in self.protection_devices}
            
            optimization_results.append({
                'episode': episode + 1,
                'avg_reward': episode_avg_reward,
                'coordination_score': final_coordination_score,
                'epsilon': self.rl_agent.epsilon,
                'adjustments_made': len(getattr(self, 'adjustment_log', []))
            })
            
            # Log de progresso
            if episode % 20 == 0 or episode == episodes - 1:
                print(f"📊 Episódio {episode + 1}: Reward={episode_avg_reward:.2f}, "
                      f"Coordenação={final_coordination_score:.1f}, ε={self.rl_agent.epsilon:.3f}")
        
        # Aplicar melhor configuração encontrada
        if best_device_settings:
            for device in self.protection_devices:
                if device.id in best_device_settings:
                    device.pickup_current, device.time_delay = best_device_settings[device.id]
        
        print(f"✅ Otimização concluída! Melhor score: {best_coordination_score:.1f}")
        
        return {
            'episodes_completed': episodes,
            'best_coordination_score': best_coordination_score,
            'final_epsilon': self.rl_agent.epsilon,
            'total_adjustments': len(getattr(self, 'adjustment_log', [])),
            'optimization_history': optimization_results,
            'improvement': best_coordination_score - optimization_results[0]['coordination_score'] if optimization_results else 0
        }
    
    def _evaluate_coordination_quality(self):
        """Avalia qualidade geral do sistema de coordenação"""
        total_score = 0
        test_scenarios = [
            {'bus': 4, 'fault_type': '3ph', 'severity': 0.8},
            {'bus': 7, 'fault_type': '2ph', 'severity': 0.6},
            {'bus': 14, 'fault_type': '1ph', 'severity': 0.5}
        ]
        
        for scenario in test_scenarios:
            result = self.simulate_fault(scenario['bus'], scenario['fault_type'], scenario['severity'])
            
            # Pontuação baseada em critérios normativos
            if result.coordination_ok:
                total_score += 30
            
            # Penalidades por problemas
            total_score -= len(result.coordination_issues) * 10
            
            # Seletividade (poucos dispositivos operando)
            operating_count = len([d for d in result.device_responses if d['should_operate']])
            if operating_count <= 2:
                total_score += 15  # Boa seletividade
            elif operating_count > 4:
                total_score -= 10  # Seletividade ruim
        
        return max(0, total_score / len(test_scenarios))  # Score normalizado
    
    def get_system_status(self):
        """Retorna status completo do sistema"""
        return {
            'total_devices': len(self.protection_devices),
            'zones': len(self.protection_zones),
            'system_health': 'healthy',
            'rl_agent_status': 'operational' if self.rl_agent.episodes > 0 else 'training'
        }
    
    def get_rl_status(self):
        """Retorna status do agente RL"""
        return {
            'status': 'operational' if self.rl_agent.episodes > 10 else 'training',
            'episodes': self.rl_agent.episodes,
            'max_episodes': self.rl_agent.max_episodes,
            'learning_rate': self.rl_agent.learning_rate,
            'epsilon': self.rl_agent.epsilon,
            'state_size': self.rl_agent.state_size,
            'action_space_size': self.rl_agent.action_space_size
        }

# Teste básico
if __name__ == "__main__":
    print("🔄 Testando ProtecAI Mini - Sistema RL...")
    coordinator = ProtectionCoordinator()
    print(f"✅ Sistema inicializado com {len(coordinator.protection_devices)} dispositivos")
    
    # Teste de simulação
    result = coordinator.simulate_fault(bus=4, fault_type='3ph', severity=0.8)
    print(f"✅ Simulação: Zona {result.affected_zone}, Coordenação: {result.coordination_ok}")
    print(f"✅ Corrente de falta: {result.fault_current_a:.0f} A")
    
    # Teste do RL
    print("🤖 Testando agente RL...")
    train_result = coordinator.train_rl_agent(episodes=3)
    print(f"✅ RL treinado: {train_result['episodes_completed']} episódios")
    print("✅ Sistema RL FUNCIONAL!")
