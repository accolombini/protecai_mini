
# Tutorial de Coordenação da Proteção no Projeto ProtecAI_Mini

## 1. Introdução
Este tutorial tem como objetivo orientar a configuração dos dispositivos de proteção elétrica no projeto **ProtecAI_Mini**, com base em uma versão customizada da rede IEEE 14 barras. A coordenação da proteção será realizada considerando duas zonas principais — uma para cada transformador de 25 MVA, 13.8 kV — e integrará algoritmos de aprendizado por reforço (RL) para detecção, ação e adaptação diante de falhas.

## 2. Dispositivos de Proteção Envolvidos

Os principais dispositivos usados na simulação do ProtecAI_Mini são:

| Tipo de Dispositivo | Função Principal                                       | Barras Relacionadas |
|---------------------|--------------------------------------------------------|---------------------|
| Relé 87T (Diferencial) | Proteção dos transformadores                         | Barra 0–4 e 1–5     |
| Relé 50/51 (Sobrecorrente) | Proteção de feeders e linhas                    | Entre barras 4–5–6  |
| Disjuntores temporizados | Isolamento automático após atuação do relé        | Saídas dos trafos   |
| Fusíveis simulados   | Redundância em cargas secundárias                    | Cargas nas barras 9–10–14 |

## 3. Parâmetros de Configuração

### 3.1 Relé 87T – Diferencial de Transformador
- **Corrente de operação**: 0.3–0.6 pu (ajustada por faixa de carga nominal)
- **Tempo de atuação**: Instantâneo (0.0 s)
- **Zona de proteção**: Exclusiva entre a barra de entrada e saída do trafo

### 3.2 Relé 50/51 – Sobrecorrente Temporizado
- **Pickup (corrente de atuação)**: 1.2× In
- **Tempo de retardo (curva)**: IEC 60255 – Curva Inversa Moderada
- **Coordenação**: Ajustado com seletividade para proteger a jusante sem atuar indevidamente na barra adjacente

### 3.3 Disjuntores Temporizados
- **Tempo de abertura**: 0.1 s após sinal de atuação do relé
- **Reset manual**: Via frontend ou lógica de RL
- **Redundância**: Pode ser bloqueado por lógica de RL em caso de falha prevista

## 4. Estratégia de Testes

### 4.1 Testes Unitários de Atuação
- Falha em barra alimentada por transformador 1 (barra 4)
- Falha entre barras 4 e 5 (curto de fase-terra)
- Verificação se apenas zona Z1 atua e mantém estabilidade do restante

### 4.2 Testes de Reconfiguração
- Queima simulada de transformador 1 (sobrecarga ou falha interna)
- Remapeamento das cargas da zona Z1 para Z2 por lógica RL
- Reconfiguração das proteções do trafo 2

### 4.3 Testes com Aprendizado por Reforço (RL)
- Ambiente simulado com Pandapower + Gym
- Ações: mudar parâmetros dos relés, abrir/fechar disjuntores, isolar cargas
- Recompensas: evitar blackout, manter seletividade, minimizar interrupção

## 5. Integração com Frontend

### 5.1 Parametrização dos Dispositivos via Interface Web
- Formulários interativos para relés 87T, 51, disjuntores
- Atualização dinâmica de arquivos `.json` de configuração

### 5.2 Monitoramento
- Visualização em tempo real da topologia (matplotlib/plotly)
- Indicadores de falha, estado dos relés, disjuntores abertos/fechados

## 6. Recomendações Finais
- Iniciar com simulações determinísticas antes de aplicar RL
- Testar casos extremos e falhas sequenciais
- Usar logs para rastrear decisões do agente RL e validar contra lógica esperada

---

# Tabela Comparativa dos Estados Pós-Falha

| Cenário de Falha            | Dispositivo Atuante          | Impacto Esperado                                | Ação RL                                              |
| :-------------------------- | :--------------------------- | :---------------------------------------------- | :--------------------------------------------------- |
| Curto na Barra 4            | Relé 87T (Z1) + Disjuntor    | Isolamento do trafo 1, carga remanejada para Z2 | Reconfigurar carga, ajustar relés da Z2              |
| Curto entre barras 4 e 5    | Relé 50/51 + Disjuntor local | Isolamento seletivo do segmento                 | Ajustar seletividade, manter carga nas extremidades  |
| Queima do Trafo 2 (Barra 5) | Relé 87T (Z2) + Disjuntor    | Perda de Z2, possível sobrecarga em Z1          | Reduzir carga, religar segmentos com atraso          |
| Falha no disjuntor da Z1    | Relé 51 + Fusível            | Atuação de backup, pequena sobrecarga           | Registrar falha, revisar confiabilidade do disjuntor |


## Manual do Agente de Reforço (RL) – ProtecAI_Mini

### Espaço de Observações
- Estado das barras (tensão, carga, corrente)
- Status dos relés (ligado/desligado, pickup, tempo)
- Status dos disjuntores (aberto/fechado)
- Falhas detectadas (por tipo e localização)
- Zonas ativas e disponíveis

### Espaço de Ações
- Abrir/fechar disjuntores
- Ajustar parâmetros dos relés (pickup, tempo)
- Redirecionar carga entre zonas
- Isolar barra ou segmento

### Recompensas e Penalidades

| Evento                            | Recompensa (+) | Penalidade (-) |
| --------------------------------- | -------------- | -------------- |
| Atuação seletiva correta          | +10            | –              |
| Evitar blackout total             | +20            | –              |
| Tempo total de recomposição curto | +5             | –              |
| Desligamento de carga crítica     | –              | -20            |
| Atuação indevida de relé          | –              | -10            |
| Falha em atuar (não isolou curto) | –              | -30            |

### Estratégia de Atualização
- O agente usa feedback de cada simulação (falha → ação → consequência)
- As ações são registradas e avaliadas em logs
- A topologia pode ser atualizada via arquivo `.json` após cada episódio

---

**Observação**: A lógica do RL deve ser validada com testes determinísticos iniciais antes de ser liberada para exploração livre.

*Data de geração: 03/07/2025*
