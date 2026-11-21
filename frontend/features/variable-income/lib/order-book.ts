import type { Order } from "@/types";
import { displayNumber, displayQuantity } from "@/shared/lib/utils/display";

/** Quantas ofertas cada coluna mostra antes do "Mostrar todas". */
export const BOOK_ROWS = 8;

/** Menor largura da barra de quantidade: a oferta pequena continua visível. */
const MIN_BAR_SHARE = 0.012;

type PricedOrder = Order & { limit_price: number };

export type OrderBook = {
  /** Compras abertas, da maior para a menor oferta (a ordem que o backend entrega). */
  buys: PricedOrder[];
  /** Vendas abertas, da menor para a maior oferta (a ordem que o backend entrega). */
  sells: PricedOrder[];
};

export const isOpenOrder = (order: Order) => order.status === "pending" || order.status === "partial";

const hasPrice = (order: Order): order is PricedOrder => order.limit_price !== null;

/** Separa as ordens abertas com preço em compras e vendas, mantendo a prioridade do backend. */
export function splitBook(orders: Order[]): OrderBook {
  const priced = orders.filter(isOpenOrder).filter(hasPrice);
  return {
    buys: priced.filter((order) => order.action === "buy"),
    sells: priced.filter((order) => order.action === "sell"),
  };
}

/** A ordem `a` fica antes da `b` na fila do livro: compras da maior para a menor oferta, depois vendas da menor para a maior. */
function queuesBefore(a: Order, b: Order) {
  if (a.action !== b.action) return a.action === "buy";
  const [x, y] = [a.limit_price ?? 0, b.limit_price ?? 0];
  return a.action === "buy" ? x >= y : x <= y;
}

/**
 * Aplica ao livro o aviso de uma ordem. A fila é por preço e, no mesmo preço, por chegada:
 * a ordem nova entra no fim do degrau do preço dela, e a que mudou fica onde estava.
 * A ordem que deixou de estar aberta sai do livro.
 */
export function applyOrderEvent(orders: Order[], order: Order): Order[] {
  const index = orders.findIndex((item) => item.id === order.id);
  if (!isOpenOrder(order)) return index === -1 ? orders : orders.filter((item) => item.id !== order.id);
  if (index !== -1) return orders.map((item) => (item.id === order.id ? order : item));
  // A fila está ordenada: a nova fica depois de todas as ordens que têm prioridade sobre ela
  const position = orders.filter((item) => queuesBefore(item, order)).length;
  return [...orders.slice(0, position), order, ...orders.slice(position)];
}

/** Preço típico do dia, `(máxima + mínima + fechamento) / 3`: o centro das ofertas do Mercado. */
export function typicalPrice({ high, low, close }: { high: number; low: number; close: number }) {
  return (high + low + close) / 3;
}

export type Spread = { amount: number; percent: number };

/** Diferença entre a melhor venda e a melhor compra, em reais e em fração do preço típico. */
export function bookSpread(book: OrderBook, typical: number): Spread | null {
  const bestBuy = book.buys[0];
  const bestSell = book.sells[0];
  if (!bestBuy || !bestSell || typical <= 0) return null;
  const amount = bestSell.limit_price - bestBuy.limit_price;
  return { amount, percent: amount / typical };
}

/** Largura da barra (0 a 1): a quantidade da oferta sobre a maior do livro, com piso. */
export function barShare(order: Order, largest: number) {
  if (largest <= 0) return MIN_BAR_SHARE;
  return Math.min(1, Math.max(MIN_BAR_SHARE, Number(order.remaining) / largest));
}

/** Maior quantidade aberta entre os dois lados: a régua comum das barras. */
export function largestQuantity(book: OrderBook) {
  return Math.max(0, ...[...book.buys, ...book.sells].map((order) => Number(order.remaining)));
}

/** Casas da diferença percentual: as que bastam para não zerar (0,16% e 0,002%). */
export function spreadPercentDigits(percent: number) {
  return percent === 0 || percent >= 0.0001 ? 2 : 3;
}

/** Quantidade das colunas: de 1 milhão em diante vira "4,82 mi", para caber na linha. */
export function displayBookQuantity(value: string) {
  const quantity = Number(value);
  return quantity >= 1_000_000 ? `${displayNumber(quantity / 1_000_000, 2)} mi` : displayQuantity(value);
}

/** "2024-01-02" vira "02/01", o dia em que a ordem foi posta. */
export function displayDayMonth(date: string) {
  const [, month, day] = date.split("-");
  return `${day}/${month}`;
}

const OFFER_SOURCE: Partial<Record<Order["owner"], string>> = {
  market: "do Mercado",
  fund_maker: "do Mercado",
  fund_issuer: "da oferta pública",
};

/** Quem pôs a oferta, para o texto da boleta: "a venda de R$ 12,35 do Mercado". */
export function describeOffer(order: Order, price: string) {
  const side = order.action === "sell" ? "a venda" : "a compra";
  return `${side} de ${price} ${OFFER_SOURCE[order.owner] ?? `de ${order.player_nickname}`}`;
}
