/** Chaves de query das gestoras: tudo vive debaixo de ["funds"], junto com a lista de contas do caixa. */
export const fundKeys = {
  all: () => ["funds"] as const,
  list: () => ["funds", "list"] as const,
  offers: () => ["funds", "offers"] as const,
  detail: (fundId: number) => ["funds", "detail", fundId] as const,
  tickerCheck: (ticker: string) => ["funds", "ticker-check", ticker] as const,
  issuancePreview: (fundId: number, quotas: number) => ["funds", "issuance-preview", fundId, quotas] as const,
  subscriptionPreview: (fundId: number, quotas: number) => ["funds", "subscription-preview", fundId, quotas] as const,
  directedPreview: (fundId: number, quotas: number) => ["funds", "directed-preview", fundId, quotas] as const,
  mergePreview: (fundId: number, daughterFundId: number) => ["funds", "merge-preview", fundId, daughterFundId] as const,
  buybackPreview: (fundId: number, quantity: number, maxPrice: string) =>
    ["funds", "buyback-preview", fundId, quantity, maxPrice] as const,
  report: (fundId: number, month: string) => ["funds", "report", fundId, month] as const,
};

const PREVIEW_KINDS = new Set([
  "issuance-preview",
  "subscription-preview",
  "directed-preview",
  "merge-preview",
  "buyback-preview",
]);

/** A chave é de uma prévia de operação da gestora `fundId`. */
export const isFundPreviewOf = (fundId: number, queryKey: readonly unknown[]) =>
  queryKey[0] === "funds" && PREVIEW_KINDS.has(queryKey[1] as string) && queryKey[2] === fundId;
