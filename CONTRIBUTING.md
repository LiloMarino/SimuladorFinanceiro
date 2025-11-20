# Guia de Desenvolvimento

## 📁 Estrutura do Projeto  

**Estrutura Documentada:**

```plaintext
SimuladorFinanceiro/
├── .gitignore                                # Arquivos e pastas a serem ignorados pelo Git
├── .vscode/
│   └── launch.json
├── CONTRIBUTING.md                           # Guia para contribuir com o projeto
├── LICENSE                                   # Licença do projeto
├── README.md                                 # README do projeto
├── backend/                                  # Lógica do backend em Python+Flask
│   ├── data_importer.py                      # Importação de dados históricos a partir do yFinance ou de CSV
│   ├── data_provider.py                      # Funções soltas para consulta ao banco de dados
│   ├── database.py                           # Configuração e conexão com banco de dados
│   ├── logger_utils.py                       # Gerador de logger personalizado
│   ├── models/
│   │   └── models.py                         # Definição dos modelos ORM
│   ├── realtime/
│   │   ├── __init__.py                       # Singleton Pub/Sub ativo (SSE, WebSocket, etc.)
│   │   ├── realtime_broker.py                # Classe abstrata de um broker de comunicação realtime (Pub/Sub)
│   │   ├── sse_broker.py                     # Broker concreto de comunicação SSE
│   │   ├── ws_broker.py                      # Broker concreto de comunicação WebSocket
│   │   └── ws_handlers.py                    # Funções de manipulação de eventos WebSocket
│   ├── routes/
│   │   ├── __init__.py                       # Configuração e registo de rotas Flask
│   │   ├── helpers.py                        # Funções auxiliares para construção de respostas HTTP padronizadas REST
│   │   ├── import_routes.py                  # Rotas de importação de dados
│   │   ├── operation_routes.py               # Rotas de negociação manual
│   │   ├── portfolio_routes.py               # Rotas de portfólio
│   │   ├── realtime_routes.py                # Rotas de comunicação realtime
│   │   ├── settings_routes.py                # Rotas de configuração
│   │   └── timespeed_routes.py               # Rotas de configuração de velocidade
│   ├── simulation/
│   │   ├── __init__.py                       # Singleton do simulador
│   │   ├── broker.py                         # Broker de negociação de ações
│   │   ├── data_buffer.py                    # Buffer de dados de ações
│   │   ├── entities/
│   │   │   ├── candle.py                     # Dataclass de um candle de mercado
│   │   │   ├── fixed_income_asset.py         # Dataclass de um ativo de renda fixa
│   │   │   ├── order.py                      # Dataclass de uma ordem de compra ou venda
│   │   │   ├── portfolio.py                  # Dataclass de um portfólio
│   │   │   └── position.py                   # Dataclass de uma posição de uma ação
│   │   ├── fixed_broker.py                   # Broker de negociação de renda fixa
│   │   ├── fixed_income_factory/             # Implementação de abstract factory para renda fixa
│   │   │   ├── __init__.py                   # Factory randômico de ativos de renda fixa (integra todos os factories disponíveis)
│   │   │   ├── abstract_factory.py           # Classe abstrata de factory de ativos de renda fixa
│   │   │   ├── cdb_factory.py                # Factory de CDBs
│   │   │   ├── lca_factory.py                # Factory de LCAs
│   │   │   ├── lci_factory.py                # Factory de LCIs
│   │   │   └── tesouro_factory.py            # Factory de Tesouros Diretos
│   │   ├── fixed_income_market.py            # Gera e mantém o hall de ativos de renda fixa disponíveis
│   │   ├── simulation.py                     # Classe principal do simulador
│   │   └── simulation_engine.py              # Classe principal do motor do simulador
│   ├── simulation_loop.py                    # Loop global da simulação
│   └── strategy/
│       ├── base_strategy.py                  # Classe base para estratégias
│       └── manual.py                         # Estratégia de negociação manual
├── data/
│   └── simulador_financeiro.mwb              # Modelo visual do banco (MySQL Workbench)
├── example.env                               # Exemplo de variáveis de ambiente
├── frontend/
│   ├── README.md                             # README gerado automaticamente pelo Vite
│   ├── components.json                       # Configuração do Shadcn UI
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── public/
│   │   └── vite.svg
│   ├── src/
│   │   ├── App.tsx                           # Componente principal da aplicação
│   │   ├── assets/
│   │   │   └── react.svg
│   │   ├── components/
│   │   │   ├── cards/
│   │   │   │   ├── base-card.tsx
│   │   │   │   ├── fixed-income-card.tsx
│   │   │   │   └── stock-card.tsx
│   │   │   ├── import-assets/
│   │   │   │   ├── csv-form.tsx
│   │   │   │   └── yfinance-form.tsx
│   │   │   ├── stock-chart.tsx
│   │   │   ├── summary-card.tsx
│   │   │   └── ui/
│   │   │       ├── alert-dialog.tsx
│   │   │       ├── badge.tsx
│   │   │       ├── button.tsx
│   │   │       ├── card.tsx
│   │   │       ├── chart.tsx
│   │   │       ├── checkbox.tsx
│   │   │       ├── dialog.tsx
│   │   │       ├── form.tsx
│   │   │       ├── input.tsx
│   │   │       ├── label.tsx
│   │   │       ├── sonner.tsx
│   │   │       ├── spinner.tsx
│   │   │       └── table.tsx
│   │   ├── context/
│   │   │   ├── page-label/
│   │   │   │   ├── PageLabelContext.ts       # Contexto do nome da página
│   │   │   │   ├── PageLabelProvider.tsx     # Provider do nome da página
│   │   │   │   └── index.ts                  # Exporta o provider e o context
│   │   │   └── realtime/
│   │   │       ├── RealtimeContext.ts        # Contexto de comunicação realtime
│   │   │       ├── RealtimeProvider.tsx      # Provider de comunicação realtime
│   │   │       └── index.ts                  # Exporta o provider e o context
│   │   ├── hooks/
│   │   │   ├── useActivePage.ts              # Hook para obter a página ativa
│   │   │   ├── useFormDataMutation.ts        # Hook para mutação de formulários
│   │   │   ├── useMutationApi.ts             # Hook para mutação de REST API
│   │   │   ├── usePageLabel.ts               # Hook para obter o nome da página
│   │   │   ├── useQueryApi.ts                # Hook para consulta de REST API
│   │   │   ├── useRealtime.ts                # Hook para comunicação realtime
│   │   │   └── useRealtimeContext.ts         # Hook para obter o contexto de comunicação realtime
│   │   ├── index.css
│   │   ├── layouts/
│   │   │   ├── main-layout.tsx               # Layout principal da aplicação
│   │   │   └── partial/
│   │   │       ├── sidebar.tsx               # Parte do sidebar da aplicação
│   │   │       └── topbar.tsx                # Parte do topbar da aplicação
│   │   ├── lib/
│   │   │   ├── realtime/
│   │   │   │   ├── baseSubscriberRealtime.ts # Classe base para clientes de comunicação realtime
│   │   │   │   ├── socketClient.ts           # Implementação concreta do cliente de comunicação realtime WebSocket
│   │   │   │   └── sseClient.ts              # Implementação concreta do cliente de comunicação realtime Server-Sent Events
│   │   │   ├── schemas/                      # Schemas Zod
│   │   │   │   └── api.ts
│   │   │   ├── utils/
│   │   │   │   ├── api.ts
│   │   │   │   └── formatting.ts             # Funções de formatação
│   │   │   └── utils.ts
│   │   ├── main.tsx
│   │   ├── models/
│   │   │   └── fixed-income-asset.ts         # Classe para ajudar a modelar um ativo de renda fixa
│   │   ├── pages/                            # Páginas da aplicação
│   │   │   ├── fixed-income-details.tsx
│   │   │   ├── fixed-income.tsx
│   │   │   ├── import-assets.tsx
│   │   │   ├── lobby.tsx
│   │   │   ├── portfolio.tsx
│   │   │   ├── settings.tsx
│   │   │   ├── statistics.tsx
│   │   │   ├── strategies.tsx
│   │   │   ├── variable-income-details.tsx
│   │   │   └── variable-income.tsx
│   │   ├── types/
│   │   │   └── index.ts                      # Tipos usados na aplicação
│   │   └── vite-env.d.ts
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── main.py                                   # Main do backend (Flask)
├── requirements.txt
└── scripts/                                  # Scripts auxiliares
    ├── fix_model.py
    ├── tree.py                               # Geração da árvore do projeto
    └── tree_descriptions.yaml                # Descrições da árvore do projeto
```

