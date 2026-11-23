import { describe, expect, it } from "vitest";
import type { PortfolioState } from "@/types";
import { lockedDistributionNote, lockedHeadline } from "@/shared/lib/locked-assets";
import { allocationRows, outsideCash } from "./allocation-rows";

type LockedAsset = PortfolioState["locked_assets"][number];

const portfolio = (lockedAssets: LockedAsset[]) =>
  ({
    variable_income_value: "0",
    variable_income_networth_pct: "0",
    fixed_income_value: "0",
    fixed_income_networth_pct: "0",
    cash: "750",
    cash_pct: "0.75",
    locked_assets: lockedAssets,
  }) as unknown as PortfolioState;

describe("allocationRows", () => {
  it("não cria linha de patrimônio de profissão quando não há nenhum", () => {
    expect(allocationRows(portfolio([])).map((r) => r.label)).toEqual(["Renda variável", "Renda fixa", "Caixa"]);
  });

  it("cria uma linha por patrimônio travado, com a regra de saída", () => {
    const rows = allocationRows(
      portfolio([
        { kind: "FGTS", value: "250", networth_pct: "0.25", exit_rule: "Sai na demissão", since: null, note: null },
      ]),
    );
    expect(rows.at(-1)).toMatchObject({
      label: "FGTS",
      value: "250",
      pct: "0.25",
      color: "bg-chart-7",
      exitRule: "Sai na demissão",
    });
  });

  it("dá a cada tipo travado o nome do tipo", () => {
    const rows = allocationRows(
      portfolio([
        {
          kind: "COMPANY_CAPITAL",
          value: "300",
          networth_pct: "0.3",
          exit_rule: "Só vira caixa vendendo uma parte",
          since: null,
          note: null,
        },
      ]),
    );
    expect(rows.at(-1)?.label).toBe("Capital da empresa");
  });

  it("o patrimônio em imóveis leva o nome Imóveis e a regra de saída do servidor", () => {
    const rows = allocationRows(
      portfolio([
        {
          kind: "REAL_ESTATE",
          value: "900000",
          networth_pct: "0.6",
          exit_rule: "Vender leva 1 mês e custa 5% de ITBI e corretagem",
          since: null,
          note: null,
        },
      ]),
    );
    expect(rows.at(-1)).toMatchObject({ label: "Imóveis", value: "900000", pct: "0.6" });
    expect(rows.at(-1)?.exitRule).toContain("Vender leva 1 mês");
  });

  it("usa o percentual que o servidor entrega para cada linha", () => {
    const rows = allocationRows(
      portfolio([
        { kind: "FGTS", value: "300", networth_pct: "0.3", exit_rule: "a" },
        { kind: "COMPANY_CAPITAL", value: "100", networth_pct: "0.1", exit_rule: "b" },
      ] as unknown as LockedAsset[]),
    );
    expect(rows.slice(-2).map((r) => r.pct)).toEqual(["0.3", "0.1"]);
  });
});

const withTotals = (lockedAssets: LockedAsset[], totals: Partial<PortfolioState>) => ({
  ...portfolio(lockedAssets),
  ...totals,
});

describe("outsideCash", () => {
  it("sem patrimônio travado, é só o investido", () => {
    const state = withTotals([], {
      invested_value: "200",
      invested_pct: "0.2",
      locked_value: "0",
      locked_networth_pct: "0",
    });
    expect(outsideCash(state)).toEqual({ value: 200, pct: 0.2 });
  });

  it("soma o patrimônio travado ao investido, em valor e em fração", () => {
    const state = withTotals([], {
      invested_value: "200",
      invested_pct: "0.2",
      locked_value: "540",
      locked_networth_pct: "0.54",
    });
    expect(outsideCash(state)).toEqual({ value: 740, pct: 0.74 });
  });
});

describe("lockedHeadline", () => {
  const asset = (kind: LockedAsset["kind"], value: string) =>
    ({ kind, value, networth_pct: "0", exit_rule: "x" }) as unknown as LockedAsset;

  it("não há frase sem patrimônio travado", () => {
    expect(lockedHeadline(portfolio([]))).toBeUndefined();
    expect(lockedDistributionNote(portfolio([]))).toBeUndefined();
  });

  it("o Locador lê a frase dos imóveis e o aviso da distribuição", () => {
    const state = portfolio([asset("REAL_ESTATE", "540000")]);
    expect(lockedHeadline(state)).toBe(
      "Quase tudo em imóveis: o aluguel é a sua renda, e o valor deles conta no patrimônio.",
    );
    expect(lockedDistributionNote(state)).toContain("acompanha o IVG-R");
  });

  it("com dois tipos travados, vale o de maior saldo", () => {
    const state = portfolio([asset("FGTS", "300"), asset("PENSION", "900")]);
    expect(lockedHeadline(state)).toContain("previdência");
  });

  it("todo tipo travado tem frase própria", () => {
    for (const kind of ["FGTS", "COMPANY_CAPITAL", "PENSION", "WELFARE_SAVINGS", "REAL_ESTATE"] as const) {
      expect(lockedHeadline(portfolio([asset(kind, "1")]))).toBeTruthy();
    }
  });
});
