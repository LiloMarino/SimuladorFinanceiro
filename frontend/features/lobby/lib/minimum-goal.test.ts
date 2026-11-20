import { describe, expect, it } from "vitest";
import {
  blockingHeirFloor,
  heirFloorMessage,
  maximumWithdrawalPercent,
  minimumExpense,
  minimumGoal,
  ruleGoal,
} from "./minimum-goal";

const heir = { nickname: "Herdeiro", isBot: true, capital: 1_580_000 };

describe("piso da meta", () => {
  const values = {
    gameType: "FINANCIAL_INDEPENDENCE" as const,
    salaryMode: "PROFESSIONS" as const,
    startingCash: "R$ 100.000,00",
    goalNetWorth: "R$ 1.000.000,00",
    monthlyExpense: "R$ 5.000,00",
    withdrawalRate: "5",
  };

  it("o capital do Herdeiro trava a meta que não passa dele", () => {
    // 12 × 5.000 ÷ 5% = 1.200.000, abaixo dos 1.580.000 do Herdeiro
    expect(blockingHeirFloor(heir, values)).toBe(1_580_000);
  });

  it("a meta acima do capital do Herdeiro não trava", () => {
    // 12 × 7.000 ÷ 5% = 1.680.000
    expect(blockingHeirFloor(heir, { ...values, monthlyExpense: "R$ 7.000,00" })).toBeNull();
  });

  it("sem Herdeiro, ou fora do modo de profissões, nada trava", () => {
    expect(blockingHeirFloor(null, values)).toBeNull();
    expect(blockingHeirFloor(heir, { ...values, salaryMode: "EQUAL" })).toBeNull();
  });

  it("com o saldo inicial acima do capital do Herdeiro o piso é o do saldo, que o formulário trata", () => {
    expect(blockingHeirFloor(heir, { ...values, startingCash: "R$ 2.000.000,00" })).toBeNull();
  });

  it("a meta mínima sobe os centavos para o real seguinte", () => {
    expect(minimumGoal(1_579_999.4)).toBe(1_580_000);
    expect(minimumGoal(1_580_000)).toBe(1_580_000);
  });

  it("o aviso diz o piso por causa do Herdeiro", () => {
    expect(heirFloorMessage(1_580_000)).toMatch(/^Meta mínima de R\$\s1\.580\.000 por causa do Herdeiro\.$/);
  });
});

describe("meta que o tipo de partida pede", () => {
  const values = { goalNetWorth: "R$ 1.000.000,00", monthlyExpense: "R$ 5.000,00", withdrawalRate: "5" };

  it("na corrida é a meta digitada", () => {
    expect(ruleGoal({ ...values, gameType: "GOAL_RACE" })).toBe(1_000_000);
  });

  it("no viver de renda é 12 × despesa ÷ taxa", () => {
    // 12 × 5.000 = 60.000 por ano; a 5%, 1.200.000
    expect(ruleGoal({ ...values, gameType: "FINANCIAL_INDEPENDENCE" })).toBeCloseTo(1_200_000, 6);
  });

  it("nos outros tipos não há meta", () => {
    expect(ruleGoal({ ...values, gameType: "CLASSIC" })).toBeNull();
  });
});

describe("sugestão para passar do piso", () => {
  it("a despesa sobe para o próximo múltiplo de R$ 100", () => {
    // 1.580.000 × 5% ÷ 12 = 6.583,33; o múltiplo de 100 acima é 6.600
    expect(minimumExpense(1_580_000, 0.05)).toBe(6600);
  });

  it("a despesa que dá exatamente o piso ainda não passa: sobe mais um degrau", () => {
    // 1.200.000 × 5% ÷ 12 = 5.000 e a meta de 5.000 é igual ao piso
    expect(minimumExpense(1_200_000, 0.05)).toBe(5100);
  });

  it("a taxa desce para a casa decimal abaixo", () => {
    // 12 × 5.000 ÷ 1.580.000 = 3,797%; a casa de 0,1 abaixo é 3,7
    expect(maximumWithdrawalPercent(1_580_000, 5000)).toBe(3.7);
  });

  it("a taxa que dá exatamente o piso ainda não passa: desce mais uma casa", () => {
    // 12 × 6.000 ÷ 1.800.000 = 4%; só 3,9% passa do piso
    expect(maximumWithdrawalPercent(1_800_000, 6000)).toBe(3.9);
  });

  it("sem taxa possível acima de 1% não há sugestão de taxa", () => {
    // 12 × 1.000 ÷ 1.580.000 = 0,76%: abaixo do mínimo de 1% do servidor
    expect(maximumWithdrawalPercent(1_580_000, 1000)).toBeNull();
  });
});
