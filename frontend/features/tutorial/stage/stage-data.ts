import type { MarketQuote, Order, Position, StockDetails } from "@/types";

/** Dados fixos dos exemplos: o palco mostra sempre os mesmos números. */

/** Série suave que termina no fechamento, para o mini gráfico de 30 dias da lista. */
const sparklineTo = (close: number, drift: number) =>
  Array.from({ length: 30 }, (_, i) => close * (1 - drift * ((29 - i) / 29) + 0.004 * Math.sin(i * 1.7)));

const quote = (
  id: number,
  ticker: string,
  name: string,
  close: number,
  changePct: number,
  volume: number,
): MarketQuote => ({
  id,
  ticker,
  name,
  asset_class: "STOCK",
  open: close * (1 - changePct / 2),
  high: close * 1.012,
  low: close * 0.988,
  close,
  volume,
  price_date: "2023-03-14",
  change: close * changePct,
  change_pct: changePct,
  sparkline: sparklineTo(close, changePct * 3),
  sector: null,
  segment: null,
});

export const STAGE_QUOTES: MarketQuote[] = [
  quote(1, "PETR4", "Petrobras PN", 38.12, 0.018, 48_200_000),
  quote(2, "VALE3", "Vale ON", 61.4, -0.006, 31_500_000),
  quote(3, "ITUB4", "Itaú Unibanco PN", 27.85, 0.003, 27_900_000),
  quote(4, "BBAS3", "Banco do Brasil ON", 45.02, 0.024, 18_300_000),
  quote(5, "WEGE3", "WEG ON", 36.77, -0.011, 12_100_000),
  quote(6, "ABEV3", "Ambev ON", 13.94, 0.001, 22_800_000),
];

export const STAGE_STOCK: StockDetails = {
  ticker: "PETR4",
  name: "Petrobras PN",
  asset_class: "STOCK",
  open: 37.6,
  high: 38.3,
  low: 37.45,
  close: 38.12,
  volume: 48_200_000,
  price_date: "2023-03-14",
  change: 0.67,
  change_pct: 0.018,
  history: [],
};

/** A posição de PETR4 logo depois da compra de 100 ações. */
export const STAGE_POSITION: Position = {
  ticker: "PETR4",
  size: "100",
  reserved: "0",
  total_cost: "3812.00",
  avg_price: "38.12",
  current_price: "38.12",
  current_value: "3812.00",
  return_value: "0.00",
  return_pct: "0",
};

const sellOrder = (id: string, size: string, price: number): Order => ({
  id,
  player_nickname: "Mercado",
  player_color: null,
  action: "sell",
  order_type: "limit",
  status: "pending",
  size,
  remaining: size,
  limit_price: price,
  created_at: "2023-03-14T10:00:00",
  synthetic: true,
});

/** O livro de quem vende PETR4, da menor venda para a maior. */
export const STAGE_SELL_BOOK: Order[] = [
  sellOrder("s1", "500", 38.12),
  sellOrder("s2", "300", 38.15),
  sellOrder("s3", "800", 38.2),
];

/** A ordem limitada do jogador: compra 100 a R$ 37,50, esperando alguém vender nesse preço. */
export const STAGE_MY_LIMIT_ORDER: Order = {
  id: "m1",
  player_nickname: "Lilo",
  player_color: null,
  action: "buy",
  order_type: "limit",
  status: "pending",
  size: "100",
  remaining: "100",
  limit_price: 37.5,
  created_at: "2023-03-14T10:05:00",
  synthetic: false,
};
