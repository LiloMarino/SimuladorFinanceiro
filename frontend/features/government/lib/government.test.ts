import { describe, expect, it } from "vitest";
import type { GovernmentMeasure } from "@/types";
import {
  approvalArrow,
  approvalTone,
  daysUntil,
  generalToday,
  holdingLabel,
  impactSentence,
  lowStreakLabel,
  nextStep,
  percentLabel,
  rateToFraction,
  sectorEffect,
  signedPoints,
} from "./government";

const measure = (partial: Partial<GovernmentMeasure>) =>
  ({ id: 1, status: "QUEUED", vote_date: "2020-03-31", effective: null, chance: null, ...partial }) as GovernmentMeasure;

describe("percentLabel", () => {
  it("escreve só as casas que fazem falta", () => {
    expect(percentLabel("0.225")).toBe("22,5%");
    expect(percentLabel("0.15")).toBe("15%");
  });
});

describe("signedPoints", () => {
  it("usa o menos tipográfico e o mais explícito", () => {
    expect(signedPoints(4)).toBe("+4");
    expect(signedPoints(-1)).toBe("−1");
    expect(signedPoints(0)).toBe("0");
  });
});

describe("rateToFraction", () => {
  it("converte o percentual digitado na fração da API", () => {
    expect(rateToFraction("22,5")).toBe("0.225");
    expect(rateToFraction("15")).toBe("0.15");
    expect(rateToFraction("")).toBeNull();
  });
});

describe("generalToday", () => {
  it("mostra a tabela da renda fixa do topo ao piso", () => {
    expect(generalToday("FIXED_INCOME_TABLE", "0.15", "0.225")).toBe("22,5% → 15%");
  });

  it("mostra a tabela única como uma alíquota só", () => {
    expect(generalToday("FIXED_INCOME_TABLE", "0.15", "0.15")).toBe("15%");
  });

  it("chama de isentas as LCI e LCA sem imposto", () => {
    expect(generalToday("LCI_LCA_RATE", "0", null)).toBe("Isentas");
  });
});

describe("daysUntil", () => {
  it("conta os dias corridos e não passa de zero", () => {
    // De 14 mar a 29 mai: 17 + 30 + 29 = 76 dias
    expect(daysUntil("2020-03-14", "2020-05-29")).toBe(76);
    expect(daysUntil("2020-06-01", "2020-05-29")).toBe(0);
  });
});

describe("nextStep", () => {
  it("diz quando o Congresso vota a medida na fila", () => {
    expect(nextStep(measure({}), "2020-03-14")).toBe("Congresso vota em 31 mar");
  });

  it("conta os dias que faltam para a medida aprovada valer", () => {
    expect(nextStep(measure({ status: "APPROVED", effective: "2020-05-29" }), "2020-03-14")).toBe(
      "Vale em 29 mai · faltam 76 dias",
    );
  });

  it("lembra a chance que a rejeitada tinha", () => {
    expect(nextStep(measure({ status: "REJECTED", chance: 59 }), "2020-03-14")).toBe("Tinha 59% de chance");
  });
});

describe("sectorEffect", () => {
  it("mostra a alíquota atual e a nova enquanto a medida espera", () => {
    const taxed = measure({ kind: "SECTOR_TAX", value: "0.05", effective: "2020-05-29" });
    expect(sectorEffect(taxed, "0.15", "2020-03-14")).toBe("15% → 20% em 29 mai");
  });

  it("mostra só a alíquota nova depois que vale", () => {
    const taxed = measure({ kind: "SECTOR_TAX", value: "0.05", effective: "2020-05-29" });
    expect(sectorEffect(taxed, "0.15", "2020-06-01")).toBe("IR 20%");
  });

  it("escreve a isenção do setor", () => {
    expect(sectorEffect(measure({ kind: "SECTOR_EXEMPT" }), "0.15", "2020-03-14")).toBe("IR 0% (isento)");
  });
});

describe("aprovação", () => {
  it("fica crítica abaixo do piso e em atenção abaixo de 50", () => {
    expect(approvalTone({ value: 22, floor: 25 })).toBe("destructive");
    expect(approvalTone({ value: 40, floor: 25 })).toBe("warning");
    expect(approvalTone({ value: 56, floor: 25 })).toBe("success");
  });

  it("aponta a seta pela variação desde o mês anterior", () => {
    expect(approvalArrow({ value: 56, previous: 50 })).toBe("▲");
    expect(approvalArrow({ value: 40, previous: 50 })).toBe("▼");
    expect(approvalArrow({ value: 50, previous: 50 })).toBe("");
    expect(approvalArrow({ value: 50, previous: null })).toBe("");
  });

  it("conta os meses abaixo do piso no plural certo", () => {
    expect(lowStreakLabel({ low_streak: 1, floor: 25 })).toBe("1 mês abaixo de 25%");
    expect(lowStreakLabel({ low_streak: 2, floor: 25 })).toBe("2 meses seguidos abaixo de 25%");
  });
});

describe("holdingLabel", () => {
  it("mostra o próprio jogador em % e os outros em reais", () => {
    expect(holdingLabel({ nickname: "Bia", share: "0.21", value: "100000" }, "Bia")).toBe("você 21%");
    expect(holdingLabel({ nickname: "Lilo", share: "0.1", value: "40000" }, "Bia")).toBe("Lilo R$ 40,0 mil");
  });
});

describe("impactSentence", () => {
  it("conta o bônus do corte no singular e no plural", () => {
    expect(impactSentence({ ruler_band: 2, impact: 2 })).toBe(
      "Fica na faixa 2 da régua e, como corte de imposto, soma 2 pontos à aprovação quando passa a valer.",
    );
    expect(impactSentence({ ruler_band: 1, impact: 1 })).toContain("soma 1 ponto à");
  });

  it("conta a perda do imposto novo e avisa que some", () => {
    expect(impactSentence({ ruler_band: 5, impact: -3 })).toBe(
      "Fica na faixa 5 da régua e, como imposto novo, tira 3 pontos da aprovação quando passa a valer, efeito que some em 6 meses.",
    );
  });
});
