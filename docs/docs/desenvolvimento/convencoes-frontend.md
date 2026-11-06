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

Mutation segue a mesma regra: um hook `useVerboX(params)` por arquivo, em `hooks/mutations/`
(da feature ou de `shared/`). O componente nunca chama `apiFetch` direto: toda chamada à API
mora em `hooks/queries/` ou `hooks/mutations/`.

O hook guarda o que vale para qualquer chamada: o `mutationFn`, o trabalho no cache
(`invalidateQueries`, `setQueryData`, update otimista) e o aviso de erro. O que mexe no estado
do componente entra na chamada, como callback do `mutate`:

```typescript
// features/variable-income/hooks/mutations/useSubmitOrder.ts
export function useSubmitOrder(ticker: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (order: SubmitOrderRequest) =>
      apiFetch<SubmitOrderResponse>(`/api/variable-income/${ticker}/orders`, { method: "POST", body: order }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.portfolioPosition(ticker) }),
    onError: (err) => toastApiError(err),
  });
}

// features/variable-income/components/order-ticket.tsx
submit.mutate(
  { action, type: kind, quantity, limit_price: limitPrice },
  { onSuccess: () => setQuantityText("") },
);
```

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

---

## Tabelas e texto

- A tabela cabe na tela em 1920 de largura sem rolagem lateral, e em 1366 nada passa da
  borda. Para caber, nesta ordem: a informação secundária vai para o hover, duas colunas
  viram uma, o texto quebra em duas linhas (`wrap` em `TableHead` e `TableCell`). A rolagem
  lateral fica para tabela larga por natureza, como a matriz de correlação.
- Nenhum texto abaixo de 12 px: use `text-xs` ou maior. O teste
  `shared/lib/min-text-size.test.ts` falha se uma classe `text-[Npx]` com N menor que 12
  entrar no código.
- Texto pequeno usa `text-muted-foreground` ou `text-faint-foreground`, ambos com contraste
  mínimo de 4,5:1 sobre os fundos do app.

---

## Ícones

- O ícone sai do `lucide-react`. Só quando o lucide não tem o desenho (marca de uma
  instituição, símbolo do design) entra um ícone próprio.
- Ícone próprio é um componente em `frontend/shared/components/icons/`, um arquivo por
  ícone, escrito como SVG dentro de um `forwardRef<SVGSVGElement, LucideProps>`. Com o
  mesmo contrato do lucide ele entra em qualquer lugar que espera um `LucideIcon` (como
  `icon` do `NavItem`), sem adaptador. Exemplo: `treasury-icon.tsx`.
- O SVG vem do design ou da fonte externa e é colado como está, com estas trocas: o
  tamanho vem da prop `size`, a cor vem de `currentColor` (nada de hex, o oxlint barra),
  e o `id` de máscara, gradiente ou `clipPath` vem de `useId()`, porque dois ícones na
  mesma página com o mesmo `id` se desenham um no outro.
- Ícone próprio é monocromático e herda a cor do texto, como os vizinhos. O fundo
  colorido, quando existe, é do componente que usa o ícone.
- Não há SVGR nem importação de `.svg` como componente: são poucos ícones e o arquivo
  `.tsx` já é o que o TypeScript, o oxlint e o Knip enxergam.

---

## Testes

O Vitest cobre as contas que o navegador faz: função pura de cálculo ou de formatação, sem
componente, tela ou teste ponta a ponta.

- o teste mora ao lado do arquivo testado: `shared/lib/goal.ts` → `shared/lib/goal.test.ts`;
- o valor esperado é calculado à mão, com a conta num comentário quando não é óbvia;
- `describe`, `it` e `expect` vêm de `import { ... } from "vitest"`, e o `tsc` confere os testes
  junto com o resto;
- o Vitest reaproveita o `vite.config.ts` (alias `@` incluído) e roda com `pnpm run front:test`,
  que também entra no `pnpm run check`.

```typescript
// shared/lib/financial-independence.test.ts
it("é a despesa de um ano dividida pela taxa de retirada", () => {
  // 12 × 5.000 = 60.000 por ano; a 4%, precisa de 1.500.000
  expect(independenceGoal(5000, 0.04)).toBeCloseTo(1_500_000, 6);
});
```
