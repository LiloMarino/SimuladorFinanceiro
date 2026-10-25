---
sidebar_position: 7
---

# Contribuindo

Este é um projeto **pessoal e em evolução**, mas contribuições são bem-vindas 🙂

Se você encontrou um bug, tem uma sugestão ou quer enviar código, abaixo está o fluxo esperado.

---

## Issues e Discussions

Antes de qualquer mudança em código:

- 🐛 **Bugs / problemas técnicos**  
  → Abra uma **[Issue](https://github.com/LiloMarino/SimuladorFinanceiro/issues)**  
  

- 💡 **Ideias, dúvidas ou sugestões**  
  → Use **[Discussions](https://github.com/LiloMarino/SimuladorFinanceiro/discussions)**  
  

Não precisa formalidade excessiva — contexto claro já ajuda bastante.

---

## Enviando Código (Pull Request)

Se quiser contribuir com código ou documentação:

### 1. Fork e clone

```bash
git clone https://github.com/<seu-usuario>/SimuladorFinanceiro.git
cd SimuladorFinanceiro
````

(opcional, mas recomendado)

```bash
git remote add upstream https://github.com/LiloMarino/SimuladorFinanceiro.git
```

---

### 2. Crie uma branch

```bash
git checkout -b feature/minha-alteracao
```

Sugestões de prefixo:

* `feature/` – funcionalidade nova
* `fix/` – correção de bug
* `docs/` – documentação
* `refactor/` – refatoração

---

### 3. Faça as mudanças

* Mantenha a alteração **focada**
* Evite misturar refatoração grande com feature
* Se for algo maior, vale abrir uma Issue antes

---

### 4. Confira, commite e envie

Na raiz, rode a checagem completa (ruff, pyright, pytest, oxlint, oxfmt, tsc e vitest). Se ela acusar formatação, `pnpm format` formata o backend e o frontend:

```bash
pnpm run check
```

Dois casos pedem um passo a mais:

* Mudou uma rota ou DTO do backend: rode `pnpm openapi`, que regenera o `docs/openapi.json` e os tipos do frontend (o teste de OpenAPI falha se estiverem defasados)
* Mudou os models: rode `pnpm db:revision "descrição"` para gerar a migration, como explica o [Ciclo de Desenvolvimento com BD](./ciclo-banco-dados.md)

Os testes que usam banco precisam do `POSTGRES_DATABASE_URL` configurado; sem ele, são pulados.

```bash
git add .
git commit -m "feat: Adicionada a descrição curta da mudança"
git push origin feature/minha-alteracao
```

A mensagem do commit é só a linha de assunto, no formato `tipo: Descrição`: o tipo em minúsculas (`feat`, `fix`, `docs`, `refactor`, `build`, `test`, `chore`, `ci`, `perf` ou `style`), sem escopo, e a descrição em português, no particípio e com a primeira letra maiúscula (`fix: Corrigido o saldo negativo na compra`).

O commit que quebra compatibilidade (partida salva que deixa de abrir, chave do `config.toml` removida ou renomeada) leva um `!` depois do tipo: `feat!: Removido o campo X do config.toml`. É dos commits que sai o número da próxima versão, como explica a página [Versionamento](./versionamento.md).

---

### 5. Abra a Pull Request

* Base: `main`
* Descreva **o que mudou** e **por quê**
* Se existir Issue relacionada, mencione (`Closes #123`)

---

## Observações

- O projeto é mantido por uma única pessoa, então análises de PR podem levar um tempo
- Nem toda ideia será aceita, mas toda sugestão é válida para discussão
- Feedback e contribuições são sempre bem-vindos

---

## Licença

Ao contribuir, você concorda que seu código será licenciado sob **GPL-3.0**, assim como o restante do projeto.

