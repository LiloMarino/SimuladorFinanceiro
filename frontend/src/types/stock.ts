/** Dados de um ativo retornado na listagem geral */
export type Stock = {
  ticker: string;
  name: string;
  price: number;
  low: number;
  high: number;
  volume: number;
  open: number;
  date: string; // ISO
  change: number;
  change_pct: string; // "+1.23%"
};

/** Registro histórico de preço (candlestick) */
export type StockCandle = {
  date: string; // ISO
  close: number;
  open: number;
  low: number;
  high: number;
  volume: number;
};

/** Detalhamento completo de um ativo (para a página individual) */
export type StockDetails = {
  ticker: string;
  name: string;
  price: number;
  low: number;
  high: number;
  volume: number;
  change: number;
  change_pct: string;
  history: StockCandle[];
};
