import { describe, expect, it } from "vitest";
import type { CandlePattern } from "@/types";
import { crossoverShapes, patternMarkers, patternShapes, type AnnotationColors } from "./chart-annotations";

const colors: AnnotationColors = { up: "g", down: "r", neutral: "n", band: "b" };
const phrases = { up: "sobe", down: "desce" };

const pattern = (end: string, direction: CandlePattern["direction"], start = end): CandlePattern => ({
  code: direction === "up" ? "hammer" : direction === "down" ? "shooting_star" : "doji",
  start,
  end,
  direction,
  change_5d: null,
  hit: null,
});

const days = ["01", "02", "03", "04", "05", "06", "07", "08"].map((d) => `2024-01-${d}`);
const line = (...values: number[]) => values.map((value, index) => ({ date: days[index]!, value }));

describe("chart annotations", () => {
  it("põe o rótulo verde embaixo, o vermelho em cima e o cinza no doji", () => {
    const markers = patternMarkers(
      [pattern(days[0]!, "up"), pattern(days[1]!, "down"), pattern(days[2]!, "neutral")],
      colors,
    );
    expect(markers.map((m) => [m.position, m.color, m.text])).toEqual([
      ["belowBar", "g", "Martelo"],
      ["aboveBar", "r", "Estrela cadente"],
      ["aboveBar", "n", "Doji"],
    ]);
  });

  it("faixa só nos padrões de várias velas e contorno dos 5 pregões do padrão em foco", () => {
    const multi = pattern(days[1]!, "up", days[0]);
    const single = pattern(days[2]!, "up");
    const shapes = patternShapes([multi, single], single, days, colors);
    expect(shapes).toEqual([
      { kind: "band", from: days[0]!, to: days[1]!, color: "b" },
      { kind: "outline", from: days[3]!, to: days[7]!, color: "g" },
    ]);
  });

  it("contorna só os pregões que existem depois do padrão", () => {
    const last = pattern(days[7]!, "up");
    expect(patternShapes([last], last, days, colors)).toEqual([]);
  });

  it("círculo em cada cruzamento e a frase só no último", () => {
    const shapes = crossoverShapes(line(1, 3, 1, 3), line(2, 2, 2, 2), null, phrases, colors);
    expect(shapes.map((s) => s.kind)).toEqual(["circle", "circle", "circle", "note"]);
    expect(shapes.at(-1)).toMatchObject({ kind: "note", text: "sobe", time: days[3]! });
  });

  it("ignora os cruzamentos de antes do período", () => {
    const shapes = crossoverShapes(line(1, 3, 1, 3), line(2, 2, 2, 2), days[3]!, phrases, colors);
    expect(shapes.map((s) => s.kind)).toEqual(["circle", "note"]);
  });
});
