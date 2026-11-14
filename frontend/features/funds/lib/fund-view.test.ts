import { describe, expect, it } from "vitest";
import { fundStage, managerQuotasOf, managerShareOf, netWorthOf } from "./fund-view";

describe("fundStage", () => {
  it("sem data de listagem a gestora está fechada", () => {
    expect(fundStage({ listed_on: null, offer_remaining: null })).toBe("closed");
  });

  it("listada com saldo a vender está em oferta", () => {
    expect(fundStage({ listed_on: "2024-03-01", offer_remaining: "300" })).toBe("offer");
  });

  it("listada sem oferta aberta já é negociada", () => {
    expect(fundStage({ listed_on: "2024-03-01", offer_remaining: null })).toBe("listed");
  });
});

describe("leituras da página", () => {
  const holders = [
    { kind: "player", user_id: 7, nickname: "Ana", color: "chart-1", quotas: "5800", share: "0.58" },
    { kind: "bot", user_id: null, nickname: "Bot", color: null, quotas: "4200", share: "0.42" },
  ] as const;

  it("o patrimônio soma as classes", () => {
    // 40.000 + 100.000 + 60.000 = 200.000
    const composition = [
      { asset_class: "cash", value: "40000", fraction: "0.2" },
      { asset_class: "stocks", value: "100000", fraction: "0.5" },
      { asset_class: "fixed_income", value: "60000", fraction: "0.3" },
    ] as const;
    expect(netWorthOf({ composition: [...composition] })).toBe(200_000);
  });

  it("a parte e as cotas do gestor vêm da linha dele nos cotistas", () => {
    const fund = { holders: [...holders], manager_user_id: 7 };
    expect(managerShareOf(fund)).toBeCloseTo(0.58, 6);
    expect(managerQuotasOf(fund)).toBe(5800);
  });

  it("sem linha do gestor, a parte é zero", () => {
    expect(managerShareOf({ holders: [...holders], manager_user_id: 99 })).toBe(0);
  });
});
