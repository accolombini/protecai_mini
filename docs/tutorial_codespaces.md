# Tutorial: Trabalhando com GitHub Codespaces no iPad (ou em qualquer dispositivo)

Este guia ensina como acessar, configurar e usar o **GitHub Codespaces**, uma plataforma de desenvolvimento em nuvem baseada no Visual Studio Code, ideal para mobilidade e produtividade em projetos como o **ProtecAI_mini**.

---

## 1. ❌ Pré-requisitos

- Conta no GitHub (preferencialmente com plano Pro ou Codespaces ativado).
- Repositório com seu projeto hospedado (ex: `protecai_mini`).
- Acesso a um navegador moderno (Safari ou Chrome no iPad funciona perfeitamente).
- Teclado físico (opcional, mas altamente recomendado no iPad).

---

## 2. 🌐 Acessar o GitHub Codespaces

1. Acesse: [https://github.com/codespaces](https://github.com/codespaces).
2. Clique em **"New codespace"**.
3. Selecione o repositório desejado (ex: `protecai_mini`).
4. Escolha a branch (ex: `main`) e clique em **"Create codespace"**.

O ambiente será iniciado com uma instância completa do VS Code, acessível no navegador.

---

## 3. 🛠️ Trabalhando com o Código

- No painel esquerdo, você verá toda a estrutura do projeto.
- Clique nos arquivos `.py`, `.md`, `.yaml` ou outros para editar.
- O terminal (bash) estará pronto na parte inferior.

### Comandos úteis:
```bash
python3 --version               # Verifica a versão do Python
pip install -r requirements.txt  # Instala dependências do projeto
python main.py                  # Executa o projeto
pytest tests/                   # Roda os testes automatizados
```

---

## 4. 📦 Instalando dependências

Caso o projeto não esteja com dependências instaladas:
```bash
pip install -r requirements.txt
```

Você pode editar o `requirements.txt` normalmente e reinstalar, se necessário.

---

## 5. 🐳 (Opcional) Criando um ambiente customizado com `.devcontainer/`

Para garantir consistência e controle de versão do Python, crie os seguintes arquivos:

### Estrutura:
```
.devcontainer/
├── devcontainer.json
└── Dockerfile
```

### `devcontainer.json`
```json
{
  "name": "ProtecAI_Mini",
  "build": {
    "dockerfile": "Dockerfile"
  },
  "postCreateCommand": "pip install -r requirements.txt",
  "customizations": {
    "vscode": {
      "extensions": ["ms-python.python", "ms-toolsai.jupyter"]
    }
  }
}
```

### `Dockerfile`
```Dockerfile
FROM python:3.12.5-slim

WORKDIR /workspace

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt
```

Salve e faça push para o GitHub. Na próxima abertura no Codespaces, o ambiente virá pronto com Python e bibliotecas instaladas.

---

## 6. ✅ Salvando e versionando seu trabalho

Use o terminal ou Git GUI no VS Code para versionar:
```bash
git add .
git commit -m "Update script"
git push origin main
```

---

## 7. 📱 Benefícios no iPad

- VS Code completo via navegador.
- Nenhuma instalação local.
- Perfeito para viagens ou trabalho remoto.
- Suporte a extensões, Git, terminal e syntax highlight.
- Leve e responsivo.

---

## 🎯 Dicas Finais

- Use teclado bluetooth para aumentar produtividade no iPad.
- Ative o modo escuro do GitHub para maior conforto visual.
- Combine com GitHub Projects para gerenciar tarefas do projeto.

---

**Pronto!** A partir daí pode-se desenvolver projetos completos com Python, FastAPI, RL e simulações elétricas — direto do  iPad com estabilidade e elegância.
