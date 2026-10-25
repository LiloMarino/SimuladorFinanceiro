import { describe, expect, it } from "vitest";
import {
  calculatedGoal,
  isPositiveMoney,
  isWithdrawalRate,
  withdrawalRateFraction,
  withdrawalRateToBody,
} from "./life-rules";

describe("taxa de retirada", () => {
  it("aceita de 1% a 10% ao ano, limites incluídos", () => {
    expect(isWithdrawalRate(0.01)).toBe(true);
    expect(isWithdrawalRate(0.1)).toBe(true);
    expect(isWithdrawalRate(0.0099)).toBe(false);
    expect(isWithdrawalRate(0.101)).toBe(false);
  });

  it("o campo guarda o percentual e o corpo da API a fração com quatro casas", () => {
    expect(withdrawalRateFraction("8,5")).toBeCloseTo(0.085, 12);
    expect(withdrawalRateToBody("4")).toBe("0.0400");
    expect(withdrawalRateToBody("8,5")).toBe("0.0850");
  });
});

describe("meta calculada do viver de renda", () => {
  it("sai da despesa mensal e da taxa", () => {
    // 12 × 5.000 ÷ 0,04
    expect(calculatedGoal("R$ 5.000,00", "4")).toBeCloseTo(1_500_000, 6);
  });

  it("é nula com despesa zero ou taxa fora da faixa", () => {
    expect(isPositiveMoney("R$ 0,00")).toBe(false);
    expect(calculatedGoal("R$ 0,00", "4")).toBeNull();
    expect(calculatedGoal("R$ 5.000,00", "11")).toBeNull();
  });
});
