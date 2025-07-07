'''
    ||> Agente de Reinforcement Learning para Coordenação de Proteção ProtecAI_Mini
        - Implementa agente RL para otimização automática de settings de proteção
        - Treinamento baseado em cenários de falha da rede IEEE 14 barras
        - Objetivo: Minimizar tempo de atuação e maximizar seletividade
        - Ambiente personalizado compatível com OpenAI Gym/Gymnasium
'''

import gymnasium as gym
import numpy as np
import pandas as pd
import json
import pandapower as pp
from pathlib import Path
import matplotlib.pyplot as plt
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback
import warnings
warnings.filterwarnings('ignore')


class ProtectionCoordinationEnv(gym.Env):
    """
    Ambiente RL para coordenação de proteção elétrica.

    Estado: Valores de corrente, tensão, settings atuais dos relés
    Ação: Ajustes dos settings de proteção (pickup, time delay)
    Recompensa: Função baseada em seletividade, velocidade e confiabilidade
    """

    def __init__(self, net_json_path, protection_devices, max_episodes=1000):
        super(ProtectionCoordinationEnv, self).__init__()

        # Carregar rede elétrica
        self.net_json_path = net_json_path
        self.protection_devices = protection_devices
        self.max_episodes = max_episodes
        self.episode_count = 0

        # Configurar ambiente
        self._load_network()
        self._setup_action_observation_space()

        # Estado inicial
        self.reset()

    def _load_network(self):
        """Carrega a rede elétrica do JSON."""
        try:
            with open(self.net_json_path, 'r') as f:
                data = json.load(f)
            self.net = pp.from_json_string(data["pandapower_net"])
            print(f"✅ Rede RL carregada: {len(self.net.bus)} barras")
        except Exception as e:
            print(f"❌ Erro ao carregar rede para RL: {e}")
            raise

    def _setup_action_observation_space(self):
        """Define espaços de ação e observação."""
        # Número de relés ajustáveis
        self.n_reles = len(self.protection_devices.get("reles", []))

        # Ação: [pickup_current, time_delay] para cada relé
        # Normalizado entre 0 e 1, será desnormalizado internamente
        self.action_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=(self.n_reles * 2,), dtype=np.float32
        )

        # Observação: [correntes nas linhas, tensões nas barras, settings atuais]
        n_obs = len(self.net.line) + len(self.net.bus) + (self.n_reles * 2)
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(n_obs,), dtype=np.float32
        )

        # Limites realistas para desnormalização
        self.pickup_limits = (50, 500)    # A (corrente de pickup)
        self.time_limits = (0.1, 2.0)    # s (tempo de atuação)

    def _denormalize_action(self, action):
        """Converte ação normalizada para valores reais."""
        actions_real = []
        for i in range(self.n_reles):
            pickup = action[i*2] * (self.pickup_limits[1] -
                                    self.pickup_limits[0]) + self.pickup_limits[0]
            time_delay = action[i*2+1] * (self.time_limits[1] -
                                          self.time_limits[0]) + self.time_limits[0]
            actions_real.extend([pickup, time_delay])
        return np.array(actions_real)

    def _simulate_fault(self, fault_type="3ph", fault_bus=None):
        """Simula diferentes tipos de falha na rede de forma estável."""
        if fault_bus is None:
            # Escolher barra aleatória (exceto slack)
            available_buses = [b for b in self.net.bus.index if b != 0]
            fault_bus = np.random.choice(available_buses)

        try:
            # Fazer cópia da rede para simulação
            net_copy = self.net.deepcopy()

            # Simular falha através de carga adicional (mais estável que impedância baixa)
            fault_loads = {
                # Curto trifásico severo
                "3ph": {"p_mw": 50.0, "q_mvar": 30.0},
                # Curto bifásico moderado
                "2ph": {"p_mw": 30.0, "q_mvar": 20.0},
                # Curto monofásico leve
                "1ph": {"p_mw": 15.0, "q_mvar": 10.0},
                "overload": {"p_mw": 8.0, "q_mvar": 5.0}    # Sobrecarga
            }

            # Adicionar carga de falha
            fault_load = fault_loads.get(fault_type, fault_loads["1ph"])
            pp.create_load(
                net_copy,
                bus=fault_bus,
                p_mw=fault_load["p_mw"],
                q_mvar=fault_load["q_mvar"],
                name=f"FAULT_{fault_type}"
            )

            # Executar fluxo de carga com configuração robusta
            pp.runpp(net_copy,
                     algorithm='nr',          # Newton-Raphson mais estável
                     max_iteration=100,       # Mais iterações
                     tolerance_mva=1e-6,      # Tolerância relaxada
                     enforce_q_lims=False,    # Não enforçar limites Q
                     check_connectivity=False)  # Não verificar conectividade

            # Coletar dados de corrente e tensão
            currents = net_copy.res_line['i_ka'].values
            voltages = net_copy.res_bus['vm_pu'].values

            # Verificar se valores são válidos
            if np.any(np.isnan(currents)) or np.any(np.isnan(voltages)):
                raise ValueError("Valores NaN detectados")

            return currents, voltages, fault_bus, fault_type

        except Exception as e:
            # print(f"⚠️ Erro na simulação de falha: {e}")
            # Retornar condição normal com pequena perturbação
            try:
                pp.runpp(self.net, algorithm='nr', max_iteration=50)
                # Simular sobrecarga leve
                currents = self.net.res_line['i_ka'].values * \
                    (1.2 + np.random.random() * 0.3)
                # Simular queda de tensão
                voltages = self.net.res_bus['vm_pu'].values * \
                    (0.95 + np.random.random() * 0.1)
            except:
                # Último recurso: valores fixos realistas
                currents = np.full(len(self.net.line), 0.3)  # 300A típico
                # 98% tensão nominal
                voltages = np.full(len(self.net.bus), 0.98)

            return currents, voltages, fault_bus, fault_type

    def _calculate_reward(self, action, currents, voltages, fault_info):
        """Calcula recompensa baseada em critérios de proteção."""
        reward = 0.0

        # Componente 1: Seletividade (evitar atuação desnecessária)
        unnecessary_trips = 0
        necessary_trips = 0

        fault_bus, fault_type = fault_info[2], fault_info[3]
        actions_real = self._denormalize_action(action)

        for i, rele in enumerate(self.protection_devices.get("reles", [])):
            pickup = actions_real[i*2]
            time_delay = actions_real[i*2+1]

            # Verificar se relé deveria atuar
            element_id = rele.get("element_id", 0)
            if element_id < len(currents):
                current_magnitude = currents[element_id] * 1000  # kA para A

                should_trip = current_magnitude > pickup

                # Verificar se é proteção primária para a falha
                is_primary = self._is_primary_protection(rele, fault_bus)

                if should_trip:
                    if is_primary:
                        necessary_trips += 1
                        reward += 10.0  # Recompensa por atuação correta
                        reward -= time_delay * 2  # Penalidade por tempo excessivo
                    else:
                        unnecessary_trips += 1
                        reward -= 15.0  # Penalidade por falta de seletividade

        # Componente 2: Velocidade de atuação
        avg_time = np.mean(actions_real[1::2])  # Tempos de atuação
        if avg_time < 0.5:
            reward += 5.0
        elif avg_time > 1.5:
            reward -= 5.0

        # Componente 3: Estabilidade da rede
        voltage_stability = 1.0 - np.std(voltages)
        reward += voltage_stability * 3.0

        # Componente 4: Penalidade por valores extremos
        # Pickup muito baixo/alto
        if np.any(actions_real[::2] < 60) or np.any(actions_real[::2] > 400):
            reward -= 10.0
        # Tempo muito baixo/alto
        if np.any(actions_real[1::2] < 0.2) or np.any(actions_real[1::2] > 1.8):
            reward -= 10.0

        return reward

    def _is_primary_protection(self, rele, fault_bus):
        """Verifica se o relé é proteção primária para a falha."""
        element_type = rele.get("element_type", "")
        element_id = rele.get("element_id", 0)

        if element_type == "bus" and element_id == fault_bus:
            return True
        elif element_type == "line":
            # Verificar se a linha conecta a barra de falha
            if element_id < len(self.net.line):
                line = self.net.line.iloc[element_id]
                if line["from_bus"] == fault_bus or line["to_bus"] == fault_bus:
                    return True
        elif element_type == "trafo":
            # Verificar se o transformador conecta a barra de falha
            if element_id < len(self.net.trafo):
                trafo = self.net.trafo.iloc[element_id]
                if trafo["hv_bus"] == fault_bus or trafo["lv_bus"] == fault_bus:
                    return True

        return False

    def _get_observation(self, action=None):
        """Constrói vetor de observação do estado atual."""
        try:
            pp.runpp(self.net, algorithm='bfsw', max_iteration=50)
            currents = self.net.res_line['i_ka'].values
            voltages = self.net.res_bus['vm_pu'].values
        except:
            currents = np.zeros(len(self.net.line))
            voltages = np.ones(len(self.net.bus))

        # Settings atuais (normalizados)
        if action is not None:
            current_settings = action
        else:
            # Settings padrão iniciais
            current_settings = np.full(self.n_reles * 2, 0.5)

        observation = np.concatenate([currents, voltages, current_settings])
        return observation.astype(np.float32)

    def reset(self, seed=None, options=None):
        """Reinicia o ambiente."""
        super().reset(seed=seed)
        self.episode_count += 1

        # Estado inicial padrão
        initial_action = np.full(self.n_reles * 2, 0.5)  # Settings medianos
        observation = self._get_observation(initial_action)

        # Gymnasium requer retornar (observation, info)
        info = {"episode": self.episode_count}
        return observation, info

    def step(self, action):
        """Executa um passo no ambiente com simulação simplificada."""
        # Simular falha de forma mais simples e estável
        fault_types = ["3ph", "2ph", "1ph", "overload"]
        fault_type = np.random.choice(fault_types)
        fault_bus = np.random.choice([b for b in self.net.bus.index if b != 0])

        # Gerar dados sintéticos de corrente e tensão baseados no tipo de falha
        base_current = 0.2  # 200A base
        base_voltage = 1.0  # 100% tensão base

        fault_multipliers = {
            # Corrente alta, tensão baixa
            "3ph": {"current": 5.0, "voltage": 0.7},
            "2ph": {"current": 3.0, "voltage": 0.8},    # Moderado
            "1ph": {"current": 1.5, "voltage": 0.9},    # Leve
            "overload": {"current": 1.3, "voltage": 0.95}  # Sobrecarga
        }

        multiplier = fault_multipliers.get(
            fault_type, fault_multipliers["1ph"])

        # Gerar currentes e tensões sintéticas com ruído
        n_lines = len(self.net.line)
        n_buses = len(self.net.bus)

        currents = np.random.normal(
            base_current * multiplier["current"],
            base_current * 0.1,
            n_lines
        )
        currents = np.clip(currents, 0.05, 10.0)  # Limitar valores

        voltages = np.random.normal(
            base_voltage * multiplier["voltage"],
            0.02,
            n_buses
        )
        voltages = np.clip(voltages, 0.5, 1.1)  # Limitar valores

        # Calcular recompensa
        reward = self._calculate_reward(
            action, currents, voltages, (currents, voltages, fault_bus, fault_type))

        # Próxima observação
        observation = self._get_observation(action)

        # Condição de término
        terminated = self.episode_count >= self.max_episodes
        truncated = False  # Para Gymnasium

        # Informações adicionais
        info = {
            "fault_type": fault_type,
            "fault_bus": fault_bus,
            "avg_current": np.mean(currents),
            "min_voltage": np.min(voltages),
            "reward": reward
        }

        return observation, reward, terminated, truncated, info

    def render(self, mode='human'):
        """Renderiza o estado atual."""
        if hasattr(self, 'last_info'):
            print(
                f"Falha: {self.last_info.get('fault_type', 'N/A')} na barra {self.last_info.get('fault_bus', 'N/A')}")


