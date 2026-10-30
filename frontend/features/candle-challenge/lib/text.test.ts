import { describe, expect, it } from "vitest";
import { displayPeriod, ordinal, pointsText, verdictText } from "./text";

describe("período da revelação", () => {
  it("escreve o mês quando começa e termina nele", () => {
    expect(displayPeriod("2015-03-02", "2015-03-30")).toBe("março de 2015");
  });

  it("junta os meses do mesmo ano", () => {
    expect(displayPeriod("2015-02-10", "2015-03-30")).toBe("fevereiro a março de 2015");
  });

  it("escreve os dois anos quando viram", () => {
    expect(displayPeriod("2014-12-10", "2015-01-20")).toBe("dezembro de 2014 a janeiro de 2015");
  });
});

describe("textos do placar", () => {
  it("conta o ordinal e o plural", () => {
    expect(ordinal(2)).toBe("2º");
    expect(pointsText(1)).toBe("1 acerto");
    expect(pointsText(8)).toBe("8 acertos");
  });

  it("diz o que o jogador respondeu", () => {
    expect(verdictText("up", "hit")).toBe("Você disse que sobe: acertou.");
    expect(verdictText("down", "miss")).toBe("Você disse que desce: errou.");
    expect(verdictText(undefined, "none")).toBe("Você não respondeu a tempo.");
  });
});
