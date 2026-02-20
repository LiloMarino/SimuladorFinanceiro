---
sidebar_position: 1
---

# Instalação

Esta página explica como baixar e executar o Simulador Financeiro no seu sistema.

## Download dos Executáveis

Os executáveis standalone estão disponíveis na página de [Releases do GitHub](https://github.com/LiloMarino/SimuladorFinanceiro/releases), escolha a versão mais recente e baixe o arquivo correspondente ao seu sistema operacional.


:::info
Os executáveis são standalone e não requerem instalação de Python, Node.js ou outras dependências.
:::

## Como Executar

### Windows

1. Baixe o arquivo `SimuladorFinanceiro.exe`
2. Execute o arquivo (pode ser necessário permitir a execução em configurações de segurança)
3. O navegador abrirá automaticamente em `http://localhost:8000`

### Linux

1. Baixe o arquivo `SimuladorFinanceiro`
2. Dê permissão de execução:
   ```bash
   chmod +x SimuladorFinanceiro
   ```
3. Execute o arquivo:
   ```bash
   ./SimuladorFinanceiro
   ```
4. Acesse `http://localhost:8000` no navegador

### macOS

1. Baixe o arquivo `SimuladorFinanceiro`
2. Dê permissão de execução:
   ```bash
   chmod +x SimuladorFinanceiro
   ```
3. Execute o arquivo:
   ```bash
   ./SimuladorFinanceiro
   ```
4. Acesse `http://localhost:8000` no navegador

:::warning
No macOS, pode ser necessário permitir a execução de aplicativos de desenvolvedores não identificados nas configurações de segurança.
:::

## Primeira Execução

Ao abrir a aplicação pela primeira vez:

1. O banco de dados será criado automaticamente (PostgreSQL)
2. Uma aba do navegador será aberta em `http://localhost:8000`
3. Você verá a tela de login

:::tip
Se a página não abrir automaticamente, acesse manualmente: `http://localhost:8000`
:::

## Instalação a partir do Código-Fonte

Se você é desenvolvedor ou deseja executar a partir do código-fonte, siga as instruções na seção [Desenvolvimento > Setup do Ambiente](../desenvolvimento/setup.md).
