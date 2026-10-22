---
sidebar_position: 1
---

# Instalação

Esta página explica como baixar e executar o Simulador Financeiro no seu sistema.

## Resumo Rápido

**Windows:** baixe o executável e abra. O banco de dados já vem dentro dele.

**Linux e macOS:**

1. Instalar PostgreSQL
2. Baixar o executável
3. Configurar o arquivo `.env`
4. Executar a aplicação

## Windows

### 1) Baixar o executável

Os executáveis estão disponíveis na página de [Releases do GitHub](https://github.com/LiloMarino/SimuladorFinanceiro/releases). Escolha a versão mais recente e baixe `SimuladorFinanceiro-windows.exe`.

:::note
O banco de dados embutido usa o **Microsoft Visual C++ Redistributable (x64)**, que a maioria dos computadores já tem. Se o jogo avisar que ele falta, baixe `vc_redist.x64.exe` na mesma página de Releases (ou no [site da Microsoft](https://aka.ms/vs/17/release/vc_redist.x64.exe)), instale e abra o jogo de novo.
:::

### 2) Executar

1. Execute o arquivo (pode ser necessário permitir a execução nas configurações de segurança do Windows)
2. Aguarde a inicialização da aplicação
3. Uma aba do navegador será aberta em `http://localhost:8000`; se não abrir, acesse manualmente esse endereço

:::info
A **primeira abertura** leva cerca de 10 segundos a mais, porque o jogo prepara o banco de dados. As seguintes abrem mais rápido.
:::

Não é preciso instalar PostgreSQL, criar senha nem editar o `.env`. Mantenha a janela preta (console) aberta enquanto joga: fechá-la encerra o jogo e o banco de dados com segurança.

### Banco de dados embutido

O executável do Windows leva o servidor [PostgreSQL](https://www.postgresql.org/) oficial dentro dele. A cada abertura o servidor sobe só para o seu computador, numa porta livre e protegido por uma senha gerada na primeira vez, e desce quando o jogo fecha.

Os dados e as configurações ficam em `%LOCALAPPDATA%\SimuladorFinanceiro`, e não ao lado do executável. O jogo mostra essa pasta no início do registro da janela preta.

| Item | O que é |
|---|---|
| `db\` | O banco de dados, com as suas partidas salvas |
| `postgres\` | Os programas do PostgreSQL, extraídos na primeira abertura |
| `db.password` | A senha do banco, gerada no seu computador |
| `postgres.log` | O registro do servidor, útil quando algo falha |
| `config.toml` | As configurações do jogo (criado com os valores padrão na primeira abertura) |
| `logs\` | Os registros do jogo |
| `.env` | Criado vazio na primeira abertura; só tem efeito se você preencher `POSTGRES_DATABASE_URL` com um PostgreSQL seu |

- **Backup:** com o jogo fechado, copie a pasta `%LOCALAPPDATA%\SimuladorFinanceiro`.
- **Começar do zero:** com o jogo fechado, apague essa pasta. A próxima abertura cria tudo de novo, **sem as partidas salvas**.
- **Usar um PostgreSQL seu em vez do embutido:** crie um arquivo `.env` em `%LOCALAPPDATA%\SimuladorFinanceiro` com `POSTGRES_DATABASE_URL=...` (veja o formato na seção de Linux e macOS). Com a variável definida, o servidor embutido não sobe.
- **Atualizações:** as partidas salvas passam para a versão nova sozinhas na primeira abertura. A página [Novidades](./novidades.md) diz, a cada versão, o que mudou e se as partidas salvas continuam valendo.

O PostgreSQL é distribuído sob a [licença do PostgreSQL](https://www.postgresql.org/about/licence/), e os textos de licença acompanham os programas em `postgres\<versão>\licenses`.

## Linux e macOS

Nestes sistemas o executável **ainda não leva o banco de dados**: é preciso ter o PostgreSQL instalado.

### 1) Instalar PostgreSQL

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

Defina uma senha para o usuário `postgres` e mantenha a porta padrão `5432`.

#### Banco e tabelas: criação automática

Você **não precisa criar manualmente** o banco `simulador_financeiro`.
Na primeira execução, o Simulador cria automaticamente o banco (se não existir) e as tabelas necessárias.

### 2) Baixar o executável

Na página de [Releases do GitHub](https://github.com/LiloMarino/SimuladorFinanceiro/releases), escolha a versão mais recente e baixe o arquivo do seu sistema (`SimuladorFinanceiro-linux` ou `SimuladorFinanceiro-macos`).

### 3) Configurar a conexão

:::tip
O `.env` é criado automaticamente na primeira execução, mas você pode criar e configurar manualmente antes de rodar o executável para evitar o erro de conexão na primeira execução.
:::

1. Crie ou edite o arquivo `.env` na **pasta de dados do app**: `~/.config/SimuladorFinanceiro` no Linux (ou em `$XDG_CONFIG_HOME/SimuladorFinanceiro`, se essa variável existir) e `~/Library/Application Support/SimuladorFinanceiro` no macOS. O `config.toml` e os `logs` ficam na mesma pasta, e o jogo mostra o caminho no início do registro.
2. Configure a variável de ambiente com a URL de conexão do PostgreSQL, substituindo `<senha>` pela senha do usuário `postgres` que você definiu durante a instalação:
   ```env
   POSTGRES_DATABASE_URL=postgresql+psycopg://postgres:<senha>@localhost:5432/simulador_financeiro
   ```

3. Salve o arquivo

### 4) Executar

1. Dê permissão de execução ao arquivo (`chmod +x SimuladorFinanceiro-linux` ou `chmod +x SimuladorFinanceiro-macos`)
2. Execute o arquivo (`./SimuladorFinanceiro-linux` ou `./SimuladorFinanceiro-macos`)
3. Uma aba do navegador será aberta em `http://localhost:8000`; se não abrir, acesse manualmente esse endereço

:::warning
No macOS, pode ser necessário permitir a execução de aplicativos de desenvolvedores não identificados nas configurações de segurança.
:::

## Observação de Performance

:::warning
Velocidades muito altas de simulação (como `100x`) podem causar muito lag no navegador, principalmente em páginas com muitas atualizações em tempo real.
:::

## Problemas Comuns

### Windows: "O servidor PostgreSQL embarcado não subiu"

A mensagem mostra o fim do `postgres.log`, em `%LOCALAPPDATA%\SimuladorFinanceiro`. As causas mais comuns:

- **Antivírus bloqueando o servidor:** adicione `%LOCALAPPDATA%\SimuladorFinanceiro` às exceções do antivírus e abra o jogo de novo.
- **Falta o Visual C++ Redistributable:** num Windows recém-instalado o jogo avisa que o Windows não encontrou uma DLL do Visual C++. Instale o `vc_redist.x64.exe` que acompanha a release (ou o [Microsoft Visual C++ Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe)) e abra o jogo de novo.
- **Jogo aberto como administrador:** o PostgreSQL recusa rodar com permissão de administrador (a mensagem diz "Execution of PostgreSQL by a user with administrative permissions is not permitted"). Abra o jogo com um duplo clique normal, sem "Executar como administrador".
- **Disco cheio ou pasta sem permissão de escrita:** o jogo precisa de cerca de 200 MB livres em `%LOCALAPPDATA%`.

### Windows: o jogo foi fechado à força ou o computador desligou

Não há risco para as partidas salvas: o banco se recupera sozinho na abertura seguinte, que pode levar alguns segundos a mais.

### Erro de conexão com o banco (PostgreSQL externo)

- Verifique se o PostgreSQL está rodando
- Confirme a senha do usuário `postgres`
- Verifique se a porta `5432` está correta

### Linux e macOS: "POSTGRES_DATABASE_URL não configurada"

O executável desses sistemas não leva o banco. Instale o PostgreSQL e configure o `.env` como descrito acima.

## Instalação a partir do Código-Fonte

Se você é desenvolvedor ou deseja executar a partir do código-fonte, siga as instruções na seção [Desenvolvimento > Setup do Ambiente](../desenvolvimento/setup.md).
