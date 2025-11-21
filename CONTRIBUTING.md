# Guia de Desenvolvimento

## 📁 Estrutura do Projeto  

**Estrutura Documentada:**

```plaintext
SimuladorFinanceiro/
├── .gitignore                                    # Ignora arquivos desnecessários do Git.
├── .vscode/                                      # Configurações específicas do VSCode.
│   └── launch.json                               # Configurações de debug do VSCode.
├── CONTRIBUTING.md                               # Guia para contribuidores.
├── LICENSE                                       # Licença do projeto.
├── README.md                                     # Descrição geral do projeto.
├── backend/                                      # Código-fonte do servidor Python. Organizado por domínios (features), rotas e utilidades compartilhadas.
│   ├── core/                                     # Infraestrutura central: database, logger, modelos e utilidades de baixo nível.
│   │   ├── database.py                           # Configuração da conexão com o banco e inicialização do ORM.
│   │   ├── logger.py                             # Logger global configurado para todo o backend.
│   │   ├── models/                               # Modelos persistentes usados pelo ORM.
│   │   │   └── models.py                         # Definições base de modelos SQLAlchemy.
│   │   └── utils/                                # Funções utilitárias genéricas de infraestrutura (puras, pequenas e sem domínio).
│   │       └── data_provider.py                  # Fornece acesso unificado aos dados.
│   ├── features/                                 # Implementações separadas por domínio funcional (DDD): realtime, simulation e strategy.
│   │   ├── import_data/                          # Lógica de ingestão de dados externos para o sistema.
│   │   │   └── importer_service.py               # Serviço responsável por importar, validar e transformar dados.
│   │   ├── realtime/                             # Módulo responsável por comunicação em tempo real.
│   │   │   ├── __init__.py
│   │   │   ├── realtime_broker.py                # Classe abstrata de um broker de comunicação realtime (Pub/Sub).
│   │   │   ├── sse_broker.py                     # Broker concreto de comunicação SSE.
│   │   │   ├── ws_broker.py                      # Broker concreto de comunicação WebSocket.
│   │   │   └── ws_handlers.py                    # Callbacks de eventos WebSocket.
│   │   ├── simulation/                           # Núcleo da engine de simulação do mercado financeiro.
│   │   │   ├── __init__.py
│   │   │   ├── broker.py                         # Broker de negociação de ações.
│   │   │   ├── data_buffer.py                    # Buffer interno para caching de dados durante a simulação.
│   │   │   ├── entities/                         # Modelos/entidades da simulação.
│   │   │   │   ├── candle.py                     # Representa candles OHLCV.
│   │   │   │   ├── fixed_income_asset.py         # Representa ativo de renda fixa.
│   │   │   │   ├── order.py                      # Ordem de compra/venda.
│   │   │   │   ├── portfolio.py                  # Carteira completa.
│   │   │   │   └── position.py                   # Posição de um único ativo de renda varíavel.
│   │   │   ├── fixed_broker.py                   # Broker de negociação de renda fixa.
│   │   │   ├── fixed_income/                     # Módulo de lógica de renda fixa e produtos.
│   │   │   │   ├── factory/                      # Factories de criação de ativos financeiros de renda fixa.
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── abstract_factory.py       # Interface base para factories.
│   │   │   │   │   ├── cdb_factory.py            # Factory para CDB.
│   │   │   │   │   ├── lca_factory.py            # Factory LCA.
│   │   │   │   │   ├── lci_factory.py            # Factory LCI.
│   │   │   │   │   └── tesouro_factory.py        # Factory Tesouro Direto.
│   │   │   │   └── market.py                     # Mercado de renda fixa.
│   │   │   ├── simulation.py                     # Módulo de lógica da simulação.
│   │   │   └── simulation_engine.py              # Engine de simulação.
│   │   └── strategy/                             # Algoritmos de estratégia de investimento.
│   │       ├── base_strategy.py                  # Interface base.
│   │       └── manual.py                         # Estratégia manual usada pelo usuário.
│   ├── routes/                                   # Blueprints/routers do backend (FastAPI/Flask).
│   │   ├── __init__.py
│   │   ├── helpers.py                            # Helpers REST — padronização de responses.
│   │   ├── import_routes.py                      # Rotas de importação.
│   │   ├── operation_routes.py                   # Operações (compra/venda).
│   │   ├── portfolio_routes.py                   # Rotas da carteira.
│   │   ├── realtime_routes.py                    # Rotas de realtime SSE.
│   │   ├── settings_routes.py                    # Configurações da simulação.
│   │   └── timespeed_routes.py                   # Ajuste de velocidade da simulação.
│   └── simulation_loop.py                        # Lógica de loop principal da simulação.
├── data/                                         # Dados externos do projeto.
│   └── simulador_financeiro.mwb                  # Esquema do banco MySQL Workbench.
├── example.env                                   # Exemplo de variáveis de ambiente.
├── frontend/                                     # Aplicação React + Vite. Estrutura Feature-Based + Domain Segmentation.
│   ├── components.json                           # Configuração do shadcn/ui.
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── public/                                   # Imagens e assets estáticos do Vite.
│   │   └── vite.svg
│   ├── src/                                      # Código-fonte principal do frontend.
│   │   ├── App.tsx
│   │   ├── assets/
│   │   │   └── react.svg
│   │   ├── features/                             # Funcionalidades agrupadas por domínio (DDD no frontend).
│   │   │   ├── fixed-income/                     # Feature de renda fixa.
│   │   │   │   └── components/
│   │   │   │       ├── base-card.tsx
│   │   │   │       └── fixed-income-card.tsx
│   │   │   ├── import-assets/                    # Tela e lógica de importação.
│   │   │   │   └── components/
│   │   │   │       ├── csv-form.tsx
│   │   │   │       └── yfinance-form.tsx
│   │   │   ├── portfolio/                        # Feature do portfólio.
│   │   │   │   └── components/
│   │   │   │       └── summary-card.tsx
│   │   │   └── variable-income/                  # Feature de renda variável.
│   │   │       └── components/
│   │   │           ├── stock-card.tsx
│   │   │           └── stock-chart.tsx
│   │   ├── index.css
│   │   ├── layouts/                              # Layouts que compõem a estrutura geral da UI.
│   │   │   ├── main-layout.tsx                   # Layout base.
│   │   │   └── partial/                          # Partes do layout (sidebar, topbar).
│   │   │       ├── sidebar.tsx
│   │   │       └── topbar.tsx
│   │   ├── main.tsx
│   │   ├── models/                               # Factories e classes (modelo orientado a objetos).
│   │   │   └── fixed-income-asset.ts
│   │   ├── pages/                                # Páginas completas do app.
│   │   │   ├── fixed-income-details.tsx
│   │   │   ├── fixed-income.tsx                  # Página principal da renda fixa.
│   │   │   ├── import-assets.tsx
│   │   │   ├── lobby.tsx
│   │   │   ├── portfolio.tsx                     # Página do portfólio.
│   │   │   ├── settings.tsx                      # Tela de configurações.
│   │   │   ├── statistics.tsx                    # Tela de estatísticas.
│   │   │   ├── strategies.tsx                    # Tela de estratégias.
│   │   │   ├── variable-income-details.tsx
│   │   │   └── variable-income.tsx               # Página principal da renda variável.
│   │   ├── shared/                               # Código compartilhado entre features.
│   │   │   ├── components/                       # Componentes reutilizáveis.
│   │   │   │   └── ui/                           # Componentes de UI do shadcn/ui.
│   │   │   │       ├── alert-dialog.tsx
│   │   │   │       ├── badge.tsx
│   │   │   │       ├── button.tsx
│   │   │   │       ├── card.tsx
│   │   │   │       ├── chart.tsx
│   │   │   │       ├── checkbox.tsx
│   │   │   │       ├── dialog.tsx
│   │   │   │       ├── form.tsx
│   │   │   │       ├── input.tsx
│   │   │   │       ├── label.tsx
│   │   │   │       ├── sonner.tsx
│   │   │   │       ├── spinner.tsx
│   │   │   │       └── table.tsx
│   │   │   ├── context/                          # Contextos globais de estado.
│   │   │   │   ├── page-label/
│   │   │   │   │   ├── PageLabelContext.ts
│   │   │   │   │   ├── PageLabelProvider.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   └── realtime/
│   │   │   │       ├── RealtimeContext.ts
│   │   │   │       ├── RealtimeProvider.tsx
│   │   │   │       └── index.ts
│   │   │   ├── hooks/                            # Hooks reutilizáveis (useQueryApi etc).
│   │   │   │   ├── useActivePage.ts
│   │   │   │   ├── useFormDataMutation.ts
│   │   │   │   ├── useMutationApi.ts
│   │   │   │   ├── usePageLabel.ts
│   │   │   │   ├── useQueryApi.ts
│   │   │   │   ├── useRealtime.ts
│   │   │   │   └── useRealtimeContext.ts
│   │   │   └── lib/                              # Bibliotecas internas.
│   │   │       ├── realtime/                     # Lógica para SSE/WS.
│   │   │       │   ├── baseSubscriberRealtime.ts
│   │   │       │   ├── socketClient.ts
│   │   │       │   └── sseClient.ts
│   │   │       ├── schemas/                      # Zod schemas da API.
│   │   │       │   └── api.ts
│   │   │       ├── utils/                        # Funções auxiliares (formatting, api).
│   │   │       │   ├── api.ts
│   │   │       │   └── formatting.ts
│   │   │       └── utils.ts
│   │   ├── types/                                # Definições TypeScript de tipos por domínio.
│   │   │   ├── base.ts                           # Tipos universais.
│   │   │   ├── economic.ts                       # Tipos de indicadores.
│   │   │   ├── fixed-income.ts                   # Tipos de renda fixa.
│   │   │   ├── index.ts
│   │   │   ├── portfolio.ts                      # Tipos da carteira.
│   │   │   ├── simulation.ts                     # Tipos de simulação.
│   │   │   └── stock.ts                          # Tipos de renda variável.
│   │   └── vite-env.d.ts
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts                            # Configuração do Vite.
├── main.py                                       # Entrada da API/backend.
├── requirements.txt                              # Dependências do backend Python.
└── scripts/                                      # Scripts utilitários para desenvolvimento.
    ├── fix_model.py                              # Script para arrumar models automaticamente.
    ├── tree.py                                   # Gera a árvore de diretórios.
    └── tree_descriptions.yaml                    # Arquivo de descrição da estrutura (este arquivo).
```

A árvore da estrutura do projeto é mantido automaticamente com o script

```bash
python -X utf8 .\scripts\tree.py > arvore.md
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
python -X utf8 .\scripts\tree.py > arvore.md
```

para gerar a estrutura atualizada com os comentários alinhados. 
Após isso copie o conteúdo para o arquivo `CONTRIBUTING.md` e exclua o arquivo `arvore.md`.

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
