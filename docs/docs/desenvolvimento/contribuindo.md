---
sidebar_position: 6
---

# Contribuindo

Saiba como contribuir com código, reportar bugs ou sugerir melhorias para o Simulador Financeiro.

## Antes de Começar

### 1. Fork do Repositório

Faça um **fork** do repositório para sua conta do GitHub:

1. Acesse [github.com/LiloMarino/SimuladorFinanceiro](https://github.com/LiloMarino/SimuladorFinanceiro)
2. Clique no botão "Fork" no canto superior direito
3. Aguarde a criação do fork na sua conta

### 2. Clone o Fork

Clone o repositório forkado para sua máquina local:

```bash
git clone https://github.com/seu-usuario/SimuladorFinanceiro.git
cd SimuladorFinanceiro
```

### 3. Configure o Upstream

Adicione o repositório original como remote `upstream`:

```bash
git remote add upstream https://github.com/LiloMarino/SimuladorFinanceiro.git
```

Isso permite que você mantenha seu fork atualizado com as mudanças do projeto original.

---

## Tipos de Contribuição

### 🐛 Reportar Bugs

Encontrou um problema? Ajude-nos a corrigi-lo!

1. **Verifique se já foi reportado:** Procure nas [Issues](https://github.com/LiloMarino/SimuladorFinanceiro/issues) existentes
2. **Abra uma nova Issue:** Se não encontrou, crie uma nova
3. **Descreva o problema detalhadamente:**
   - **Título claro:** Ex: "Erro ao importar CSV com dados de ações"
   - **Sistema operacional:** Windows/Linux/macOS e versão
   - **Versão da aplicação:** Release ou commit
   - **Passos para reproduzir:** Liste exatamente o que fazer para ver o bug
   - **Resultado esperado:** O que deveria acontecer
   - **Resultado atual:** O que aconteceu de fato
   - **Screenshots/logs:** Se aplicável

**Exemplo de boa issue:**
```markdown
## Descrição
Ao importar arquivo CSV com mais de 1000 linhas, a aplicação trava.

## Ambiente
- SO: Windows 11
- Versão: v1.0.0

## Passos para reproduzir
1. Ir em Importar Ativos > CSV
2. Selecionar arquivo `dados.csv` (1500 linhas)
3. Clicar em "Importar"
4. Aplicação trava sem mensagem de erro

## Esperado
CSV deveria ser importado com sucesso.

## Atual
Aplicação congela e precisa ser fechada.
```

---

### 💡 Sugerir Melhorias

Tem uma ideia para melhorar o projeto?

1. **Abra uma [Discussion](https://github.com/LiloMarino/SimuladorFinanceiro/discussions)** na categoria "Ideas"
2. **Descreva sua ideia:**
   - O que você quer que seja adicionado/mudado
   - Por que isso seria útil
   - Como você imagina que funcionaria
3. **Aguarde feedback da comunidade**
4. **Se aprovado**, uma Issue será criada para rastrear a implementação

---

### 📖 Melhorar Documentação

Documentação sempre pode ser melhorada!

- Corrija erros de digitação ou gramática
- Adicione exemplos faltantes
- Esclareça seções confusas
- Adicione screenshots

O processo é o mesmo de contribuir com código (veja abaixo).

---

### 🔧 Contribuir com Código

#### Passo 1: Crie uma Branch

Sempre crie uma branch nova para suas mudanças:

```bash
git checkout -b feature/minha-feature
```

**Convenções de nome de branch:**
- `feature/nome` - Para novas funcionalidades
- `fix/nome` - Para correções de bugs
- `docs/nome` - Para mudanças na documentação
- `refactor/nome` - Para refatorações

**Exemplos:**
- `feature/add-bitcoin-support`
- `fix/import-csv-crash`
- `docs/improve-installation-guide`

#### Passo 2: Faça suas Mudanças

- Escreva código limpo e bem comentado
- Siga as convenções do projeto (veja [Estrutura de Pastas](./estrutura-pastas))
- Mantenha mudanças focadas no objetivo da branch

#### Passo 3: Teste suas Mudanças

**Backend:**
```bash
# Executar testes (se existirem)
python -m pytest

# Executar a aplicação e testar manualmente
python main.py
```

**Frontend:**
```bash
cd frontend

# Executar linter
pnpm lint

# Executar testes (se existirem)
pnpm test

# Executar a aplicação e testar manualmente
pnpm dev
```

#### Passo 4: Commit suas Mudanças

Use mensagens de commit claras e descritivas:

```bash
git add .
git commit -m "feat: adicionar suporte a importação de Bitcoin"
```

**Convenções de Commit (Conventional Commits):**
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Mudanças na documentação
- `refactor:` - Refatoração de código
- `test:` - Adicionar/modificar testes
- `chore:` - Tarefas de manutenção

**Exemplos:**
```bash
git commit -m "feat: adicionar gráfico de candlestick na tela de ações"
git commit -m "fix: corrigir crash ao importar CSV com linhas vazias"
git commit -m "docs: atualizar guia de instalação com PostgreSQL"
git commit -m "refactor: melhorar performance do cálculo de carteira"
```

#### Passo 5: Push para seu Fork

```bash
git push origin feature/minha-feature
```

#### Passo 6: Abra uma Pull Request

1. Acesse seu fork no GitHub
2. Clique em "Compare & pull request"
3. **Base repository:** `LiloMarino/SimuladorFinanceiro` - `main`
4. **Head repository:** `seu-usuario/SimuladorFinanceiro` - `feature/minha-feature`
5. Preencha o template da PR:
   - **Título claro:** Ex: "Adicionar suporte a importação de Bitcoin"
   - **Descrição:** O que foi mudado e por quê
   - **Issues relacionadas:** Use `Closes #123` para fechar issues automaticamente
   - **Screenshots:** Se aplicável (especialmente para mudanças visuais)
6. Marque os checkboxes (testes, linter, etc.)
7. Clique em "Create pull request"

---

## Diretrizes de Código

### Python (Backend)

- **Siga [PEP 8](https://pep8.org/)**
- **Use type hints:**
  ```python
  def calculate_profit(initial: float, final: float) -> float:
      return final - initial
  ```
- **Escreva docstrings:**
  ```python
  def calculate_profit(initial: float, final: float) -> float:
      """
      Calcula o lucro de um investimento.
      
      Args:
          initial: Valor inicial investido
          final: Valor final do investimento
          
      Returns:
          Lucro obtido (final - initial)
      """
      return final - initial
  ```
- **Nomes descritivos:**
  - Classes: `PascalCase`
  - Funções/variáveis: `snake_case`
  - Constantes: `SCREAMING_SNAKE_CASE`

### TypeScript/React (Frontend)

- **Use ESLint + Prettier** (configuração já presente no projeto)
- **Escreva tipos explícitos:**
  ```typescript
  interface User {
    id: number;
    name: string;
    balance: number;
  }
  
  function getUser(id: number): User {
    // ...
  }
  ```
- **Evite `any`:** Use tipos específicos ou `unknown` se realmente não souber o tipo
- **Nomes descritivos:**
  - Componentes: `PascalCase`
  - Funções/variáveis: `camelCase`
  - Hooks: `useNomeDoHook`
- **Componentes funcionais:**
  ```typescript
  export const Button = ({ label, onClick }: ButtonProps) => {
    return <button onClick={onClick}>{label}</button>;
  };
  ```

---

## Processo de Review

1. **Um mantenedor revisará seu código**
   - Pode levar alguns dias, tenha paciência
2. **Podem ser solicitadas mudanças**
   - Seja receptivo ao feedback
   - Faça as mudanças solicitadas
   - Faça push novamente (a PR será atualizada automaticamente)
3. **Uma vez aprovado, será feito merge na `main`**
4. **Parabéns!** 🎉 Sua contribuição está no projeto

---

## Mantendo seu Fork Atualizado

Periodicamente, sincronize seu fork com o repositório original:

```bash
# Buscar mudanças do upstream
git fetch upstream

# Mudar para sua branch main
git checkout main

# Fazer merge das mudanças do upstream
git merge upstream/main

# Atualizar seu fork no GitHub
git push origin main
```

---

## Código de Conduta

Esperamos que todos os contribuidores:

- Sejam respeitosos e colaborativos
- Dêem e recebam feedback de forma construtiva
- Foquem no que é melhor para o projeto e a comunidade
- Demonstrem empatia com outros membros da comunidade

---

## Licença

Ao contribuir, você concorda que seu código será licenciado sob [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0).

Isso significa que:
- Seu código será open-source
- Outros podem usar, modificar e distribuir (mantendo a licença GPL-3.0)
- Você mantém seus direitos autorais

---

## Dúvidas?

- **Issues técnicas:** Abra uma [Issue](https://github.com/LiloMarino/SimuladorFinanceiro/issues)
- **Discussões gerais:** Use [Discussions](https://github.com/LiloMarino/SimuladorFinanceiro/discussions)
- **Contato direto:** [@LiloMarino](https://github.com/LiloMarino)

**Obrigado por contribuir!** 🙌
