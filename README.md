# 📊 Simulador Financeiro  

## 📌 Visão Geral  
O **Simulador Financeiro** é uma aplicação interativa inspirada em jogos RTS como **Capitalism Lab e Victoria 3**, que permite testar estratégias de investimento no **mercado financeiro brasileiro**. O simulador inclui **renda fixa (CDB, LCI, LCA, Tesouro Direto)** e **renda variável (Ações, FIIs, ETFs)**, além de eventos econômicos dinâmicos, métricas de desempenho e suporte a múltiplas fontes de dados.  

O objetivo é oferecer um ambiente dinâmico para experimentação de estratégias de compra e venda de ativos, seja de forma automática ou manual.  

## 🎮 Modos de Jogo  

### 1️⃣ **Modo Automático** 📈  
- O tempo avança automaticamente, como em um RTS.  
- As compras e vendas são executadas conforme uma **estratégia de negociação programada**.  
- O usuário pode configurar e testar diferentes **algoritmos de investimento**.  

### 2️⃣ **Modo Manual** 🏦  
- O jogador pode **emitir ordens de compra e venda manualmente**.  
- O mercado segue em tempo real, e o usuário decide **quando intervir**.  
- O tempo pode ser pausado ou acelerado (**1x, 2x, 4x, 10x**).  

### 3️⃣ **Modo Multiplayer** 🌐  
- Permite **vários jogadores** competindo simultaneamente.  
- O jogo sincroniza eventos econômicos e tempo de simulação para todos os participantes.  
- O jogador com o maior patrimônio ao final vence.  

## 🔥 Funcionalidades Principais  

✅ **Simulação de negociações** (Ações, FIIs, ETFs) em tempo real.  
✅ **Investimentos em renda fixa** (CDB, LCI, LCA, Tesouro Direto).  
✅ **Fluxo de caixa mensal** (simulação de salário ou renda fixa recorrente).  
✅ **Análise de desempenho**: Retorno, drawdown, índice de Sharpe, etc.  
✅ **Eventos econômicos dinâmicos**: Crises, mudanças nos juros e inflação.  
✅ **Gráficos interativos** em **Plotly + Dash** para acompanhar a evolução do portfólio.  
✅ **Interface Web personalizada** via **Flask + Dash + CSS**.  
✅ **Suporte a múltiplas fontes de dados** (Yahoo Finance, MySQL, SQLite).  
✅ **Modo Multiplayer** com servidor cliente-servidor via **WebSockets**.  
✅ **Atualizações em tempo real** simulando ticks do mercado.  
✅ **Empacotamento como executável (.exe)** para facilitar a distribuição.  

## 🌐 Providers de Túnel

O Simulador Financeiro suporta diferentes formas de compartilhar a sessão de jogo multiplayer. Você pode escolher entre conectar localmente via LAN/VPN ou usar um túnel público:

### **Providers Garantidos** ✅

#### 1. **LAN** (Padrão)
Conecte-se diretamente via rede local ou VPN própria.

- **Detecção Automática**: Radmin VPN, LogMeIn Hamachi, Tailscale
- **Ideal para**: Usuários avançados, jogadores de Minecraft, grupos de amigos
- **Banda**: ✅ **Ilimitada** (zero limite)
- **Latência**: ✅ **Excelente**
- **Configuração**: 
  ```toml
  [tunnel]
  provider = "lan"
  port = 8000
  ```
- **Como usar**:
  1. Instale [Radmin VPN](https://www.radmin-vpn.com/) (gratuito)
  2. Crie uma rede ou entre em uma existente
  3. Inicie o simulador
  4. Compartilhe o IP detectado com seus amigos

---

#### 2. **LocalTunnel** (Em desenvolvimento)
Túnel público automático - funciona na hora, sem configuração.

- **Ideal para**: Iniciantes, testes rápidos
- **Banda**: ⚠️ Pode ter limitações
- **Latência**: ⚠️ Moderada
- **Vantagem**: Zero configuração necessária
- **Instalação**: Automática quando configurado
- **Configuração**:
  ```toml
  [tunnel]
  provider = "localtunnel"
  port = 8000
  ```

---

### **Providers Planejados** 🚀

#### 3. **Playit.gg** (Em desenvolvimento)
Túnel otimizado para jogos, desenvolvido por gamers.

- **Ideal para**: Jogos multiplayer, gaming
- **Banda**: ✅ Boa
- **Latência**: ✅ Otimizada para games
- **Site**: https://playit.gg/
- **Quando disponível**:
  ```toml
  [tunnel]
  provider = "playit"
  port = 8000
  ```

---

#### 4. **Zrok** (Em desenvolvimento)
Túnel open-source robusto e confiável.

- **Ideal para**: Deployments profissionais, servidor próprio
- **Banda**: ✅ Excelente
- **Latência**: ✅ Baixa
- **Site**: https://zrok.io/
- **Quando disponível**:
  ```toml
  [tunnel]
  provider = "zrok"
  port = 8000
  ```

---

### 📊 Tabela Comparativa

| Feature      | LAN         | LocalTunnel | Playit.gg   | Zrok        |
| ------------ | ----------- | ----------- | ----------- | ----------- |
| Status       | ✅ Ativo     | 🚀 Planejado | 🚀 Planejado | 🚀 Planejado |
| Configuração | Fácil       | Automática  | Simples     | Moderada    |
| Banda        | ∞ Ilimitada | ⚠️ Limitada  | ✅ Boa       | ✅ Excelente |
| Latência     | ⭐⭐⭐⭐⭐       | ⭐⭐⭐         | ⭐⭐⭐⭐⭐       | ⭐⭐⭐⭐        |
| Custo        | Grátis      | Grátis      | Grátis      | Grátis      |
| Requer VPN   | ✅ Sim       | ❌ Não       | ❌ Não       | ❌ Não       |
| Ideal para   | Amigos      | Testes      | Games       | Produção    |

---



- **[Backtrader](https://www.backtrader.com/)** → Motor de backtesting e simulação.  
- **[Flask](https://flask.palletsprojects.com/)** → Backend da aplicação.  
- **[Dash](https://dash.plotly.com/)** → Framework para interface gráfica interativa.  
- **[Plotly](https://plotly.com/python/)** → Gráficos dinâmicos para acompanhamento do portfólio.  
- **[yfinance](https://pypi.org/project/yfinance/)** → Dados do mercado financeiro.  
- **[SQLAlchemy](https://www.sqlalchemy.org/)** → ORM para banco de dados.  
- **Banco de Dados** → **MySQL e SQLite** para armazenamento de históricos e portfólio.  
- **WebSockets** → Comunicação em tempo real para atualização de gráficos e multiplayer (back -> front).
- **REST** → Comunicação em eventos e dados externos (front -> back).
- **PyInstaller** → Empacotamento da aplicação como executável (.exe).  

## 📦 Como Compilar o Executável

Para compilar o projeto em um executável único que inclui frontend e backend:

```bash
make build
```

Isso irá:
1. Compilar o frontend React/TypeScript
2. Copiar os arquivos para o backend
3. Gerar o executável com PyInstaller

O executável será gerado em `dist/SimuladorFinanceiro.exe` (Windows) ou `dist/SimuladorFinanceiro` (Linux/Mac).

Para mais detalhes, consulte a [documentação de build](docs/BUILD.md).

## 📜 Licença

Este projeto está licenciado sob os termos da [Licença Pública Geral GNU, versão 3 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.html).

Você pode usar, modificar e redistribuir este software livremente, contanto que preserve a mesma licença em versões modificadas.

© 2025 Murilo Marino

