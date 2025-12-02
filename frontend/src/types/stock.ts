/** Dados de um ativo retornado na listagem geral */
export type Stock = {
  ticker: string;
  name: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  price_date: string; // ISO
  change: number;
  change_pct: string;
};

/** Registro histórico de preço (candlestick) */
export type StockCandle = {
  price_date: string; // ISO
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

/** Detalhamento completo de um ativo (para a página individual) */
export type StockDetails = Stock & {
  history: StockCandle[];
};
