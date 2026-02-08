---
sidebar_position: 4
---

# Ciclo de Desenvolvimento com Banco de Dados


O ciclo de desenvolvimento do projeto é feito **exclusivamente com PostgreSQL** como banco principal.

O **SQLite** existe apenas para uso simples e rápido (out-of-the-box), conforme descrito em
[Recomendações Gerais](../como-usar/recomendacoes.md), e **não deve ser considerado a fonte de verdade do schema**.

Durante o desenvolvimento, **o PostgreSQL é tratado como o banco canônico**.

---

## Configuração do Banco de Dados (PostgreSQL)

1. **Instalar PostgreSQL:**

   * Windows: [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)
   * Linux: `sudo apt install postgresql`
   * macOS: `brew install postgresql`

2. **Criar banco de dados:**

   ```sql
   CREATE DATABASE simulador_financeiro;
   ```

3. **Configurar `.env`:**

   ```env
   DATABASE_URL=postgresql+psycopg://postgres:sua_senha@localhost:5432/simulador_financeiro
   ```

4. **Iniciar a aplicação:**

   ```bash
   python main.py
   ```

As tabelas serão criadas automaticamente se não existirem.

---

## Ciclo de Desenvolvimento

O fluxo de trabalho para alterações no banco de dados é:

1. ✏️ **Editar o schema no PostgreSQL** (via ferramenta gráfica ou SQL manual)
2. 📥 **Sincronizar o banco local** (tabelas e relações atualizadas)
3. 🧬 **Gerar modelos ORM com `sqlacodegen`** (quando fizer sentido)
4. 🛠️ **Ajustar modelos manualmente** quando a alteração for pequena

---

### Passo 1: Editar o Schema no PostgreSQL

Você pode editar o schema usando ferramentas como **pgAdmin** ou **DataGrip**, ou editar manualmente via SQL.

#### Opção A: Ferramentas gráficas

1. Edite as tabelas, colunas e relações na ferramenta
2. Aplique as mudanças no banco local

#### Opção B: SQL manual

1. Edite o SQL das tabelas e relações
2. Execute os comandos diretamente no banco local

---

### Passo 2: Sincronizar o banco local

Se as alterações foram feitas via ferramenta gráfica, elas já são aplicadas no banco local.

Se foram feitas manualmente, execute os scripts SQL:

```bash
psql -U postgres -d simulador_financeiro -f schema_changes.sql
```

---

### Passo 3: Gerar ORM com `sqlacodegen`

O `sqlacodegen` lê o schema existente no banco de dados e gera automaticamente os modelos SQLAlchemy.

**Instalação:**

```bash
pip install sqlacodegen
```

**Gerar modelos:**

```bash
sqlacodegen postgresql+psycopg://postgres:<senha>@localhost:5432/simulador_financeiro > backend/core/models/models.py
```

Substitua `<senha>` pela senha do seu banco PostgreSQL.

:::tip Quando usar sqlacodegen
O `sqlacodegen` é mais útil quando há **mudanças grandes no schema**.
Para alterações pequenas, normalmente é melhor editar diretamente o arquivo  `backend/core/models/models.py`.
:::

:::warning Código gerado não é final
O código gerado pelo `sqlacodegen` **serve como ponto de partida e deve ser revisado.**.

É comum ajustar manualmente:
- Relacionamentos
- Enums
- Tipos customizados
- Defaults e constraints
- Incompatibilidades entre bancos (ex: tipos específicos do PostgreSQL que não existem no SQLite)
:::


---

## Criação Automática de Tabelas

O projeto cria automaticamente as tabelas **em ambientes limpos ou no primeiro run**, com base nos modelos ORM:

```python
Base.metadata.create_all(bind=engine)
```

Isso é útil para:

* Primeiro setup
* SQLite
* Ambientes de teste

No desenvolvimento contínuo com PostgreSQL, o schema deve ser tratado como **database-first**.


---

## Dicas e Boas Práticas

### Teste Ambos os Bancos

Sempre teste as mudanças em **PostgreSQL e SQLite**, lembrando que o comportamento pode variar:

```bash
# Testar com SQLite (remova DATABASE_URL do .env)
python main.py

# Testar com PostgreSQL
DATABASE_URL=postgresql+psycopg://... python main.py
```

SQLite é apenas um apoio para desenvolvimento rápido e para usuários sem PostgreSQL instalado/configurado.

---

### Evite SQL Raw

Sempre que possível, use o ORM do SQLAlchemy para garantir compatibilidade entre bancos.

**Evite:**

```python
session.execute("SELECT * FROM users WHERE id = 1")
```

**Prefira:**

```python
session.get(User, 1)
```

ou, em consultas mais complexas:

```python
stmt = select(User).where(User.id == 1)
session.execute(stmt).scalar_one_or_none()
```

---

## Próximos Passos

* [Diretrizes Async vs Sync](./async-vs-sync.md)
* [Estrutura de Pastas](./estrutura-pastas.md)

