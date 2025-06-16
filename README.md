
# PetroProtecAI Mini – Simulação do Projeto Petro_ProtecAI

Este projeto apresenta uma versão simplificada, porém tecnicamente estruturada, do Petro_ProtecAI, visando ilustrar o ciclo completo de desenvolvimento e integração entre Frontend, Backend, simulação elétrica com PandaPower, banco de dados PostgreSQL e CI/CD com GitHub Actions.

## 🎯 Objetivo

Demonstrar o fluxo completo e integrado de uma aplicação para simulação e análise preliminar de redes elétricas com foco em automação de ajustes de proteção, considerando os desafios técnicos reais encontrados em projetos industriais, como em plataformas de petróleo.

## 📌 Contexto e Abordagem

Este projeto utiliza o sistema IEEE 14 barras como base para experimentação, integrando simulação de faltas com técnicas de aprendizado por reforço (RL) para ajustar relés de proteção.

### PandaPower em Projetos Complexos: Aplicabilidade e Limitações

O PandaPower é uma biblioteca Python voltada para análise de sistemas de potência, combinando a flexibilidade do Python com o poder computacional do PYPOWER. Apesar de sua popularidade em contextos acadêmicos, ele apresenta limitações importantes em projetos industriais complexos, especialmente na modelagem e coordenação de dispositivos de proteção:

- Não possui suporte nativo para relés ANSI/IEC com curvas normalizadas (50/51/67/81).
- Não permite simulação dinâmica de lógicas de coordenação seletiva.
- A modelagem de proteção deve ser feita de forma simplificada e assumida via código externo.

Portanto, seu uso neste projeto é exclusivamente voltado à prototipagem de estratégias e validação estática preliminar.

### Configuração de Relés no Sistema IEEE 14 Barras

**Ausência de Relés no Modelo Padrão:** O sistema IEEE 14 barras não inclui ativos de proteção como relés em sua modelagem padrão. A topologia é composta por 14 barras, 5 geradores, 11 cargas e 20 linhas, mas os dados são orientados a fluxo de potência e tensões, sem contemplar explicitamente elementos de proteção.

**Limitação:** Isso dificulta a aplicação direta de algoritmos de RL para ajuste de relés. Para contornar:

- **Modelagem Adicional:** Inserir relés sintéticos nas linhas e barras, com curvas de tempo inverso, corrente de pickup, e parâmetros extraídos de normas (ex.: IEEE C37.113).
- **Simulação de Falhas:** Gerar cenários realistas de faltas e utilizar o PandaPower para observar a resposta da rede.

**Desafio Específico:** A simplicidade topológica do IEEE 14 barras limita tanto a complexidade da coordenação quanto a representatividade para sistemas reais.

**Solução Proposta:**
- Adicionar relés fictícios e simular seu comportamento.
- Usar RL para otimizar os parâmetros (como TMS e pickup).
- Validar os resultados com ferramentas mais robustas como DIgSILENT PowerFactory ou Matpower.

### Implementação de RL com IEEE 14 Barras: Cuidados e Estratégia

Para implementar o algoritmo RL:
- Os relés serão simulados externamente.
- As ações serão ajustes contínuos (pickup, TMS).
- O ambiente de aprendizado modelará correntes de curto-circuito, tensões e resposta dos relés.

### Penalidades e Recompensas no RL

**Problemas Identificados:**
- Funções de recompensa mal calibradas não capturam bem os trade-offs entre seletividade, rapidez e confiabilidade.
- Penalidades genéricas resultam em exploração arriscada.
- Espaço de ação contínuo e amplo dificulta a convergência.

**Refinamentos Propostos:**
- **Recompensa Multiobjetivo:**
  - Seletividade: premiar atuação apenas do relé mais próximo.
  - Rapidez: tempo mínimo sem perder coordenação.
  - Estabilidade: manter variáveis do sistema dentro dos limites.

  Fórmula exemplo:
  ```
  R = w1*(1 - desvio_tensão) + w2*(1 - tempo_ação) - w3*disparo_indesejado
  ```

- **Penalidades Granulares:**
  ```
  P = -k1*(sobrecarga)^2 - k2*(desvio_tensão)^2 - k3*(falha_coordenação)
  ```

- **Exploração Controlada:**
  - Uso de PPO ou DDPG.
  - Restringir espaço de ação a limites realistas (ex: 0.5–2.0 pu).

- **Validação com Simulações:**
  - Testes com Matpower e PSS/E.
  - Ajustes iterativos na função de recompensa.

**Riscos e Cuidados:**
- Recompensas imprecisas podem priorizar rapidez em detrimento da seletividade.
- A convergência lenta pode comprometer a utilidade operacional.
- Começar com IEEE 14 barras e migrar para IEEE 39 após validação.

