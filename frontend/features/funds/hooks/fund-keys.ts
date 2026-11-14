/** Chaves de query das gestoras: tudo vive debaixo de ["funds"], junto com a lista de contas do caixa. */
export const fundKeys = {
  all: () => ["funds"] as const,
  list: () => ["funds", "list"] as const,
  detail: (fundId: number) => ["funds", "detail", fundId] as const,
  tickerCheck: (ticker: string) => ["funds", "ticker-check", ticker] as const,
};
