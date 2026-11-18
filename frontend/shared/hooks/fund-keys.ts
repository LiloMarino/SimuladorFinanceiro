/** Chaves de query das gestoras: tudo vive debaixo de ["funds"], junto com a lista de contas do caixa. */
export const fundKeys = {
  all: () => ["funds"] as const,
  list: () => ["funds", "list"] as const,
  detail: (fundId: number) => ["funds", "detail", fundId] as const,
  tickerCheck: (ticker: string) => ["funds", "ticker-check", ticker] as const,
  issuancePreview: (fundId: number, quotas: number) => ["funds", "issuance-preview", fundId, quotas] as const,
  subscriptionPreview: (fundId: number, quotas: number) => ["funds", "subscription-preview", fundId, quotas] as const,
  buybackPreview: (fundId: number, quantity: number, maxPrice: string) =>
    ["funds", "buyback-preview", fundId, quantity, maxPrice] as const,
};
