import { describe, expect, it } from "vitest";
import { displayPeriod, finalBand, ordinal, pointsText, verdictText } from "./text";

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

describe("faixa do fim da rodada", () => {
  it("de 0 a 3 acertos avisa que o gráfico é traiçoeiro, sem comemorar", () => {
    for (const hits of [0, 3]) {
      expect(finalBand(hits)).toEqual({ title: "Gráfico é traiçoeiro: veja as respostas", celebrate: false });
    }
  });

  it("de 4 a 7 acertos fica na média, sem comemorar", () => {
    for (const hits of [4, 7]) expect(finalBand(hits)).toEqual({ title: "Na média", celebrate: false });
  });

  it("de 8 a 10 acertos é leitura afiada e só aí comemora", () => {
    for (const hits of [8, 10]) expect(finalBand(hits)).toEqual({ title: "Leitura afiada", celebrate: true });
  });
});
