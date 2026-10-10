---
sidebar_position: 5
---

# Diagrama do Banco de Dados

O schema atual do banco, com cada tabela, suas colunas e as relações entre elas. Para a forma de alterar o schema, veja o [Ciclo de Desenvolvimento com Banco de Dados](./ciclo-banco-dados.md).

:::info Página gerada
Esta página é gerada a partir de `backend/core/models/models.py` por `pnpm db:erd`. O `tests/test_erd.py` falha enquanto ela estiver diferente dos models.
:::

**Como ler:** `PK` é chave primária, `FK` é chave estrangeira e `UK` é valor único. Uma linha liga a tabela referenciada (lado `||`, exatamente um) à que guarda a chave estrangeira (lado `o{`, zero ou mais), e o rótulo é a coluna da chave. Uma coluna marcada `nullable` aceita nulo. Coluna de `ENUM` tem como tipo o nome do `ENUM`, e os valores aceitos estão em [Valores dos ENUM](#valores-dos-enum). Uma tabela que aparece só com o nome está detalhada na outra seção.

## Partidas e jogadores

Cada partida, quem joga nela, e os eventos e snapshots que reconstroem a carteira de cada jogador.

```mermaid
erDiagram
    direction LR
    event_cashflow {
        bigint id PK
        bigint simulation_id FK
        integer user_id FK
        cashflow_event_type event_type
        numeric amount
        date event_date
        timestamptz created_at
    }
    event_equity {
        bigint id PK
        bigint simulation_id FK
        integer user_id FK
        integer stock_id FK
        equity_event_type event_type
        integer quantity
        numeric price
        date event_date
        timestamptz created_at
    }
    event_fixed_income {
        bigint id PK
        bigint simulation_id FK
        integer user_id FK
        bigint asset_id FK
        fixed_income_event_type event_type
        numeric amount
        date event_date
        timestamptz created_at
    }
    simulations {
        bigint id PK
        text name UK
        date start_date
        date end_date
        numeric starting_cash
        numeric monthly_contribution
        boolean price_impact_enabled
        double price_impact_k
        integer price_impact_decay_days
        timestamptz created_at
        timestamptz last_simulated_at
    }
    snapshots {
        bigint simulation_id PK, FK
        integer user_id PK, FK
        date snapshot_date PK
        numeric total_equity
        numeric total_fixed
        numeric total_cash
        numeric total_contribution
        numeric total_networth
        timestamptz created_at
    }
    users {
        integer id PK
        uuid client_id UK
        text nickname UK
        timestamptz created_at
        jsonb settings
    }
    simulations ||--o{ event_cashflow : simulation_id
    users ||--o{ event_cashflow : user_id
    simulations ||--o{ event_equity : simulation_id
    stock ||--o{ event_equity : stock_id
    users ||--o{ event_equity : user_id
    fixed_income_asset ||--o{ event_fixed_income : asset_id
    simulations ||--o{ event_fixed_income : simulation_id
    users ||--o{ event_fixed_income : user_id
    simulations ||--o{ snapshots : simulation_id
    users ||--o{ snapshots : user_id
```

## Ativos e indicadores

Os ativos negociáveis com o setor e o segmento de cada um, o histórico de preços e os indicadores econômicos, com a origem de cada valor (real ou gerado) e o registro das buscas.

```mermaid
erDiagram
    direction LR
    economic_indicator_history {
        indicator_series series PK
        date ref_date PK
        numeric value
        data_origin origin
    }
    fetch_log {
        indicator_series series PK
        timestamptz attempted_at
        timestamptz succeeded_at "nullable"
    }
    fixed_income_asset {
        bigint id PK
        uuid asset_uuid UK
        text name
        text issuer
        investment_type investment_type
        rate_type rate_type
        date maturity_date
        numeric interest_rate
    }
    sectors {
        integer id PK
        text name UK
    }
    segments {
        integer id PK
        integer sector_id FK
        text name
    }
    stock {
        integer id PK
        text ticker UK
        text name UK
        asset_class asset_class
        integer segment_id FK "nullable"
    }
    stock_price_history {
        integer stock_id PK, FK
        date price_date PK
        double open
        double high
        double low
        double close
        bigint volume
        data_origin origin
    }
    sectors ||--o{ segments : sector_id
    segments |o--o{ stock : segment_id
    stock ||--o{ stock_price_history : stock_id
```

## Valores dos ENUM

| ENUM | Valores | Colunas |
| --- | --- | --- |
| `asset_class` | `STOCK`, `FII`, `ETF`, `BDR` | `stock.asset_class` |
| `cashflow_event_type` | `DEPOSIT`, `WITHDRAW`, `DIVIDEND`, `CONTRIBUTION`, `TAX` | `event_cashflow.event_type` |
| `data_origin` | `REAL`, `GENERATED` | `economic_indicator_history.origin`, `stock_price_history.origin` |
| `equity_event_type` | `BUY`, `SELL` | `event_equity.event_type` |
| `fixed_income_event_type` | `BUY`, `REDEEM` | `event_fixed_income.event_type` |
| `indicator_series` | `CDI`, `SELIC`, `IPCA`, `IBOV` | `economic_indicator_history.series`, `fetch_log.series` |
| `investment_type` | `CDB`, `LCI`, `LCA`, `TESOURO_DIRETO` | `fixed_income_asset.investment_type` |
| `rate_type` | `SELIC`, `IPCA`, `CDI`, `PREFIXADO` | `fixed_income_asset.rate_type` |
