---
sidebar_position: 2
---

# Recomendações Gerais

Recomendações para melhor experiência ao usar o Simulador Financeiro.

## Banco de Dados

### SQLite (Padrão)

Por padrão, o simulador utiliza **SQLite**, que é mais simples e não requer configuração adicional. O banco de dados é criado automaticamente no arquivo `database.db` na pasta do projeto.

**Vantagens:**
- Não requer instalação ou configuração
- Ideal para uso pessoal e desenvolvimento
- Funciona out-of-the-box

**Limitações:**
- Menor performance em cenários com múltiplos usuários simultâneos
- Pode ter problemas com concorrência em multiplayer intenso

### PostgreSQL (Recomendado para Multiplayer)

Para melhor performance em sessões multiplayer, recomendamos usar **PostgreSQL**.

#### Instalação do PostgreSQL

**Windows:**
1. Baixe o instalador em [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Execute o instalador e siga as instruções
3. Anote a senha do usuário `postgres`
4. Deixe a porta padrão `5432`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

#### Configuração no Simulador

1. Crie um arquivo `.env` na raiz do projeto (baseado no `example.env`)
2. Configure a connection string do PostgreSQL:
   ```env
   DATABASE_URL=postgresql+psycopg://postgres:<senha>@localhost:5432/simulador_financeiro
   ```
3. Reinicie o simulador

O banco de dados e as tabelas serão criados automaticamente na primeira execução.

## Comunicação em Tempo Real

O simulador suporta dois métodos de comunicação em tempo real:

### WebSocket (Recomendado)

O **WebSocket** é o método padrão e recomendado por ser mais estável e eficiente.

**Vantagens:**
- Comunicação bidirecional eficiente
- Menor latência
- Melhor performance
- Mais testado e estável

### Server-Sent Events (SSE)

O **SSE** é uma alternativa mais simples, mas menos testada.

**Quando usar:**
- Se você tiver problemas de compatibilidade com WebSocket
- Para ambientes com restrições de proxy/firewall

#### Ativar SSE

Edite o arquivo `config.toml` na raiz do projeto:

```toml
[realtime]
use_sse = true
```

:::warning Menos Testado
O modo SSE é menos testado que o WebSocket e pode apresentar comportamentos inesperados. Use apenas se necessário.
:::

## Performance e Otimização

### Recomendações de Hardware

Para melhor experiência, especialmente em multiplayer:

- **RAM:** 4 GB ou mais
- **Processador:** Dual-core ou superior
- **Conexão:** Internet estável (para multiplayer e dados de mercado)

### Velocidade da Simulação

O simulador permite controlar a velocidade do tempo:

- **1x**: Velocidade normal
- **2x**: Dobro da velocidade
- **4x**: Quatro vezes mais rápido
- **10x**: Dez vezes mais rápido

:::tip
Em sessões multiplayer intensas, velocidades muito altas podem causar lag. Recomendamos 1x ou 2x para melhor experiência.
:::
