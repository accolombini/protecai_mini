# ProtecAI Mini - API REST Documentation

## 🎯 Visão Geral

A **ProtecAI Mini API** é uma interface REST completa para laboratório de coordenação de proteção elétrica com inteligência artificial. Permite parametrização dinâmica de dispositivos de proteção, execução de simulações, treinamento de agentes RL e geração de relatórios.

## 🚀 Início Rápido

### 1. Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 2. Geração dos Dados Iniciais

```bash
# Gerar dados da rede IEEE 14 barras
python simuladores/power_sim/gerar_ieee14_json.py

# Gerar visualização inicial
python simuladores/power_sim/visualizar_toplogia_protecao.py
```

### 3. Iniciar a API

```bash
# Opção 1: Script dedicado
python start_api.py

# Opção 2: Uvicorn diretamente
python -m uvicorn src.backend.api.main:app --reload

# Opção 3: Demonstração completa
python demo_api.py
```

### 4. Acessar a Documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📊 Estrutura da API

### 🏗️ Network (`/network`)
Gerenciamento da rede elétrica IEEE 14 barras.

#### Endpoints Principais:
- `GET /network/topology` - Topologia da rede
- `GET /network/status` - Status da rede
- `GET /network/buses` - Lista de barras
- `GET /network/lines` - Lista de linhas
- `PUT /network/buses/{bus_id}` - Atualizar barra
- `PUT /network/lines/{line_id}` - Atualizar linha

#### Exemplo de Uso:
```python
import requests

# Obter topologia
response = requests.get("http://localhost:8000/network/topology")
topology = response.json()

# Atualizar barra
bus_update = {"name": "Barra Principal", "vn_kv": 13.8}
response = requests.put(f"http://localhost:8000/network/buses/1", json=bus_update)
```

### 🛡️ Protection (`/protection`)
Gerenciamento de dispositivos de proteção.

#### Endpoints Principais:
- `GET /protection/devices` - Lista todos os dispositivos
- `GET /protection/devices/{type}` - Dispositivos por tipo
- `POST /protection/devices/{type}` - Criar dispositivo
- `PUT /protection/devices/{type}/{id}` - Atualizar dispositivo
- `GET /protection/zones` - Zonas de proteção
- `POST /protection/coordination/analyze` - Análise de coordenação

#### Exemplo de Uso:
```python
# Listar relés
response = requests.get("http://localhost:8000/protection/devices/reles")
relays = response.json()

# Criar novo relé
new_relay = {
    "id": "R_TEST",
    "element_type": "line",
    "element_id": 1,
    "tipo": "OVERCURRENT",
    "pickup_current": 100.0,
    "time_delay": 0.5,
    "enabled": True
}
response = requests.post("http://localhost:8000/protection/devices/reles", json=new_relay)

# Analisar coordenação
response = requests.post("http://localhost:8000/protection/coordination/analyze")
analysis = response.json()
```

### ⚡ Simulation (`/simulation`)
Simulação de falhas e análises.

#### Endpoints Principais:
- `POST /simulation/run` - Executar simulação completa
- `GET /simulation/status/{id}` - Status da simulação
- `GET /simulation/results/{id}` - Resultados da simulação
- `POST /simulation/quick-analysis` - Análise rápida
- `GET /simulation/templates` - Templates de simulação

#### Exemplo de Uso:
```python
# Simulação rápida
fault_config = {
    "fault_type": "short_circuit",
    "element_type": "bus",
    "element_id": 4,
    "fault_impedance": 0.01,
    "severity": "high"
}
response = requests.post("http://localhost:8000/simulation/quick-analysis", json=fault_config)
result = response.json()

# Simulação completa
simulation_config = {
    "name": "Teste Curto-circuito",
    "description": "Simulação de curto-circuito na barra 4",
    "faults": [fault_config]
}
response = requests.post("http://localhost:8000/simulation/run", json=simulation_config)
simulation_id = response.json()["simulation_id"]

# Monitorar progresso
response = requests.get(f"http://localhost:8000/simulation/status/{simulation_id}")
status = response.json()
```

### 🧠 Reinforcement Learning (`/rl`)
Treinamento e otimização com RL.

#### Endpoints Principais:
- `POST /rl/train` - Iniciar treinamento
- `GET /rl/training/status/{id}` - Status do treinamento
- `GET /rl/models` - Lista de modelos
- `POST /rl/models/{id}/predict` - Predição com modelo
- `POST /rl/models/{id}/optimize` - Otimização de settings

#### Exemplo de Uso:
```python
# Configurar treinamento
training_config = {
    "episodes": 1000,
    "learning_rate": 0.001,
    "discount_factor": 0.95,
    "epsilon_start": 1.0,
    "epsilon_end": 0.1,
    "epsilon_decay": 0.995
}
response = requests.post("http://localhost:8000/rl/train", json=training_config)
training_id = response.json()["training_id"]

# Monitorar treinamento
response = requests.get(f"http://localhost:8000/rl/training/status/{training_id}")
status = response.json()

# Usar modelo para predição
test_state = {
    "fault_current": 3000.0,
    "fault_location": 4,
    "system_loading": 0.7,
    "protection_settings": {},
    "network_topology": {}
}
response = requests.post(f"http://localhost:8000/rl/models/{training_id}/predict", json=test_state)
prediction = response.json()
```