A árvore da estrutura do projeto é mantido automaticamente com o script

```bash
python .\scripts\tree.py
```

As descrições exibidas ao lado dos arquivos e pastas na árvore são carregadas automaticamente do arquivo

```
scripts/tree_descriptions.yaml
```

Para adicionar ou alterar descrições, basta editar esse arquivo YAML, seguindo o padrão:

```yaml
backend/: Lógica do backend em Flask
backend/database.py: Configuração do banco de dados
data/: Arquivos de dados de entrada
```

Após salvar, execute novamente:

```bash
python .\scripts\tree.py
```

para gerar a estrutura atualizada com os comentários alinhados.

## 🔁 Ciclo de Desenvolvimento com Banco de Dados

1. ✏️ **Editar modelo no MySQL Workbench** (`.mwb`)
2. 📥 **Sincronizar o banco de dados MySQL**
3. 🧬 **Gerar ORM com sqlacodegen**  

```bash
   sqlacodegen mysql+pymysql://usuario:senha@localhost/simulador_financeiro > backend/models/models.py
```
4. 🛠️ **Compatibilizar com múltiplos bancos (MySQL/SQLite)**

O projeto detecta automaticamente qual banco usar (MySQL ou SQLite) com base nas variáveis de ambiente, e cria as tabelas automaticamente com:
```python
Base.metadata.create_all(bind=engine)
```

