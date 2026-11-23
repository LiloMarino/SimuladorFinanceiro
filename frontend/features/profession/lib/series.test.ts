import { describe, expect, it } from "vitest";
import type { IncomeSeries } from "@/types";
import { todaySentence } from "./series";

const series = (overrides: Partial<IncomeSeries>): IncomeSeries => ({
  key: "GDP",
  current: "0.027",
  neutral: "0.02",
  points: [],
  guides: [{ value: "0", overtime: true }],
  effect: "0.007",
  effect_kind: "REAL_RAISE",
  changes: [],
  lever: false,
  ...overrides,
});

describe("todaySentence", () => {
  it("diz de que lado do ponto neutro o PIB está e libera a hora extra acima de zero", () => {
    expect(todaySentence(series({ current: "0.027" }))).toEqual({
      lead: "Acima do neutro de 2%:",
      text: "reajuste de +0,7% acima do IPCA. Acima de 0, hora extra liberada.",
    });
  });

  it("conta a chance de demissão em vezes a normal quando o desemprego está abaixo do neutro", () => {
    expect(
      todaySentence(
        series({
          key: "UNEMPLOYMENT",
          current: "0.07",
          neutral: "0.09",
          guides: [],
          effect: "0.6",
          effect_kind: "LAYOFF_FACTOR",
        }),
      ),
    ).toEqual({ lead: "Abaixo do neutro de 9%:", text: "chance de demissão em 0,6 vez a normal." });
  });

  it("abre com Hoje na alavanca do governo, que não tem ponto neutro", () => {
    const sentence = todaySentence(
      series({ key: "SERVANT_RAISE", neutral: null, guides: [], lever: true, current: "0.03", effect: "0.03" }),
    );
    expect(sentence?.lead).toBe("Hoje:");
  });

  it("não tem frase quando o indicador não tem efeito na renda", () => {
    expect(todaySentence(series({ effect: null }))).toBeNull();
  });
});