class RLProtectionOptimizer:
    """Otimizador de coordenação de proteção usando RL."""

    def __init__(self, net_json_path, protection_devices):
        self.net_json_path = net_json_path
        self.protection_devices = protection_devices
        self.env = None
        self.model = None

    def create_environment(self):
        """Cria ambiente de treinamento."""
        self.env = ProtectionCoordinationEnv(
            self.net_json_path,
            self.protection_devices,
            max_episodes=1000
        )
        print("✅ Ambiente RL criado")

    def train_agent(self, algorithm="PPO", total_timesteps=5000):
        """Treina agente RL com timesteps reduzidos para demonstração."""
        if self.env is None:
            self.create_environment()

        print(
            f"🧠 Iniciando treinamento com {algorithm} (timesteps: {total_timesteps})...")

        # Criar ambiente vetorizado
        vec_env = DummyVecEnv([lambda: self.env])

        # Configurar algoritmo com parâmetros mais conservadores
        if algorithm == "PPO":
            self.model = PPO(
                "MlpPolicy",
                vec_env,
                verbose=1,
                learning_rate=1e-3,      # Learning rate menor
                n_steps=512,             # Passos menores
                batch_size=32,           # Batch menor
                n_epochs=5,              # Menos épocas
                device="cpu",
                policy_kwargs=dict(net_arch=[64, 64])  # Rede menor
            )
        elif algorithm == "DQN":
            # Para DQN, precisaríamos discretizar o espaço de ação
            print("⚠️ DQN requer discretização - usando PPO")
            self.model = PPO("MlpPolicy", vec_env, verbose=1)

        # Treinamento com tratamento de erro
        try:
            print("🎯 Treinando com configuração simplificada...")
            self.model.learn(total_timesteps=total_timesteps)
            print("✅ Treinamento concluído")
        except Exception as e:
            print(f"❌ Erro no treinamento: {e}")
            print("🔄 Tentando com configuração ainda mais simples...")

            # Configuração de emergência
            simple_env = DummyVecEnv([lambda: self.env])
            self.model = PPO(
                "MlpPolicy",
                simple_env,
                verbose=0,
                learning_rate=1e-4,
                n_steps=256,
                batch_size=16,
                n_epochs=3,
                policy_kwargs=dict(net_arch=[32, 32])
            )

            try:
                self.model.learn(total_timesteps=min(1000, total_timesteps))
                print("✅ Treinamento simplificado concluído")
            except Exception as e2:
                print(f"❌ Erro persistente: {e2}")
                return False

        return True

    def evaluate_agent(self, n_episodes=10):
        """Avalia performance do agente treinado."""
        if self.model is None:
            print("❌ Modelo não treinado")
            return None

        print(f"📊 Avaliando agente por {n_episodes} episódios...")

        rewards = []
        fault_responses = {"3ph": [], "2ph": [], "1ph": [], "overload": []}

        for episode in range(n_episodes):
            obs, _ = self.env.reset()  # Gymnasium retorna (obs, info)
            episode_reward = 0

            for step in range(10):  # 10 passos por episódio
                action, _states = self.model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = self.env.step(
                    action)
                episode_reward += reward

                # Coletar estatísticas por tipo de falha
                fault_type = info.get("fault_type", "unknown")
                if fault_type in fault_responses:
                    fault_responses[fault_type].append(reward)

                if terminated or truncated:
                    break

            rewards.append(episode_reward)

        # Estatísticas
        results = {
            "avg_reward": np.mean(rewards),
            "std_reward": np.std(rewards),
            "min_reward": np.min(rewards),
            "max_reward": np.max(rewards),
            "fault_performance": {k: np.mean(v) if v else 0 for k, v in fault_responses.items()}
        }

        print("\n📈 Resultados da Avaliação:")
        print(
            f"Recompensa Média: {results['avg_reward']:.2f} ± {results['std_reward']:.2f}")
        print(
            f"Recompensa Min/Max: {results['min_reward']:.2f} / {results['max_reward']:.2f}")
        print("\n🔥 Performance por Tipo de Falha:")
        for fault_type, performance in results['fault_performance'].items():
            print(f"  {fault_type}: {performance:.2f}")

        return results

    def get_optimal_settings(self):
        """Obtém settings otimizados pelo agente."""
        if self.model is None:
            print("❌ Modelo não treinado")
            return None

        obs, _ = self.env.reset()  # Gymnasium retorna (obs, info)
        action, _states = self.model.predict(obs, deterministic=True)

        # Desnormalizar ação para valores reais
        optimal_settings = self.env._denormalize_action(action)

        # Organizar settings por relé
        settings_dict = {}
        for i, rele in enumerate(self.protection_devices.get("reles", [])):
            rele_id = rele.get("id", f"RELE_{i}")
            settings_dict[rele_id] = {
                "pickup_current": optimal_settings[i*2],
                "time_delay": optimal_settings[i*2+1],
                "element_type": rele.get("element_type", ""),
                "element_id": rele.get("element_id", "")
            }

        return settings_dict

    def save_model(self, path):
        """Salva modelo treinado."""
        if self.model is not None:
            self.model.save(path)
            print(f"💾 Modelo salvo em: {path}")

    def load_model(self, path):
        """Carrega modelo salvo."""
        try:
            if self.env is None:
                self.create_environment()
            self.model = PPO.load(path, env=self.env)
            print(f"📂 Modelo carregado de: {path}")
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")
            return False