## 📖 Overview da Arquitetura Realtime

Esta seção documenta a arquitetura de comunicação realtime do SimuladorFinanceiro, usando **Pub/Sub** e mantendo consistência entre backend e frontend.

### Estrutura

* **Backend**

  * `RealtimeBroker` (interface)
  * `SSEBroker` / `SocketBroker` (implementações concretas)
  * Singleton do broker (`current_app.config["realtime_broker"]`)
  * Função `notify(event, payload)` para publicar eventos

* **Frontend**

  * `Subscriber` (interface comum)
  * `SSEClient` / `SocketClient` (implementações concretas)
  * `RealtimeProvider` (Provider do React)
  * `useRealtime()` (hook genérico)
  * Componentes consomem `useRealtime()` sem se importar com implementação concreta

---

### Diagrama UML em Mermaid

```mermaid
classDiagram
%% Interfaces
class RealtimeBroker {
  <<interface>>
  +register_client(client_id)
  +remove_client(client_id)
  +update_subscription(client_id, events)
  +notify(event, payload)
  +connect()
}

class SubscriberRealtime {
  <<interface>>
  +connect()
  +subscribe(cb)
  +unsubscribe(cb)
}

%% Implementações backend
class SSEBroker {
  +register_client()
  +remove_client()
  +update_subscription()
  +notify()
  +connect()
}

class SocketBroker {
  +register_client()
  +remove_client()
  +update_subscription()
  +notify()
}

%% Implementações frontend
class SSEClient {
  +connect()
  +subscribe()
  +unsubscribe()
}

class SocketClient {
  +connect()
  +subscribe()
  +unsubscribe()
}

%% Provider + Hook
class RealtimeProvider {
  +value: SubscriberRealtime
}

class useRealtime {
  +subscribe(cb)
  +unsubscribe(cb)
}

%% Relações de implementação
RealtimeBroker <|.. SSEBroker
RealtimeBroker <|.. SocketBroker
SubscriberRealtime <|.. SSEClient
SubscriberRealtime <|.. SocketClient

%% Relações frontend
RealtimeProvider o-- SubscriberRealtime : contém / injeta instância singleton
useRealtime --> RealtimeProvider : consome Provider (dependency)
useRealtime --> SubscriberRealtime : chama subscribe/unsubscribe (dependency)

%% Comunicação pub/sub entre front e back
SSEBroker --> SSEClient : Pub/Sub SSE (dependency)
SocketBroker --> SocketClient : Pub/Sub WS (dependency)


```

---

### Explicação

1. **Frontend**

   * O `Subscriber` define o contrato comum que qualquer implementação concreta (SSE ou WebSocket) deve seguir.
   * `RealtimeProvider` injeta **uma instância singleton** de `Subscriber` na árvore de componentes.
   * `useRealtime()` consome o Provider e gerencia subscribe/unsubscribe, atualizando `state` dos componentes.
   * Componentes (`Dashboard`, `Notifications`, etc.) usam `useRealtime()` sem conhecer se é SSE ou WS.

2. **Backend**

   * `RealtimeBroker` define a interface Pub/Sub para qualquer broker realtime.
   * `SSEBroker` implementa SSE, expondo `connect()` para streaming HTTP.
   * `SocketBroker` implementa WebSocket, sem `connect()` (conexão é gerenciada pelo SocketIO).
   * Singleton no Flask (`current_app.config["realtime_broker"]`) garante **uma única instância compartilhada** para todos os endpoints.

3. **Comunicação**

   * O frontend recebe eventos do backend via SSE ou WebSocket.
   * Backend publica eventos com `notify(event, payload)` para todos os subscribers registrados.
   * Frontend atualiza estado e re-renderiza componentes automaticamente.

---

💡 **Vantagens desta arquitetura**

* Coerência entre backend e frontend (interface comum + singleton + pub/sub).
* Flexível: troca de SSE por WebSocket ou mocks de teste apenas alterando o Provider.
* Seguro: TypeScript e Python garantem que as implementações concretas seguem os contratos.
* Reutilizável: múltiplos componentes podem usar o mesmo hook sem criar novas conexões.
* Evita memory leaks: subscribe/unsubscribe gerenciados pelo hook.
