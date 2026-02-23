---
sidebar_position: 1
---

# Instalação

Esta página explica como baixar e executar o Simulador Financeiro no seu sistema.

## Resumo Rápido

1. Instalar PostgreSQL
2. Baixar o executável
3. Configurar o arquivo `.env`
4. Executar a aplicação

## 1) Instalar PostgreSQL

O Simulador Financeiro usa **PostgreSQL** como banco de dados. Antes de executar o aplicativo, instale e configure o PostgreSQL.

### Instalar PostgreSQL

**Windows:**
1. Baixe o instalador em [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Execute o instalador e siga as instruções
3. Anote a senha do usuário `postgres`
4. Mantenha a porta padrão `5432`

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

### Banco e tabelas: criação automática

Você **não precisa criar manualmente** o banco `simulador_financeiro`.
Na primeira execução, o Simulador cria automaticamente o banco (se não existir) e as tabelas necessárias.

## 2) Download dos Executáveis

Os executáveis estão disponíveis na página de [Releases do GitHub](https://github.com/LiloMarino/SimuladorFinanceiro/releases), escolha a versão mais recente e baixe o arquivo correspondente ao seu sistema operacional.

## 3) Configurar conexão no Simulador
:::tip
O `.env` é criado automaticamente na primeira execução, mas você pode criar e configurar manualmente antes de rodar o executável para evitar esse erro na primeira execução.
:::
1. Crie ou edite o arquivo `.env` presente na **mesma pasta do executável**
2. Configure a variável de ambiente com a URL de conexão do PostgreSQL, substituindo `<senha>` pela senha do usuário `postgres` que você definiu durante a instalação:
   ```env
   POSTGRES_DATABASE_URL=postgresql+psycopg://postgres:<senha>@localhost:5432/simulador_financeiro
   ```

3. Salve o arquivo

## 4) Executar o Simulador

Com o executável baixado e o PostgreSQL configurado, execute o arquivo correspondente ao seu sistema:

### Windows

1. Execute o arquivo `SimuladorFinanceiro.exe` (pode ser necessário permitir a execução em configurações de segurança)
2. Aguarde a inicialização da aplicação
3. Uma aba do navegador será aberta em `http://localhost:8000`; se não abrir, acesse manualmente esse endereço

### Linux

1. Dê permissão de execução ao arquivo `SimuladorFinanceiro`:
   ```bash
   chmod +x SimuladorFinanceiro
   ```
2. Execute o arquivo:
   ```bash
   ./SimuladorFinanceiro
   ```
3. Uma aba do navegador será aberta em `http://localhost:8000`; se não abrir, acesse manualmente esse endereço

### macOS

1. Dê permissão de execução ao arquivo `SimuladorFinanceiro`:
   ```bash
   chmod +x SimuladorFinanceiro
   ```
2. Execute o arquivo:
   ```bash
   ./SimuladorFinanceiro
   ```
3. Uma aba do navegador será aberta em `http://localhost:8000`; se não abrir, acesse manualmente esse endereço

:::warning
No macOS, pode ser necessário permitir a execução de aplicativos de desenvolvedores não identificados nas configurações de segurança.
:::

## Observação de Performance

:::warning
Velocidades muito altas de simulação (como `100x`) podem causar muito lag no navegador, principalmente em páginas com muitas atualizações em tempo real.
:::

## Problemas Comuns

### Erro de conexão com o banco

- Verifique se o PostgreSQL está rodando
- Confirme a senha do usuário `postgres`
- Verifique se a porta `5432` está correta

## Instalação a partir do Código-Fonte

Se você é desenvolvedor ou deseja executar a partir do código-fonte, siga as instruções na seção [Desenvolvimento > Setup do Ambiente](../desenvolvimento/setup.md).