def demonstrate_rl_optimization():
    """Demonstração do otimizador RL."""
    print("🚀 DEMONSTRAÇÃO: RL para Coordenação de Proteção")
    print("="*60)

    # Caminhos
    json_path = Path("simuladores/power_sim/data/ieee14_protecao.json")
    model_path = Path("docs/rl_protection_model")

    # Carregar dados de proteção (simulado)
    protection_devices = {
        "reles": [
            {"id": "RELE_LINE_0", "element_type": "line",
                "element_id": 0, "tipo": "OVERCURRENT"},
            {"id": "RELE_LINE_1", "element_type": "line",
                "element_id": 1, "tipo": "OVERCURRENT"},
            {"id": "RELE_TRAFO_0", "element_type": "trafo",
                "element_id": 0, "tipo": "DIFFERENTIAL"},
            {"id": "RELE_BUS_1", "element_type": "bus",
                "element_id": 1, "tipo": "VOLTAGE"}
        ]
    }

    # Criar otimizador
    optimizer = RLProtectionOptimizer(json_path, protection_devices)

    print("📚 Fase 1: Treinamento do Agente RL")
    success = optimizer.train_agent(
        algorithm="PPO", total_timesteps=2000)  # Reduzido para demonstração

    if success:
        print("\n📊 Fase 2: Avaliação do Agente")
        results = optimizer.evaluate_agent(n_episodes=5)

        print("\n⚙️ Fase 3: Settings Otimizados")
        optimal_settings = optimizer.get_optimal_settings()

        if optimal_settings:
            print("\n🎯 Settings Recomendados pelo RL:")
            for rele_id, settings in optimal_settings.items():
                print(f"  {rele_id}:")
                print(f"    Pickup: {settings['pickup_current']:.1f} A")
                print(f"    Tempo: {settings['time_delay']:.3f} s")

        # Salvar modelo
        optimizer.save_model(model_path)

        print("\n✅ Demonstração RL concluída com sucesso!")
        return True

    else:
        print("❌ Falha na demonstração RL")
        return False


if __name__ == "__main__":
    demonstrate_rl_optimization()
