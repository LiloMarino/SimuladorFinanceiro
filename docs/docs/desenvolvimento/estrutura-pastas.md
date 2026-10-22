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
features/lobby/components/lobby-header.tsx
```
Este componente é usado **apenas** dentro da feature `lobby`.

### `shared/**/components/*`

Componentes, hooks, contexts e outros recursos dentro de `shared/` são **REAPROVEITÁVEIS** e podem ser usados em **múltiplas features**.

**Exemplo:**
```
shared/components/base-card.tsx
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
│   │   ├── decorators/                 # Decoradores reutilizáveis (transações)
│   │   ├── dependencies/               # Dependências do FastAPI (injeção de dependência)
│   │   ├── dto/                        # Data Transfer Objects para comunicação backend->frontend e tipagem forte
│   │   │   └── events/                 # DTOs específicos para eventos da simulação
│   │   ├── enum/                       # Enumerações globais (tipos, status, etc)
│   │   ├── exceptions/                 # Exceções customizadas da aplicação
│   │   ├── models/                     # Modelos SQLAlchemy (entidades do banco de dados)
│   │   ├── repository/                 # Camada de acesso a dados (Data Access Layer)
│   │   ├── runtime/                    # Gerenciadores runtime singleton thread-safe (brokers, usuários, etc)
│   │   └── utils/                      # Funções utilitárias genéricas de infraestrutura
│   ├── features/                       # Funcionalidades organizadas por domínio (DDD)
│   │   ├── achievements/               # Catálogo e avaliação das conquistas
│   │   ├── correlation/                # Cálculo da correlação entre ativos
│   │   ├── fixed_income/               # Lógica de negócio de Renda Fixa
│   │   │   ├── entities/               # Entidades de domínio (CDB, Tesouro, etc)
│   │   │   └── factory/                # Factories para criação de ativos de RF
│   │   ├── import_data/                # Importação de dados externos e geração do futuro
│   │   ├── realtime/                   # Sistema de comunicação em tempo real (WebSocket)
│   │   ├── simulation/                 # Engine de simulação do mercado financeiro
│   │   ├── statistics/                 # Nota, ranking, retorno, risco e meta da partida
│   │   ├── strategy/                   # Algoritmos de estratégias de investimento
│   │   ├── tunnel/                     # Link de convite para o multiplayer
│   │   │   ├── network_utils/          # Utilitários de rede
│   │   │   └── providers/              # Provedores do link (rede local e um de exemplo)
│   │   └── variable_income/            # Lógica de negócio de Renda Variável
│   │       ├── entities/               # Entidades de domínio (Ações, FIIs, etc)
│   │       └── liquidity/              # Sistema de liquidez e book de ofertas
│   ├── migrations/                     # Migrations do Alembic (schema do banco)
│   │   └── versions/                   # Uma revisão por mudança de schema
│   ├── routes/                         # Endpoints REST da API (routers do FastAPI)
│   └── types/                          # Definições de tipos Python compartilhados
├── docs/                               # Documentação do projeto (Docusaurus)
├── frontend/                           # Aplicação React + TypeScript (Vite)
│   ├── assets/                         # Assets estáticos do frontend (imagens, fontes)
│   ├── features/                       # Funcionalidades organizadas por domínio (Feature-Based)
│   │   ├── achievements/               # Tela de conquistas
│   │   ├── auth/                       # Feature de autenticação e login
│   │   ├── correlation/                # Tela de correlação entre ativos
│   │   ├── fixed-income/               # Feature de Renda Fixa
│   │   ├── goal/                       # Tela Meta (corrida à meta e vida financeira)
│   │   ├── import-assets/              # Central de dados (importação e séries da base)
│   │   ├── join/                       # Entrada numa partida em andamento
│   │   ├── lobby/                      # Feature de lobby/sessões multiplayer
│   │   ├── performance/                # Painel de desempenho (modo debug)
│   │   ├── portfolio/                  # Feature de carteira/portfólio
│   │   ├── settings/                   # Feature de configurações
│   │   ├── statistics/                 # Estatísticas, ranking e fechamento da partida
│   │   ├── strategies/                 # Feature de estratégias automatizadas
│   │   └── variable-income/            # Feature de Renda Variável
│   │       ├── components/             # Componentes de RV (gráficos, ordens)
│   │       └── pages/                  # Páginas de RV (mercado, detalhes)
│   ├── layouts/                        # Layouts principais da aplicação
│   │   └── partial/                    # Componentes parciais de layout (sidebar, topbar)
│   ├── pages/                          # Páginas genéricas (erro, loading, etc)
│   ├── public/                         # Assets públicos servidos pelo Vite
│   ├── shared/                         # Código compartilhado entre features
│   │   ├── components/                 # Componentes React reutilizáveis entre as features
│   │   │   └── ui/                     # Design system (componentes shadcn)
│   │   ├── context/                    # Contexts globais (React Context API)
│   │   │   ├── auth/                   # Context de autenticação
│   │   │   ├── notifications-settings/ # Context de configurações de notificações
│   │   │   ├── page-label/             # Context de labels de páginas
│   │   │   ├── realtime/               # Context de comunicação em tempo real
│   │   │   └── simulation/             # Context de estado da simulação
│   │   ├── hooks/                      # Hooks customizados reutilizáveis
│   │   ├── lib/                        # Bibliotecas internas e utilitários
│   │   │   ├── api/                    # Chamada à API (apiFetch)
│   │   │   ├── models/                 # Classes e models (ApiError, etc)
│   │   │   ├── realtime/               # Cliente de WebSocket
│   │   │   ├── schemas/                # Schemas de validação (Zod)
│   │   │   └── utils/                  # Funções utilitárias (formatação, exibição, etc)
│   │   └── notifications/              # Sistema global de notificações
│   └── types/                          # Definições de tipos TypeScript compartilhados
├── scripts/                            # Scripts utilitários (release, demo, openapi, diagrama do banco)
└── tests/                              # Testes do backend (pytest)
```

Na raiz ficam também `main.py` (a entrada da aplicação), `pyproject.toml` e `uv.lock` (as dependências do Python), `config.toml` e `example.env` (as configurações), `cliff.toml` (o changelog) e o `CHANGELOG.md`.

---

## Atualização da Árvore de Estrutura

O script abaixo gera a árvore completa do projeto, com todas as subpastas:

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
- **Arquivos utilitários:** `kebab-case.ts` (`goal-metrics.ts`, `income-tax.ts`)
- **Componentes:** `PascalCase`
- **Funções:** `camelCase()`
- **Hooks:** `useNomeDoHook()`
- **Constantes:** `SCREAMING_SNAKE_CASE`
- **Variáveis:** `camelCase`

**Exemplo:**
```typescript
// frontend/shared/components/base-card.tsx
export const BaseCard = () => { ... }

// frontend/shared/hooks/useAuth.ts
export const useAuth = () => { ... }

// frontend/shared/lib/utils/display.ts
export function displayMoney(value: number) { ... }
```

---

## Próximos Passos

- [Ciclo de Desenvolvimento com BD](./ciclo-banco-dados) — Como trabalhar com banco de dados
- [Diretrizes Async vs Sync](./async-vs-sync) — Padrões de código assíncrono
- [Contribuindo](./contribuindo) — Como enviar suas mudanças
