---
sidebar_position: 3
---

# Estrutura de Pastas

Como o código é organizado no projeto.

## Visão Geral

O projeto segue uma arquitetura organizada por features (Domain-Driven Design) tanto no backend quanto no frontend, facilitando a manutenção e escalabilidade.

## Organização Frontend: Features vs Shared

No frontend, existe uma separação **implícita mas clara** pela organização de pastas:

### `features/**/components/*`

Componentes, hooks e outros recursos dentro de `features/` são **EXCLUSIVOS** daquela feature específica. Eles **não podem** ser reutilizados em outras features.

**Exemplo:**
```
features/lobby/components/SessionCard.tsx
```
Este componente é usado **apenas** dentro da feature `lobby`.

### `shared/**/components/*`

Componentes, hooks, contexts e outros recursos dentro de `shared/` são **REAPROVEITÁVEIS** e podem ser usados em **múltiplas features**.

**Exemplo:**
```
shared/components/Button.tsx
```
Este componente pode ser usado em qualquer feature do projeto.

### Regra de Ouro

:::tip Regra de Organização
- **Feature-specific** → `features/nome-feature/components/*`, `features/nome-feature/hooks/*`
- **Reusable** → `shared/components/*`, `shared/hooks/*`, `shared/context/*`
:::

---

## Estrutura Completa Documentada

```plaintext
SimuladorFinanceiro/
├── .github/                            # Configurações do GitHub (Actions, workflows, etc)
│   └── workflows/                      # Workflows de CI/CD e automações
├── .vscode/                            # Configurações do Visual Studio Code para o projeto
├── backend/                            # Código-fonte do servidor Python (FastAPI)
│   ├── config/                         # Configurações da aplicação (variáveis de ambiente, TOML)
│   ├── core/                           # Infraestrutura central (database, logger, models, utils)
│   │   ├── decorators/                 # Decoradores reutilizáveis (auth, cache, etc)
│   │   ├── dependencies/               # Dependências do FastAPI (injeção de dependência)
│   │   ├── dto/                        # Data Transfer Objects para comunicação backend->frontend e tipagem forte
│   │   │   └── events/                 # DTOs específicos para eventos da simulação
│   │   ├── enum/                       # Enumerações globais (tipos, status, etc)
│   │   ├── exceptions/                 # Exceções customizadas da aplicação
│   │   ├── models/                     # Modelos SQLAlchemy (entidades do banco de dados)
│   │   ├── repository/                 # Camada de acesso a dados (Data Access Layer)
│   │   ├── runtime/                    # Gerenciadores runtime singleton thread-safe (brokers, túneis, etc)
│   │   └── utils/                      # Funções utilitárias genéricas de infraestrutura
│   ├── features/                       # Funcionalidades organizadas por domínio (DDD)
│   │   ├── fixed_income/               # Lógica de negócio de Renda Fixa
│   │   │   ├── entities/               # Entidades de domínio (CDB, Tesouro, etc)
│   │   │   └── factory/                # Factories para criação de ativos de RF
│   │   ├── import_data/                # Serviço de importação de dados externos
│   │   ├── realtime/                   # Sistema de comunicação em tempo real (WebSocket/SSE)
│   │   ├── simulation/                 # Engine de simulação do mercado financeiro
│   │   ├── strategy/                   # Algoritmos de estratégias de investimento
│   │   ├── tunnel/                     # Sistema de túnel para multiplayer (ngrok, etc)
│   │   │   ├── network_utils/          # Utilitários de rede para túneis
│   │   │   └── providers/              # Provedores de túnel (ngrok, localtunnel)
│   │   └── variable_income/            # Lógica de negócio de Renda Variável
│   │       ├── entities/               # Entidades de domínio (Ações, FIIs, etc)
│   │       └── liquidity/              # Sistema de liquidez e book de ofertas
│   ├── routes/                         # Endpoints REST da API (routers do FastAPI)
│   └── types/                          # Definições de tipos Python compartilhados
├── docs/                               # Documentação do projeto (Docusaurus)
├── frontend/                           # Aplicação React + TypeScript (Vite)
│   ├── assets/                         # Assets estáticos do frontend (imagens, fontes)
│   ├── features/                       # Funcionalidades organizadas por domínio (Feature-Based)
│   │   ├── auth/                       # Feature de autenticação e login
│   │   │   └── pages/                  # Páginas de autenticação
│   │   ├── fixed-income/               # Feature de Renda Fixa
│   │   │   ├── components/             # Componentes específicos de RF
│   │   │   ├── models/                 # Models de ativos de RF
│   │   │   ├── pages/                  # Páginas da feature de RF
│   │   │   └── schemas/                # Schemas de validação (Zod) para RF
│   │   ├── import-assets/              # Feature de importação de ativos
│   │   │   ├── components/             # Componentes de importação (CSV, YFinance)
│   │   │   └── pages/                  # Páginas de importação
│   │   ├── lobby/                      # Feature de lobby/sessões multiplayer
│   │   │   ├── components/             # Componentes do lobby
│   │   │   ├── hooks/                  # Hooks customizados do lobby
│   │   │   └── pages/                  # Páginas do lobby
│   │   ├── portfolio/                  # Feature de carteira/portfólio
│   │   │   ├── components/             # Componentes da carteira (gráficos, tabelas)
│   │   │   ├── lib/                    # Lógica de negócio da carteira
│   │   │   └── pages/                  # Páginas da carteira
│   │   ├── settings/                   # Feature de configurações
│   │   │   ├── components/             # Componentes de configurações
│   │   │   └── pages/                  # Páginas de configurações
│   │   ├── statistics/                 # Feature de estatísticas e ranking
│   │   │   ├── components/             # Componentes de estatísticas
│   │   │   ├── lib/                    # Lógica de cálculo de estatísticas
│   │   │   └── pages/                  # Páginas de estatísticas
│   │   ├── strategies/                 # Feature de estratégias automatizadas
│   │   │   └── pages/                  # Páginas de estratégias
│   │   └── variable-income/            # Feature de Renda Variável
│   │       ├── components/             # Componentes de RV (gráficos, ordens)
│   │       └── pages/                  # Páginas de RV (mercado, detalhes)
│   ├── layouts/                        # Layouts principais da aplicação
│   │   └── partial/                    # Componentes parciais de layout (sidebar, topbar)
│   ├── pages/                          # Páginas genéricas (erro, loading, etc)
│   ├── public/                         # Assets públicos servidos pelo Vite
│   ├── shared/                         # Código compartilhado entre features
│   │   ├── components/                 # Componentes React reutilizáveis entre as features
│   │   ├── context/                    # Contexts globais (React Context API)
│   │   │   ├── auth/                   # Context de autenticação
│   │   │   ├── notifications-settings/ # Context de configurações de notificações
│   │   │   ├── page-label/             # Context de labels de páginas
│   │   │   ├── realtime/               # Context de comunicação em tempo real
│   │   │   └── simulation/             # Context de estado da simulação
│   │   ├── hooks/                      # Hooks customizados reutilizáveis
│   │   ├── lib/                        # Bibliotecas internas e utilitários
│   │   │   ├── models/                 # Classes e models (ApiError, etc)
│   │   │   ├── realtime/               # Cliente de WebSocket/SSE
│   │   │   ├── schemas/                # Schemas de validação (Zod)
│   │   │   └── utils/                  # Funções utilitárias (formatação, API, etc)
│   │   └── notifications/              # Sistema global de notificações
│   └── types/                          # Definições de tipos TypeScript compartilhados
└── scripts/                            # Scripts utilitários de desenvolvimento
```

