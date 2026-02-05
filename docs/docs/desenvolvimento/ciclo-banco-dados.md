---
sidebar_position: 3
---

# Ciclo de Desenvolvimento com Banco de Dados

Como trabalhar com o banco de dados durante o desenvolvimento do projeto.

## Visão Geral

O projeto suporta **PostgreSQL** (recomendado para produção) e **SQLite** (desenvolvimento). O sistema detecta automaticamente qual banco usar baseado nas variáveis de ambiente e cria as tabelas automaticamente.

## Bancos Suportados

### SQLite (Padrão para Desenvolvimento)

- Arquivo `database.db` na raiz do projeto
- Não requer instalação ou configuração
- Ideal para desenvolvimento local

### PostgreSQL (Recomendado para Produção)

- Melhor performance
- Suporte a concorrência
- Recomendado para multiplayer

---

## Ciclo de Desenvolvimento

O fluxo de trabalho para alterações no banco de dados é:

1. ✏️ **Editar modelo** (no MySQL Workbench ou diretamente no código)
2. 📥 **Sincronizar o banco de dados PostgreSQL** (se usando)
3. 🧬 **Gerar ORM com sqlacodegen**
4. 🛠️ **Compatibilizar com múltiplos bancos** (PostgreSQL e SQLite)

### Passo 1: Editar o Modelo

Você pode editar o modelo de duas formas:

#### Opção A: MySQL Workbench (.mwb)

Se você usa MySQL Workbench para design visual do banco:

1. Abra o arquivo `.mwb` (se existir)
2. Faça as alterações necessárias
3. Forward engineer para o banco PostgreSQL

#### Opção B: Diretamente no Código

Ou edite os modelos SQLAlchemy diretamente em `backend/core/models/models.py`.

### Passo 2: Sincronizar com PostgreSQL

Se você estiver usando PostgreSQL e fez mudanças diretamente no banco:

```bash
# Conecte-se ao banco e execute os scripts SQL necessários
psql -U postgres -d simulador_financeiro -f schema_changes.sql
```

### Passo 3: Gerar ORM com sqlacodegen

O `sqlacodegen` lê o schema do banco de dados e gera automaticamente os modelos SQLAlchemy.

**Instalação:**
```bash
pip install sqlacodegen
```

**Gerar modelos:**

```bash
sqlacodegen postgresql+psycopg://postgres:<senha>@localhost:5432/simulador_financeiro > backend/core/models/models.py
```

Substitua `<senha>` pela senha do seu banco PostgreSQL.

:::tip
O sqlacodegen facilita muito o desenvolvimento, pois você não precisa escrever os modelos manualmente. Ele reflete o schema real do banco.
:::

### Passo 4: Compatibilizar com SQLite

**Atenção:** PostgreSQL e SQLite têm algumas diferenças de tipos de dados. A principal incompatibilidade é o tipo **JSONB**.

#### Problema: JSONB

PostgreSQL tem o tipo `JSONB` (JSON binário), mas SQLite não suporta.

**Exemplo de problema:**
```python
# Gerado pelo sqlacodegen para PostgreSQL
class Simulation(Base):
    __tablename__ = 'simulations'
    
    config = Column(JSONB, nullable=False)  # ❌ Não funciona no SQLite
```

**Solução:**

Use o tipo `JSON` do SQLAlchemy, que é compatível com ambos:

```python
from sqlalchemy import JSON

class Simulation(Base):
    __tablename__ = 'simulations'
    
    config = Column(JSON, nullable=False)  # ✅ Funciona em ambos
```

O SQLAlchemy converte automaticamente:
- **PostgreSQL:** Usa `JSONB` internamente
- **SQLite:** Usa `TEXT` e faz serialização/deserialização automaticamente

:::warning Atenção
Sempre verifique os modelos gerados pelo sqlacodegen e substitua `JSONB` por `JSON` para garantir compatibilidade.
:::

---

## Criação Automática de Tabelas

O projeto cria automaticamente as tabelas no primeiro run:

```python
# No arquivo de inicialização
Base.metadata.create_all(bind=engine)
```

Isso significa que você **não precisa** criar as tabelas manualmente. O SQLAlchemy faz isso para você baseado nos modelos.

---

## Migrations (Futuro)

Atualmente, o projeto não usa migrations (Alembic), mas isso pode ser adicionado no futuro para melhor controle de versão do schema.

**Vantagens de usar Alembic:**
- Histórico de mudanças no schema
- Rollback de mudanças
- Deploy mais seguro

Se você quiser implementar, consulte a [documentação do Alembic](https://alembic.sqlalchemy.org/).

---

## Configuração do Banco de Dados

### SQLite (Padrão)

Não requer configuração. O arquivo `database.db` é criado automaticamente.

### PostgreSQL

1. **Instalar PostgreSQL:**
   - Windows: [postgresql.org/download](https://www.postgresql.org/download/windows/)
   - Linux: `sudo apt install postgresql`
   - macOS: `brew install postgresql`

2. **Criar banco de dados:**
   ```sql
   CREATE DATABASE simulador_financeiro;
   ```

3. **Configurar `.env`:**
   ```env
   DATABASE_URL=postgresql+psycopg://postgres:sua_senha@localhost:5432/simulador_financeiro
   ```

4. **Reiniciar aplicação:**
   ```bash
   python main.py
   ```
   
   As tabelas serão criadas automaticamente.

---

## Dicas e Boas Práticas

### Use PostgreSQL em Produção

Mesmo que SQLite seja prático para desenvolvimento, use PostgreSQL em produção:
- Melhor performance
- Suporte a concorrência (importante para multiplayer)
- Mais robusto

### Teste Ambos os Bancos

Sempre teste suas mudanças em **ambos** SQLite e PostgreSQL para garantir compatibilidade:

```bash
# Testar com SQLite (remova DATABASE_URL do .env)
python main.py

# Testar com PostgreSQL (adicione DATABASE_URL ao .env)
DATABASE_URL=postgresql+psycopg://... python main.py
```

### Evite SQL Raw

Sempre que possível, use o ORM do SQLAlchemy ao invés de SQL raw. Isso garante compatibilidade entre bancos.

**Evite:**
```python
session.execute("SELECT * FROM users WHERE id = 1")
```

**Prefira:**
```python
session.query(User).filter_by(id=1).first()
```

---

## Problemas Comuns

### "relation does not exist"

O banco não tem as tabelas. Execute o app para criá-las automaticamente:
```bash
python main.py
```

### Tipos incompatíveis

Verifique se você está usando tipos compatíveis. Especialmente `JSONB` → `JSON`.

### Conexão recusada

Verifique se o PostgreSQL está rodando:
```bash
# Linux
sudo systemctl status postgresql

# macOS
brew services list
```

---

## Próximos Passos

- [Diretrizes Async vs Sync](../async-vs-sync) — Padrões de código assíncrono/síncrono
- [Estrutura de Pastas](./estrutura-pastas) — Entenda a organização do código
