import { describe, expect, it } from "vitest";
import type { StrategyInfo } from "@/types";
import { paramPills } from "./strategy-params";

const strategy = {
  key: "moving_average",
  params: [
    { key: "short", label: "Média curta", kind: "int", default: 50, min: 5, max: 100, unit: "dias", hint: "" },
    {
      key: "share",
      label: "Quanto do caixa por compra",
      kind: "percent",
      default: 20,
      min: 5,
      max: 100,
      unit: "%",
      hint: "",
    },
    { key: "tickers", label: "Ações que ela opera", kind: "tickers", default: ["PETR4", "VALE3"], hint: "" },
  ],
} as unknown as StrategyInfo;

describe("paramPills", () => {
  it("marca só o que saiu do padrão", () => {
    const pills = paramPills(strategy, { short: 20, share: 20, tickers: ["PETR4", "VALE3"] });
    expect(pills.map((p) => p.changed)).toEqual([true, false, false]);
  });

  it("escreve o valor com a unidade", () => {
    const pills = paramPills(strategy, { short: 20, share: 30, tickers: ["PETR4"] });
    expect(pills.map((p) => p.value)).toEqual(["20 dias", "30%", "1 ação"]);
  });

  it("compara a lista de ações pela ordem e pelo conteúdo", () => {
    const pills = paramPills(strategy, { short: 50, share: 20, tickers: ["VALE3", "PETR4"] });
    expect(pills[2].changed).toBe(true);
  });
});
