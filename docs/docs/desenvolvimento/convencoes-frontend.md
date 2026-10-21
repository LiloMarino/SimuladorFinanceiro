---
sidebar_position: 3.5
---

# Convenções do Frontend

Como o frontend busca dados da API e monta formulários. Cada seção traz a regra e um
exemplo real do código.

---

## Queries (React Query)

### Toda query é um hook

Cada endpoint lido pelo frontend tem um hook `useX(params)`, num arquivo de mesmo nome dentro
de `hooks/queries/`:

- `features/<feature>/hooks/queries/` quando só aquela feature consome;
- `shared/hooks/queries/` quando mais de uma feature consome.

O componente chama o hook direto no render e usa o resultado como ele vem do `useQuery`:

```typescript
// features/variable-income/hooks/queries/useTrades.ts
export function useTrades(ticker: string, { enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: queryKeys.trades(ticker),
    queryFn: ({ signal }) => apiFetch<Trade[]>(`/api/variable-income/${ticker}/trades`, { signal }),
    enabled,
  });
}

// features/variable-income/components/order-book-card.tsx
const { data: trades } = useTrades(ticker, { enabled: tab === "HISTORY" });
```

Os parâmetros do hook são o que varia entre as chamadas: id, ticker, corpo da requisição,
`enabled` ou um ajuste pontual como o `refetchOnMount` de `useSimulationList`.

### Chave, tipo e erro

- **Chave:** sempre pela fábrica `queryKeys` (`shared/lib/queryKeys.ts`). Invalidar um prefixo
  (`queryKeys.statistics()`) renova todas as queries debaixo dele.
- **Tipo da resposta:** sempre de `@/types`, que reexporta os tipos gerados do OpenAPI. Quando
  falta um alias, ele nasce em `types/api.ts`.
- **Erro:** `ApiError`, registrado como erro padrão do React Query em
  `shared/lib/queryClient.ts`. Por isso `error` já chega tipado em qualquer `useQuery` ou
  `useMutation`.

### Tempo real

O evento que só atualiza a própria query mora dentro do hook dela, com `useRealtime` +
`setQueryData`. Todo consumidor do hook recebe o dado novo:

```typescript
// shared/hooks/queries/usePortfolio.ts
useRealtime("portfolio_update", ({ portfolio }) => {
  queryClient.setQueryData(queryKeys.portfolio(), portfolio);
});
```

O evento que mexe em várias queries, ou que também navega, fica no componente que orquestra
a tela (página ou provider). Exemplo: `simulation_ended` no `SimulationProvider` invalida as
estatísticas, troca de rota e renova o status da partida.

### Mutations

A mutation fica no componente que a dispara, com `useMutation` direto. Ela vira hook quando
mais de um componente a usa (exemplo: `features/lobby/hooks/useChooseColor.ts`).

---

## Formulários

O critério é **onde a validação acontece**.

### React Hook Form + Zod + `Field`

Quando o formulário tem submit e a validação roda no cliente, campo a campo:

- schema Zod no próprio arquivo do formulário, com as mensagens em português;
- `useForm` com `zodResolver`, campos via `Controller` + `Field`/`FieldLabel`/`FieldError`
  de `shared/components/ui/field.tsx`;
- valores iniciais vindos da API chegam já resolvidos pelo componente pai, e entram por
  `values:` ou `defaultValues:` no `useForm`.

Exemplos: `features/auth/pages/login.tsx`, `features/lobby/components/lobby-match.tsx`.

### `useState`

Quando a entrada é um filtro, uma busca, um interruptor que salva na hora, uma confirmação
por digitação, ou quando quem valida é o servidor:

- a boleta (`features/variable-income/components/order-ticket.tsx`) valida a quantidade
  contra o `max_quantity` que a prévia da ordem devolve;
- a zona de perigo (`features/settings/components/danger-zone-card.tsx`) só libera o botão
  quando o nickname digitado confere.
