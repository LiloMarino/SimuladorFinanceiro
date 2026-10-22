import { describe, expect, it } from "vitest";
import type { StockDetails } from "@/types";
import { mergeStockUpdate } from "./stock-history";

const candle = { id: 1, ticker: "ABCD3", name: "Empresa", asset_class: "STOCK" as const,
  price_date: "2020-01-06", open: 10, close: 11, low: 9, high: 12, volume: 100, change: 1, change_pct: 0.1 };
const detail: StockDetails = { ...candle, history: [{ ...candle }] };

describe("histórico recebido ao pausar", () => {
  it("aguarda o detalhe inicial em vez de criar um histórico vazio pelo WS", () => {
    expect(mergeStockUpdate(undefined, candle)).toBeUndefined();
  });
  it("incorpora o último pregão e substitui o candle sem duplicar a data", () => {
    const next = { ...candle, price_date: "2020-01-07", close: 12, change: 2 };
    const updated = mergeStockUpdate(detail, next);
    expect(updated?.history.map((row) => row.close)).toEqual([11, 12]);
    expect(mergeStockUpdate(updated, { ...next, close: 13 })?.history.map((row) => row.close)).toEqual([11, 13]);
    expect(detail.history).toHaveLength(1);
  });
  it("não regride a cotação quando uma mensagem antiga chega atrasada", () => {
    expect(mergeStockUpdate(detail, { ...candle, price_date: "2020-01-03" })).toBe(detail);
  });
});
