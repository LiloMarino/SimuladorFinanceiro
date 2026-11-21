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
`applyRealtime`. Todo consumidor do hook recebe o dado novo:

```typescript
// shared/hooks/queries/usePortfolio.ts
useRealtime("portfolio_update", ({ portfolio, account }) => {
  void applyRealtime(queryClient, queryKeys.portfolioOf(eventAccountKey(account)), portfolio);
});
```

O evento que mexe em várias queries, ou que também navega, fica no componente que orquestra
a tela (página ou provider). Exemplo: `simulation_ended` no `SimulationProvider` invalida as
estatísticas, troca de rota e renova o status da partida.

### Avisos que carregam o dado

O aviso do websocket carrega o dado novo, e o front o aplica no cache. A leitura HTTP busca
na abertura da tela e quando a conexão volta; entre uma e outra, a tela vive do que os avisos
entregam.

- **`applyRealtime`** (`shared/lib/realtime/apply-realtime.ts`) é o jeito de aplicar: cancela a
  leitura em voo da chave (`cancelQueries`) e só então faz `setQueryData`. Uma resposta HTTP que
  saiu antes do aviso não chega depois dele e desfaz o que ele entregou.
- **`applyRealtimeDelta`** serve ao aviso que acrescenta ao que a tela já tem (o ponto novo de
  uma série, uma ordem do livro). A função `merge` é pura e mora em `lib/`, com teste. Quando
  o aviso não encaixa no que a tela tem, `merge` devolve `null` e a chave é lida de novo.
- **Dado derivado do pedido do cliente** (prévia da ordem, indicadores técnicos) usa assinatura
  com parâmetro: a rota HTTP responde na hora e o servidor guarda o último pedido do cliente no
  ativo; a cada pregão ele recalcula para quem ainda assina e entrega só àquele cliente, em
  `order_preview:{ticker}` e `indicators_update:{ticker}`; a cotação da boleta de renda fixa
  segue o mesmo molde em `fixed_income_projection:{id}`, com o valor digitado no pedido. O aviso devolve o pedido que o
  gerou, e o hook só aplica o que corresponde ao pedido atual da tela. A ordem que deixa de caber vai no mesmo aviso, com o motivo (`refused`); a chave da prévia guarda a prévia ou o motivo, venha da leitura HTTP ou do aviso. Recusa de regra é 409 ou 422, a mesma lista nos dois lados (`fetchPreviewOutcome` e `refusal_reason`); permissão, recurso inexistente e falha do servidor seguem como erro.
- **Dado igual para todos** (padrões de vela, estatal do ativo) vai num evento por ativo,
  `candle_patterns_update:{ticker}` e `state_company_update:{ticker}`, calculado só para quem o assina.
- **Dado por jogador** (Fundo Soberano, crédito, títulos do Tesouro, vida financeira, pendências,
  páginas das gestoras) é montado para cada assinante e entregue só a ele, com `to=`. O dado de
  uma conta de gestora chega marcado com o `account` dela, e o hook só aplica o que é da conta
  ativa (`eventAccountKey(account)`).
- **Painéis do governo e da eleição** (eleição, mapa, campanha, promessas, balanços, governo, base,
  orçamento) têm cada um o seu evento com o DTO da rota (`GovernmentFeed`), entregue a cada
  assinante com `to=` quando muda com quem olha; o botão da ação não renova nada, e o
  `government_update` carrega só o fato (com o dado do toast e do diálogo).
- **Publicação uma vez por operação**: o caixa e as gestoras mudam em vários pontos da mesma
  operação (a compra, a taxa, a oferta). Cada ponto só marca a mudança, e o dado sai uma vez, ao
  fechar a operação mais externa (`synchronized`), já no estado final. O pregão marca todas as
  contas e publica o dia por tela (`DayFeed`, `CashFeed`, `FundsFeed`).
- **O que não mudou não sai**: o catálogo do Tesouro guarda o último enviado e só um catálogo
  diferente volta a sair; a série do Tesouro recebe o ponto novo (`merge` por mês) só na virada
  do mês; o crédito sai quando a conta muda e, depois do pregão, nas contas com parcela em atraso.
- **Prévias abertas na página da gestora** (emissão, subscrição, oferta dirigida, fusão e
  recompra) seguem o molde da prévia da ordem: a rota responde na hora e registra o pedido; o
  servidor recalcula para quem ainda assina quando muda algo que a prévia lê (a gestora, o caixa
  pessoal de quem pediu, o caixa da gestora, o dia) e entrega só àquele cliente, em
  `fund_issuance_preview:{id}` e nos irmãos, com os parâmetros do pedido e a prévia ou a recusa
  (`refused`). A prévia igual à última enviada não sai de novo, e o hook só aplica o que
  corresponde ao pedido atual da tela.
- **Registro da estratégia** pagina por id (`before`, a última linha da página anterior), então a
  linha nova não repete nem pula nenhuma. `strategy_log_update` leva a conta, as linhas novas ou
  mudadas (já com id) e o total de cada filtro; `mergeStrategyLog` coloca a linha nova no topo da
  primeira página, troca a mudada pelo id e devolve `null` quando o total não fecha.
- **Reconexão**: `useRefetchOnReconnect`, montado no `SimulationProvider`, lê uma vez as
  consultas ativas que ficaram desatualizadas durante a queda. A primeira conexão não dispara nada.

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
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: queryKeys.portfolioPosition(ticker) }),
    onError: (err) => toastApiError(err),
  });
}

// features/variable-income/components/order-ticket.tsx
submit.mutate(
  { action, type: kind, quantity, limit_price: limitPrice },
  { onSuccess: () => setQuantityText("") },
);
```

O `isPending` da mutation solta quando o servidor confirma: a releitura do cache roda em segundo
plano, com `void` na frente do `invalidateQueries`. O callback que devolve a promessa da
releitura segura o botão até a leitura terminar, e com a partida andando essa leitura disputa a
fila com o próprio jogo. Aguardar a releitura só cabe quando o passo seguinte depende do dado novo.

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
  `shared/lib/min-text-size.test.ts` falha se uma classe `text-[Npx]` ou um `fontSize`
  literal com N menor que 12 entrar no código. O texto de gráfico (eixos, rótulos, tooltip)
  usa `CHART_TICK` e `CHART_FONT_SIZE` de `shared/lib/chart-text.ts`; onde 12 px não cabe, o
  gráfico mostra menos marcas ou abrevia o rótulo.
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
  `.tsx` já é o que o TypeScript, o oxlint e o Knip enxergam. Passou de uns 10 ícones
  próprios, ou os SVGs começaram a chegar prontos de fora em volume, vale reavaliar o
  `vite-plugin-svgr`, que converte cada `.svg` em componente sem copiar o desenho à mão.
- O `forwardRef` é o que mantém o ícone compatível com o tipo `LucideIcon`, que ainda é um
  `ForwardRefExoticComponent`. Quando o lucide trocar esse tipo, os ícones próprios trocam
  junto, um arquivo por vez.
- A regra `shadcn/no-raw-colors` vale na pasta de ícones: a máscara usa `fill-white` e
  `fill-black`. Chegou um ícone colorido de verdade, ou um SVG externo cheio de hex, o
  caminho é um `override` do oxlint para `frontend/shared/components/icons/**` que
  desliga só essa regra.

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
