import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import type { HousePick, MarketQuote } from "@/types";
import { MarketTable } from "./market-table";

const quote = (ticker: string): MarketQuote => ({
  id: 1,
  ticker,
  name: `Empresa ${ticker}`,
  asset_class: "STOCK",
  origin: "DOMESTIC",
  open: 30,
  high: 31,
  low: 29,
  close: 30.5,
  volume: 1000,
  price_date: "2012-03-07",
  change: 0.5,
  change_pct: 0.0166,
  sparkline: [30, 30.2, 30.5],
  sector: null,
  segment: null,
  state_owned: false,
  fund: false,
});

function render(housePicks: ReadonlyMap<string, HousePick["side"]>) {
  return renderToStaticMarkup(
    <MemoryRouter>
      <MarketTable
        quotes={[quote("PETR4"), quote("VALE3")]}
        holdings={new Map()}
        housePicks={housePicks}
        message={null}
      />
    </MemoryRouter>,
  );
}

describe("MarketTable", () => {
  it("marca com o selo a ação que está no relatório da casa, com o lado", () => {
    const html = render(new Map<string, HousePick["side"]>([["PETR4", "buy"]]));
    expect(html).toContain("Casa: compra");
    expect(html).not.toContain("Casa: venda");
  });

  it("mostra o selo de venda na ação recomendada para vender", () => {
    const html = render(new Map<string, HousePick["side"]>([["VALE3", "sell"]]));
    expect(html).toContain("Casa: venda");
  });

  it("sem relatório, nenhuma ação leva o selo", () => {
    const html = render(new Map());
    expect(html).not.toContain("Casa:");
  });
});
