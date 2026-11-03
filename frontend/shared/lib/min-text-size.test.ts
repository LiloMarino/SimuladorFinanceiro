import { describe, expect, it } from "vitest";

const MIN_TEXT_PX = 12;
const ARBITRARY_TEXT_SIZE = /text-\[(\d+(?:\.\d+)?)px\]/g;

const sources = import.meta.glob("../../**/*.{ts,tsx}", { query: "?raw", import: "default", eager: true });

// Devolve os tamanhos de texto em px, escritos como classe arbitrária, que ficam abaixo do mínimo
const belowMinimum = (source: string) =>
  [...source.matchAll(ARBITRARY_TEXT_SIZE)].filter((match) => Number(match[1]) < MIN_TEXT_PX).map((match) => match[0]);

describe("tamanho mínimo do texto", () => {
  it("reconhece a classe abaixo de 12 px", () => {
    expect(belowMinimum('<span className="text-[11px] font-mono">')).toEqual(["text-[11px]"]);
    expect(belowMinimum('<span className="text-[10.5px]">')).toEqual(["text-[10.5px]"]);
  });

  it("aceita 12 px ou mais", () => {
    expect(belowMinimum('<span className="text-[12px] text-[13px] text-xs">')).toEqual([]);
  });

  it("nenhum arquivo do front escreve texto abaixo de 12 px", () => {
    const offenders = Object.entries(sources)
      .filter(([path]) => !path.endsWith("min-text-size.test.ts"))
      .flatMap(([path, source]) => belowMinimum(source).map((found) => `${path}: ${found}`));
    expect(offenders).toEqual([]);
  });
});
