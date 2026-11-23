import { describe, expect, it } from "vitest";
import type { PortfolioState } from "@/types";
import { allocationRows } from "./allocation-rows";

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
      portfolio([{ kind: "FGTS", value: "250", networth_pct: "0.25", exit_rule: "Sai na demissão" }]),
    );
    expect(rows.at(-1)).toMatchObject({
      label: "FGTS",
      value: "250",
      pct: "0.25",
      color: "bg-chart-7",
      exitRule: "Sai na demissão",
    });
  });

  it("usa o percentual que o servidor entrega para cada linha", () => {
    const rows = allocationRows(
      portfolio([
        { kind: "FGTS", value: "300", networth_pct: "0.3", exit_rule: "a" },
        { kind: "PENSION", value: "100", networth_pct: "0.1", exit_rule: "b" },
      ] as unknown as LockedAsset[]),
    );
    expect(rows.slice(-2).map((r) => r.pct)).toEqual(["0.3", "0.1"]);
  });
});