---

## Atualização da Árvore de Estrutura

A árvore da estrutura do projeto é mantida automaticamente com o script:

```bash
python -X utf8 ./scripts/tree.py > arvore.md
```

### Como Adicionar Descrições

As descrições exibidas ao lado dos arquivos e pastas na árvore são carregadas do arquivo:

```
scripts/tree_descriptions.yaml
```

Para adicionar ou alterar descrições, edite esse arquivo YAML seguindo o padrão:

```yaml
backend/: Lógica do backend em FastAPI
backend/core/: Infraestrutura central do backend
frontend/: Aplicação React + TypeScript
```

Após salvar, execute novamente:

```bash
python -X utf8 ./scripts/tree.py > arvore.md
```

Isso gerará a estrutura atualizada com os comentários alinhados.

:::tip
Após gerar, você pode atualizar esta documentação com a nova árvore se houver mudanças significativas na estrutura.
:::

---

## Convenções de Nomenclatura

### Backend (Python)

- **Arquivos:** `snake_case.py`
- **Classes:** `PascalCase`
- **Funções:** `snake_case()`
- **Constantes:** `SCREAMING_SNAKE_CASE`
- **Variáveis:** `snake_case`

**Exemplo:**
```python
# backend/features/simulation/simulation_engine.py
class SimulationEngine:
    MAX_SPEED = 10
    
    def calculate_returns(self):
        pass
```

### Frontend (TypeScript/React)

- **Arquivos de Componentes:** `kebab-case.tsx`
- **Arquivos classe:** `PascalCase.ts`
- **Arquivos utilitários:** `camelCase.ts`
- **Componentes:** `PascalCase`
- **Funções:** `camelCase()`
- **Hooks:** `useNomeDoHook()`
- **Constantes:** `SCREAMING_SNAKE_CASE`
- **Variáveis:** `camelCase`

**Exemplo:**
```typescript
// frontend/shared/components/Button.tsx
export const Button = () => { ... }

// frontend/shared/hooks/useAuth.ts
export const useAuth = () => { ... }

// frontend/shared/lib/utils/formatCurrency.ts
export const formatCurrency = (value: number) => { ... }
```

---

## Próximos Passos

- [Ciclo de Desenvolvimento com BD](../ciclo-banco-dados) — Como trabalhar com banco de dados
- [Diretrizes Async vs Sync](../async-vs-sync) — Padrões de código assíncrono
- [Contribuindo](./contribuindo) — Como enviar suas mudanças