### Ferramentas utilizadas:

- **PandaPower** para simulação de fluxo de potência e faltas.
- **Gymnasium** como interface de ambiente RL customizado.
- **Stable-Baselines3** com o algoritmo PPO (Proximal Policy Optimization), ideal para otimizações em espaços contínuos.

## 🚀 Estrutura do Projeto

```bash
petro_protecai_mini/
├── src/
│   ├── backend/
│   │   ├── api/
│   │   │   ├── routers/
│   │   │   └── main.py
│   │   ├── services/
│   │   │   └── simulacao.py
│   │   └── database/
│   │       └── models.py
│   └── frontend/
│       └── petro-protecai-frontend/
│           ├── index.html
│           ├── vite.config.ts
│           ├── src/
│           │   ├── App.tsx
│           │   ├── main.tsx
│           │   └── index.css
├── docs/
│   └── Guias, documentação técnica e relatórios
├── simuladores/
│   └── pandapower/
│       └── scripts_simulacao.py
├── infra/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/
│   ├── test_api.py
│   └── test_simulation.py
├── .github/
│   └── workflows/
│       └── ci_cd.yml
└── README.md
```

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.12.5, FastAPI
- **Frontend**: React, TypeScript
- **Banco de Dados**: PostgreSQL
- **Simulador**: PandaPower (Rede IEEE 14 barras)
- **Aprendizado por Reforço**: Gymnasium, Stable-Baselines3
- **Infraestrutura**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## 🗃️ Configuração do Ambiente

### Requisitos
- Docker e Docker Compose
- Python 3.12.5
- Node.js (para frontend)

### Inicializando o ambiente

Clone o repositório:
```bash
git clone <url_repositorio>
cd petro_protecai_mini
```

Inicialize o backend e banco PostgreSQL:
```bash
cd infra/
docker-compose up --build
```

Frontend (instalar e rodar):
```bash
cd frontend/
npm install
npm run dev
```

## ⚙️ Backend – FastAPI

O backend oferece endpoints REST para comunicação com a simulação.

### Estrutura Modular

- **api/main.py** – ponto de entrada principal da API.
- **routers/** – definição de rotas REST.
- **services/simulacao.py** – lógica de negócio das simulações.
- **database/models.py** – estrutura das tabelas com SQLAlchemy.

### Rodando localmente
```bash
cd backend/
uvicorn api.main:app --reload
```

Acesse documentação interativa: `http://localhost:8000/docs`

## 📊 Simulador – PandaPower

Utilizamos PandaPower com a rede IEEE 14 barras para demonstrar as capacidades de simulação e fluxo de potência.

Exemplo de execução:
```bash
python simuladores/pandapower/scripts_simulacao.py
```

## 🌐 Frontend – React

Interface responsiva para interação e visualização dos resultados.

- Visualização gráfica dos resultados
- Entrada dinâmica de dados da rede elétrica

Rodando frontend:
```bash
cd frontend/
npm run dev
```
Acesse via: `http://localhost:3000`

## 📦 Docker

Infraestrutura local com Docker:
- PostgreSQL (armazenamento persistente)
- Backend FastAPI

Comandos úteis:
```bash
docker-compose up --build  # inicializa todo ambiente
docker-compose down        # encerra ambiente
```

## 🔄 Integração Contínua (CI/CD)

GitHub Actions configurado para automação:
- Testes unitários backend
- Build frontend/backend
- Deploy (futuro ambiente de staging)

Exemplo do workflow:
```yaml
.github/workflows/ci_cd.yml
```

## 📁 Estrutura de Banco de Dados

O PostgreSQL gerencia dados das simulações:
- Dados de entrada das simulações
- Resultados armazenados para análise posterior

## 📌 Limitações do PandaPower

Este projeto é destinado a fins acadêmicos e demonstração, devido às limitações do PandaPower para aplicações industriais complexas, destacadamente nas áreas de proteção e coordenação seletiva (ANSI/IEC 50/51/67/81).

## 🧪 Testes

Execute testes automatizados com Pytest:
```bash
cd tests/
pytest
```

## 🎯 Instalando bibliotecas

```bash
# Instalar dependências de produção
pip install -r requirements.txt

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

```

## 🎯 Roadmap futuro

- Implementação de autenticação JWT
- Deploy em ambiente de staging
- Expansão das simulações com novos cenários
- Melhoria contínua da documentação

## 📄 Contribuição

- Crie uma nova branch para suas alterações
- Realize Pull Request descrevendo claramente as modificações

## 📌 Licença

Este projeto é distribuído sob a licença MIT.

---

Desenvolvido por: Equipe Petro_ProtecAI Mini 🚀
