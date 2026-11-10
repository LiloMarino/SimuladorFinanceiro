import { describe, expect, it } from "vitest";

const MIN_TEXT_PX = 12;
// Classe arbitrária (text-[11px]) ou fontSize literal de gráfico (fontSize: 11, fontSize={11}, fontSize="11px")
const ARBITRARY_TEXT_SIZE = /text-\[(\d+(?:\.\d+)?)px\]|fontSize(?:[:=]\s*\{?\s*)["']?(\d+(?:\.\d+)?)(?:px)?["']?/g;

const sources = import.meta.glob("../../**/*.{ts,tsx}", { query: "?raw", import: "default", eager: true });

// Devolve os tamanhos de texto em px, escritos como classe arbitrária ou fontSize literal, que ficam abaixo do mínimo
const belowMinimum = (source: string) =>
  [...source.matchAll(ARBITRARY_TEXT_SIZE)]
    .filter((match) => Number(match[1] ?? match[2]) < MIN_TEXT_PX)
    .map((match) => match[0]);

describe("tamanho mínimo do texto", () => {
  it("reconhece a classe abaixo de 12 px", () => {
    expect(belowMinimum('<span className="text-[11px] font-mono">')).toEqual(["text-[11px]"]);
    expect(belowMinimum('<span className="text-[10.5px]">')).toEqual(["text-[10.5px]"]);
  });

  it("reconhece fontSize literal abaixo de 12", () => {
    expect(belowMinimum("const TICK = { fontSize: 10.5 };")).toEqual(["fontSize: 10.5"]);
    expect(belowMinimum("<text fontSize={11} />")).toEqual(["fontSize={11"]);
    expect(belowMinimum('<text fontSize="10px" />')).toEqual(['fontSize="10px"']);
  });

  it("aceita 12 px ou mais", () => {
    expect(belowMinimum('<span className="text-[12px] text-[13px] text-xs">')).toEqual([]);
    expect(belowMinimum("<text fontSize={CHART_FONT_SIZE} /> { fontSize: 12 }")).toEqual([]);
  });

  it("nenhum arquivo do front escreve texto abaixo de 12 px", () => {
    const offenders = Object.entries(sources)
      .filter(([path]) => !path.endsWith("min-text-size.test.ts"))
      .flatMap(([path, source]) => belowMinimum(source).map((found) => `${path}: ${found}`));
    expect(offenders).toEqual([]);
  });
});
