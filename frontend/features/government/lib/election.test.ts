import { describe, expect, it } from "vitest";
import { countdownLabel, monthlyYield, phaseLabel, promiseBand, remainingCollections, rulerPosition } from "./election";

describe("rulerPosition", () => {
  it("põe o marcador no meio da faixa: cada uma das 5 ocupa 20% da régua", () => {
    // faixa 1 vai de 0% a 20%, o meio é 10%; faixa 3 fica no centro; faixa 5 termina em 100%, o meio é 90%
    expect(rulerPosition(1)).toBeCloseTo(10, 6);
    expect(rulerPosition(3)).toBeCloseTo(50, 6);
    expect(rulerPosition(5)).toBeCloseTo(90, 6);
  });
});

describe("promiseBand", () => {
  it("nomeia a faixa e segura valores fora da régua nas pontas", () => {
    expect(promiseBand(2).title).toBe("Impostos baixos");
    expect(promiseBand(9).value).toBe(5);
    expect(promiseBand(0).value).toBe(1);
  });
});

describe("monthlyYield", () => {
  it("é a raiz do gasto mensal dividida por 64", () => {
    // √10.000 = 100; 100 / 64 = 1,5625 pontos
    expect(monthlyYield(10_000)).toBeCloseTo(1.5625, 6);
  });

  it("dobrar a verba rende menos que o dobro", () => {
    // √16.000 / √8.000 = √2 ≈ 1,414
    expect(monthlyYield(16_000) / monthlyYield(8_000)).toBeCloseTo(Math.SQRT2, 6);
  });

  it("não rende com verba zero ou negativa", () => {
    expect(monthlyYield(0)).toBe(0);
    expect(monthlyYield(-5)).toBe(0);
  });
});

describe("countdownLabel", () => {
  it("conta meses cheios e os dias que sobram", () => {
    // 14 mar → 14 set são 6 meses cheios; mais 9 dias chega a 23 set
    expect(countdownLabel("2018-03-14", "2018-09-23")).toBe("6 meses e 9 dias");
  });

  it("usa o singular e omite a parte zerada", () => {
    expect(countdownLabel("2018-03-14", "2018-04-14")).toBe("1 mês");
    expect(countdownLabel("2018-03-14", "2018-03-15")).toBe("1 dia");
  });

  it("vira hoje quando a data já chegou", () => {
    expect(countdownLabel("2018-10-07", "2018-10-07")).toBe("hoje");
  });
});

describe("remainingCollections", () => {
  it("conta os dias 1º depois de hoje até o 1º turno", () => {
    // 1º de abr a 1º de out de 2018: abr, mai, jun, jul, ago, set e out = 7
    expect(remainingCollections("2018-03-14", "2018-10-07")).toBe(7);
  });

  it("não conta o 1º do mês corrente", () => {
    expect(remainingCollections("2018-10-01", "2018-10-07")).toBe(0);
  });
});

describe("phaseLabel", () => {
  it("dá um nome a cada fase", () => {
    expect(phaseLabel("CAMPAIGN")).toBe("Campanha aberta");
  });
});
