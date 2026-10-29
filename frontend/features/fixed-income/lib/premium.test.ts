import { describe, expect, it } from "vitest";
import type { Budget, FixedIncomeOffer } from "@/types";
import { hasPremium, premiumSinceStart, premiumTagLabel, rateWithoutPremium, signedPremium } from "./premium";

const asset = (overrides: Partial<FixedIncomeOffer> = {}) =>
  ({
    investment_type: "Tesouro Direto",
    rate_index: "IPCA",
    interest_rate: "0.0628",
    risk_premium: "0.019",
    ...overrides,
  }) as FixedIncomeOffer;

const month = (premium: string, closed = true) => ({ month_end: "2017-01-31", premium, closed });
const budget = (history: ReturnType<typeof month>[], premium: string) =>
  ({ history, month: month(premium) }) as unknown as Pick<Budget, "history" | "month">;

describe("hasPremium", () => {
  it("vale só para Tesouro com prêmio gravado", () => {
    expect(hasPremium(asset())).toBe(true);
    expect(hasPremium(asset({ risk_premium: null }))).toBe(false);
    expect(hasPremium(asset({ investment_type: "CDB" }))).toBe(false);
  });
});

describe("premiumTagLabel", () => {
  it("escreve o prêmio em pontos, com uma casa", () => {
    expect(premiumTagLabel(asset())).toBe("inclui 1,9 de prêmio");
    expect(premiumTagLabel(asset({ risk_premium: "0.0097" }))).toBe("inclui 1 de prêmio");
  });
});

describe("rateWithoutPremium", () => {
  it("tira o prêmio da taxa do título", () => {
    expect(rateWithoutPremium(asset())).toBe("IPCA + 4,38%");
  });
});

describe("premiumSinceStart", () => {
  it("sem fechamento, nada a comparar", () => {
    expect(premiumSinceStart(budget([], "0.019"))).toBeNull();
  });

  it("prêmio maior que o do início sobe", () => {
    expect(premiumSinceStart(budget([month("0.015")], "0.019"))).toEqual({
      text: "▲ 0,4 ponto desde jan/17",
      rising: true,
    });
  });

  it("prêmio menor desce e igual fica estável", () => {
    expect(premiumSinceStart(budget([month("0.021")], "0.019"))?.rising).toBe(false);
    expect(premiumSinceStart(budget([month("0.019")], "0.019"))?.text).toBe("estável desde jan/17");
  });
});

describe("signedPremium", () => {
  it("põe o sinal na frente", () => {
    expect(signedPremium("0.0187")).toBe("+1,87 ponto");
  });
});
