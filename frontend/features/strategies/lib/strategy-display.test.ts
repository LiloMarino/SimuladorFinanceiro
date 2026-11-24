import { describe, expect, it } from "vitest";
import type { StrategyOrderLine, StrategyPanel, StrategyParam } from "@/types";
import { creditTitle, dayOrdersSummary, orderToastTitle } from "@/shared/lib/strategy-orders";
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
  return {
    action,
    ticker: "PETR4",
    asset_name: null,
    quantity: "300",
    price: "18.40",
    status: "executed",
    reason: null,
    asset_uuid: null,
    annual_rate: null,
    term_months: null,
    loan_number: null,
  };
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
    {
      key: "short_window",
      label: "Média curta",
      kind: "int",
      default: 50,
      min: 5,
      max: 100,
      unit: "dias",
      hint: "",
      enabled_by: null,
    },
    {
      key: "tickers",
      label: "Ações",
      kind: "tickers",
      default: ["PETR4"],
      min: null,
      max: null,
      unit: null,
      hint: "",
      enabled_by: null,
    },
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
      {
        key: "asset",
        label: "Ativo",
        kind: "ticker",
        default: "BOVA11",
        min: null,
        max: null,
        unit: null,
        hint: "",
        enabled_by: null,
      },
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
      enabled_by: null,
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
      enabled_by: null,
    });
    expect(hint).toBe("Padrão 20% · de 5% a 100%");
  });
});

describe("linhas de crédito", () => {
  // Contratação leva o prazo; as demais, o número do empréstimo
  const credit = (action: StrategyOrderLine["action"], number: number, annual_rate: string | null = null) => ({
    ...line(action),
    ticker: null,
    quantity: null,
    price: "20000.00",
    annual_rate,
    term_months: action === "take_loan" ? number : null,
    loan_number: action === "take_loan" ? null : number,
  });

  it("escreve cada ação pelo valor, prazo e número do empréstimo", () => {
    expect(creditTitle(credit("take_loan", 48, "0.153"))).toMatch(
      /^Empréstimo · R\$\s20\.000,00 em 48x · 15,3% a\.a\.$/,
    );
    expect(creditTitle(credit("prepay_loan", 3))).toMatch(/^Amortização de R\$\s20\.000,00 no empréstimo nº 3$/);
    expect(creditTitle(credit("payoff_loan", 3))).toBe("Quitação do empréstimo nº 3");
    expect(creditTitle(credit("pay_overdue", 3))).toBe("Atraso pago do empréstimo nº 3");
  });

  it("entra no resumo do dia e no aviso", () => {
    expect(dayOrdersSummary([credit("take_loan", 48), credit("payoff_loan", 1)])).toBe("1 empréstimo e 1 quitação");
    expect(orderToastTitle({ ...credit("payoff_loan", 3), status: "refused" })).toBe(
      "Recusada: Quitação do empréstimo nº 3",
    );
  });
});

describe("parâmetro booleano", () => {
  const leverage: StrategyParam = {
    key: "leverage",
    label: "Alavancar",
    kind: "boolean",
    default: false,
    min: null,
    max: null,
    unit: null,
    hint: "",
    enabled_by: null,
  };

  it("o rascunho ligado ou desligado vira o valor, sem texto numérico", () => {
    expect(fromDraft([leverage], { leverage: true })).toEqual({ leverage: true });
    expect(fromDraft([leverage], { leverage: false })).toEqual({ leverage: false });
    expect(rangeHint(leverage)).toBeNull();
  });
});
