# Guia de Desenvolvimento

## 📁 Estrutura do Projeto  

**Estrutura Documentada:**

```plaintext
/SimuladorFinanceiro
├── .gitignore                          # Arquivos e pastas a serem ignorados pelo Git
├── CONTRIBUTING.md                     # Guia para contribuir com o projeto
├── LICENSE                             # Licença de uso do projeto
├── README.md                           # Documentação principal
├── backend/                            # Lógica do backend em Flask
│   ├── data_loader.py                  # Importação de dados históricos
│   ├── database.py                     # Configuração do banco de dados
│   ├── logger_utils.py                 # Utilitários para logging
│   ├── models/                         # Modelos ORM
│   │   └── models.py                   # Definição dos modelos de dados
│   ├── routes.py                       # Rotas de navegação (páginas)
│   ├── simulation.py                   # Classe Simulation
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── global.js
│   │       └── modules/
│   │           ├── import.js
│   │           ├── sidebar.js
│   │           ├── simulation.js
│   │           └── toast.js
│   ├── templates/                      # HTML com Jinja2
│   │   ├── base.html
│   │   ├── carteira.html
│   │   ├── components/
│   │   │   └── stock_card.html
│   │   ├── configs.html
│   │   ├── detalhe_renda_fixa.html
│   │   ├── detalhe_renda_variavel.html
│   │   ├── estatisticas.html
│   │   ├── estrategias.html
│   │   ├── importar_ativos.html
│   │   ├── lobby.html
│   │   ├── partials/
│   │   │   ├── sidebar.html
│   │   │   └── topbar.html
│   │   ├── renda_fixa.html
│   │   └── renda_variavel.html
│   └── websocket.py                    # Comunicação real-time com JS no front
├── data/                               # Arquivos de dados de entrada
│   └── simulador_financeiro.mwb        # Modelo visual do banco (MySQL Workbench)
├── example.env                         # Exemplo de variáveis de ambiente
├── main.py                             # Ponto de entrada da aplicação Flask
├── requirements.txt                    # Lista de dependências do projeto
└── scripts/                            # Scripts auxiliares
    ├── fix_model.py
    ├── tree.py                         # Geração da árvore do projeto
    └── tree_descriptions.yaml
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