### 📈 Visualization (`/visualization`)
Geração de visualizações e relatórios.

#### Endpoints Principais:
- `POST /visualization/generate` - Gerar visualização
- `GET /visualization/download/{filename}` - Download de arquivo
- `POST /visualization/report/generate` - Gerar relatório
- `GET /visualization/templates` - Templates disponíveis

#### Exemplo de Uso:
```python
# Gerar visualização da rede
viz_config = {
    "visualization_type": "network_topology",
    "parameters": {
        "show_protection_devices": True,
        "show_zones": True
    },
    "title": "Rede IEEE 14 Barras com Proteção"
}
response = requests.post("http://localhost:8000/visualization/generate", json=viz_config)
viz_result = response.json()

# Gerar relatório
report_config = {
    "report_type": "system_overview",
    "include_sections": ["summary", "analysis", "recommendations"],
    "output_format": "html"
}
response = requests.post("http://localhost:8000/visualization/report/generate", json=report_config)
report_result = response.json()
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```bash
# Configuração do servidor
export PROTECAI_HOST=0.0.0.0
export PROTECAI_PORT=8000
export PROTECAI_DEBUG=true

# Configuração de dados
export PROTECAI_DATA_PATH=simuladores/power_sim/data
export PROTECAI_MODELS_PATH=simuladores/power_sim/models
export PROTECAI_OUTPUT_PATH=docs
```

### Configuração do Banco de Dados (Futuro)

```python
# src/backend/database/config.py
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "protecai",
    "user": "protecai_user",
    "password": "protecai_pass"
}
```

## 🧪 Testes

### Executar Testes da API

```bash
# Testes completos
python test_api.py

# Testes específicos
python -m pytest tests/test_api.py -v
```

### Exemplo de Teste Custom

```python
import requests
import pytest

def test_network_topology():
    response = requests.get("http://localhost:8000/network/topology")
    assert response.status_code == 200
    data = response.json()
    assert data["total_buses"] == 14
    assert data["total_lines"] > 0

def test_protection_devices():
    response = requests.get("http://localhost:8000/protection/devices")
    assert response.status_code == 200
    data = response.json()
    assert "devices" in data
    assert "total_devices" in data

def test_simulation_quick_analysis():
    fault_config = {
        "fault_type": "short_circuit",
        "element_type": "bus",
        "element_id": 4,
        "severity": "medium"
    }
    response = requests.post("http://localhost:8000/simulation/quick-analysis", json=fault_config)
    assert response.status_code == 200
    data = response.json()
    assert "fault_analysis" in data
    assert "recommendations" in data
```

## 📚 Exemplos de Integração

### Cliente Python

```python
class ProtecAIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_network_status(self):
        response = requests.get(f"{self.base_url}/network/status")
        return response.json()
    
    def run_fault_simulation(self, fault_config):
        response = requests.post(f"{self.base_url}/simulation/quick-analysis", json=fault_config)
        return response.json()
    
    def train_rl_agent(self, config):
        response = requests.post(f"{self.base_url}/rl/train", json=config)
        return response.json()

# Uso
client = ProtecAIClient()
status = client.get_network_status()
print(f"Rede: {status['total_buses']} barras, {status['total_lines']} linhas")
```

### Cliente JavaScript

```javascript
class ProtecAIClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async getNetworkStatus() {
        const response = await fetch(`${this.baseUrl}/network/status`);
        return await response.json();
    }
    
    async runFaultSimulation(faultConfig) {
        const response = await fetch(`${this.baseUrl}/simulation/quick-analysis`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(faultConfig)
        });
        return await response.json();
    }
}

// Uso
const client = new ProtecAIClient();
client.getNetworkStatus().then(status => {
    console.log(`Rede: ${status.total_buses} barras, ${status.total_lines} linhas`);
});
```

## 🔍 Monitoramento e Logs

### Logs da API

```bash
# Logs detalhados
python -m uvicorn src.backend.api.main:app --log-level debug

# Logs em arquivo
python -m uvicorn src.backend.api.main:app --log-config logging.conf
```

### Health Check

```python
# Verificar saúde da API
response = requests.get("http://localhost:8000/health")
if response.status_code == 200:
    print("API está saudável")
else:
    print("API com problemas")
```

## 🚀 Deploy

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "src.backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  protecai-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PROTECAI_DEBUG=false
    volumes:
      - ./data:/app/data
      - ./docs:/app/docs
```

## 📞 Suporte

### Resolução de Problemas

1. **API não inicia**:
   - Verificar se a porta 8000 está disponível
   - Verificar se todas as dependências estão instaladas
   - Verificar se os arquivos de dados existem

2. **Erro 500 na API**:
   - Verificar logs do servidor
   - Verificar se o arquivo JSON da rede existe
   - Verificar permissões de arquivo

3. **Simulações não funcionam**:
   - Verificar se os scripts de simulação estão no PATH
   - Verificar dependências do PandaPower
   - Verificar dados da rede

### Contato

- **Email**: suporte@protecai.com
- **GitHub**: https://github.com/protecai/protecai-mini
- **Documentação**: https://docs.protecai.com

---

**ProtecAI Mini** - Laboratório Inteligente de Coordenação de Proteção Elétrica  
Versão 1.0.0 - 2024
