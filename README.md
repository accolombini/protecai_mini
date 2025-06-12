
# PetroProtecAI Mini – Simulação do Projeto Petro_ProtecAI

Este projeto apresenta uma versão simplificada e modular do Petro_ProtecAI, visando ilustrar claramente o ciclo completo de desenvolvimento e integração entre Frontend, Backend, simulação elétrica com PandaPower, banco de dados PostgreSQL e CI/CD com GitHub Actions.

## 🎯 Objetivo

Demonstrar o fluxo completo e integrado de uma aplicação para simulação e visualização de redes elétricas, utilizando ferramentas e tecnologias modernas de desenvolvimento.

## 🚀 Estrutura do Projeto

```bash
petro_protecai_mini/
├── docs/
│   └── Guias, documentação técnica e relatórios
├── frontend/
│   └── Aplicação React com TypeScript
├── backend/
│   ├── api/
│   │   ├── routers/
│   │   └── main.py
│   ├── services/
│   │   └── simulacao.py
│   └── database/
│       └── models.py
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
