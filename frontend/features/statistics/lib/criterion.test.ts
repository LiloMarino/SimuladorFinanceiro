import { describe, expect, it } from "vitest";
import {
  criterionLabel,
  displayCriterionContribution,
  displayCriterionGap,
  displayCriterionValue,
  displayRemainingToGoal,
  rankingMeasure,
} from "./criterion";

describe("critério do ranking", () => {
  it("a partida clássica usa o critério escolhido; as outras, a meta", () => {
    expect(rankingMeasure({ game_type: "CLASSIC", criterion: "SHARPE" })).toBe("SHARPE");
    expect(rankingMeasure({ game_type: "GOAL_RACE", criterion: "SHARPE" })).toBe("GOAL");
  });

  it("nomeia o critério, com o valor da meta quando há", () => {
    expect(criterionLabel({ game_type: "CLASSIC", criterion: "RETURN", goal_net_worth: null })).toBe("Rentabilidade");
    expect(criterionLabel({ game_type: "GOAL_RACE", criterion: "SCORE", goal_net_worth: "1500000" })).toBe(
      "Primeiro a chegar à meta (R$ 1,5 mi)",
    );
    expect(criterionLabel({ game_type: "FINANCIAL_INDEPENDENCE", criterion: "SCORE", goal_net_worth: null })).toBe(
      "Primeiro a chegar à independência financeira",
    );
  });
});

describe("distância para o líder", () => {
  it("o líder e quem não tem valor", () => {
    expect(displayCriterionGap("SCORE", "0")).toBe("líder");
    expect(displayCriterionGap("SCORE", null)).toBe("—");
  });

  it("cada critério na sua unidade", () => {
    expect(displayCriterionGap("SCORE", "12.4")).toBe("12 pts");
    expect(displayCriterionGap("RETURN", "0.0123")).toBe("1,23 p.p.");
    expect(displayCriterionGap("NETWORTH", "2500")).toBe("R$ 2.500,00");
    expect(displayCriterionGap("SHARPE", "0.456")).toBe("0,46");
  });

  it("na meta vira dinheiro quando se sabe a meta", () => {
    // 25% de uma meta de 200.000
    expect(displayCriterionGap("GOAL", "0.25", "200000")).toBe("R$ 50.000,00");
    expect(displayCriterionGap("GOAL", "0.25", null)).toBe("25,00 p.p. da meta");
  });
});

describe("valor no critério", () => {
  it("cada critério na sua unidade", () => {
    expect(displayCriterionValue("GOAL", "0.5")).toBe("50%");
    expect(displayCriterionValue("SCORE", "71.6")).toBe("72 pts");
    expect(displayCriterionValue("RETURN", "0.0141")).toBe("+1,41%");
    expect(displayCriterionValue("NETWORTH", "1000")).toBe("R$ 1.000,00");
    expect(displayCriterionValue("SHARPE", "1.234")).toBe("Sharpe 1,23");
  });

  it("sem valor", () => {
    expect(displayCriterionValue("SCORE", null)).toBe("sem nota");
    expect(displayCriterionValue("RETURN", undefined)).toBe("—");
    expect(displayCriterionValue("SHARPE", null)).toBe("Sharpe —");
  });
});

describe("contribuição para o critério", () => {
  it("mostra o sinal com o menos tipográfico", () => {
    expect(displayCriterionContribution("RETURN", "-0.015")).toBe("−1,50 p.p.");
    expect(displayCriterionContribution("SCORE", "3")).toBe("+3");
    expect(displayCriterionContribution("NETWORTH", "-2500")).toBe("−R$ 2.500,00");
  });

  it("zero vai sem sinal, e sem valor vira traço", () => {
    expect(displayCriterionContribution("RETURN", "0")).toBe("0,00 p.p.");
    expect(displayCriterionContribution("SCORE", null)).toBe("—");
  });
});

describe("quanto falta para a meta", () => {
  it("é a parte que falta da meta, nunca negativa", () => {
    expect(displayRemainingToGoal("0.75", "100000")).toBe("R$ 25.000,00");
    expect(displayRemainingToGoal("1.2", "100000")).toBe("R$ 0,00");
  });

  it("sem fração ou sem meta vira traço", () => {
    expect(displayRemainingToGoal(null, "100000")).toBe("—");
    expect(displayRemainingToGoal("0.5", null)).toBe("—");
  });
});
