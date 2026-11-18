import { describe, expect, it } from "vitest";
import type { MarketQuote, SimulationEvents } from "@/types";
import { applyStocksUpdate } from "./market-quotes";

type Candle = SimulationEvents["stocks_update"]["stocks"][number];

const quote = (ticker: string, priceDate: string, sparkline: number[]) =>
  ({ ticker, price_date: priceDate, close: sparkline.at(-1), sparkline, fund: false }) as MarketQuote;

const candle = (ticker: string, priceDate: string, close: number) =>
  ({ ticker, price_date: priceDate, close }) as Candle;

describe("applyStocksUpdate", () => {
  it("no mesmo dia, o último ponto do mini gráfico segue o fechamento", () => {
    const { quotes, hasUnknown } = applyStocksUpdate(
      [quote("PETR4", "2024-03-01", [10, 11, 12])],
      [candle("PETR4", "2024-03-01", 13)],
    );
    expect(quotes[0]?.sparkline).toEqual([10, 11, 13]);
    expect(quotes[0]?.close).toBe(13);
    expect(hasUnknown).toBe(false);
  });

  it("num pregão novo, o ponto mais antigo sai e o fechamento entra", () => {
    const { quotes } = applyStocksUpdate(
      [quote("PETR4", "2024-03-01", [10, 11, 12])],
      [candle("PETR4", "2024-03-04", 13)],
    );
    expect(quotes[0]?.sparkline).toEqual([11, 12, 13]);
  });

  it("vela de ticker que a lista não tem marca a lista como desatualizada", () => {
    const { quotes, hasUnknown } = applyStocksUpdate(
      [quote("PETR4", "2024-03-01", [10])],
      [candle("AURO11", "2024-03-01", 100)],
    );
    expect(quotes).toHaveLength(1);
    expect(hasUnknown).toBe(true);
  });
});
