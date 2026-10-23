import { describe, expect, it } from "vitest";
import type { StrategyOrderLine, StrategyPanel, StrategyParam } from "@/types";
import { dayOrdersSummary, orderToastTitle } from "@/shared/lib/strategy-orders";
import { cashShare } from "@/shared/lib/strategy-orders";
import { ordersBreakdown } from "./strategy-display";
import { fromDraft, rangeHint, sameValues } from "@/shared/lib/strategy-params";

const PANEL: StrategyPanel = {
  orders_total: 14,
  executed: 11,
  partial: 0,
  open: 2,
  canceled: 1,
  refused: 0,
  return_pct: "0.0382",
  ibov_pct: "-0.012",
  last_order: null,
};

function line(action: StrategyOrderLine["action"]): StrategyOrderLine {
  return { action, ticker: "PETR4", asset_name: null, quantity: "300", price: "18.40", status: "executed", reason: null };
}

describe("ordersBreakdown", () => {
  it("lista só as situações que têm ordem, no plural certo", () => {
    expect(ordersBreakdown(PANEL)).toBe("11 executadas, 2 abertas, 1 cancelada");
  });

  it("sem ordens, diz que não há nenhuma", () => {
    const empty = { ...PANEL, executed: 0, open: 0, canceled: 0, orders_total: 0 };
    expect(ordersBreakdown(empty)).toBe("Nenhuma ordem ainda");
  });
});

describe("cashShare", () => {
  it("é a parte do caixa que cada compra usa", () => {
    // 20% de R$ 41.050,00 = R$ 8.210,00
    expect(cashShare("41050.00", 20)).toBeCloseTo(8210, 6);
  });
});

describe("dayOrdersSummary", () => {
  it("junta compras e vendas do dia", () => {
    const orders = [line("buy"), line("buy"), line("buy"), line("sell")];
    expect(dayOrdersSummary(orders)).toBe("3 compras e 1 venda");
  });

  it("com um só tipo, não leva o e", () => {
    expect(dayOrdersSummary([line("buy"), line("buy")])).toBe("2 compras");
  });
});

describe("orderToastTitle", () => {
  it("diz o que a estratégia fez com a quantidade e o ativo", () => {
    expect(orderToastTitle(line("buy"))).toBe("A estratégia comprou 300 PETR4");
  });

  it("a ordem recusada diz que ela tentou", () => {
    expect(orderToastTitle({ ...line("sell"), status: "refused" })).toBe("A estratégia tentou vender 300 PETR4");
  });
});

describe("fromDraft", () => {
  const params: StrategyParam[] = [
    { key: "short_window", label: "Média curta", kind: "int", default: 50, min: 5, max: 100, unit: "dias", hint: "" },
    { key: "tickers", label: "Ações", kind: "tickers", default: ["PETR4"], min: null, max: null, unit: null, hint: "" },
  ];

  it("converte o texto dos campos numéricos em inteiro", () => {
    expect(fromDraft(params, { short_window: " 30 ", tickers: ["VALE3"] })).toEqual({
      short_window: 30,
      tickers: ["VALE3"],
    });
  });

  it("campo vazio ou com decimal ainda não tem valor", () => {
    expect(fromDraft(params, { short_window: "", tickers: [] })).toBeNull();
    expect(fromDraft(params, { short_window: "3,5", tickers: [] })).toBeNull();
  });

  it("o ativo é o ticker escolhido, e sem ticker ainda não tem valor", () => {
    const withAsset: StrategyParam[] = [
      { key: "asset", label: "Ativo", kind: "ticker", default: "BOVA11", min: null, max: null, unit: null, hint: "" },
      ...params,
    ];
    expect(fromDraft(withAsset, { asset: "VALE3", short_window: "30", tickers: [] })).toEqual({
      asset: "VALE3",
      short_window: 30,
      tickers: [],
    });
    expect(fromDraft(withAsset, { asset: "", short_window: "30", tickers: [] })).toBeNull();
  });
});

describe("sameValues", () => {
  it("compara números e a lista de ações em ordem", () => {
    expect(sameValues({ a: 1, t: ["X", "Y"] }, { a: 1, t: ["X", "Y"] })).toBe(true);
    expect(sameValues({ a: 1, t: ["X", "Y"] }, { a: 1, t: ["Y", "X"] })).toBe(false);
  });
});

describe("rangeHint", () => {
  it("o ativo mostra só o padrão", () => {
    const hint = rangeHint({
      key: "asset",
      label: "Ativo",
      kind: "ticker",
      default: "BOVA11",
      min: null,
      max: null,
      unit: null,
      hint: "",
    });
    expect(hint).toBe("Padrão BOVA11");
  });

  it("mostra o padrão e a faixa, com % quando a unidade é percentual", () => {
    const hint = rangeHint({
      key: "cash_pct",
      label: "",
      kind: "percent",
      default: 20,
      min: 5,
      max: 100,
      unit: "%",
      hint: "",
    });
    expect(hint).toBe("Padrão 20% · de 5% a 100%");
  });
});
