import { describe, expect, it } from "vitest";
import { crossovers, type SeriesPoint } from "./crossovers";

const series = (...values: number[]): SeriesPoint[] =>
  values.map((value, index) => ({ date: `2024-01-${String(index + 1).padStart(2, "0")}`, value }));

describe("crossovers", () => {
  it("acha o dia em que a linha passa para cima da outra", () => {
    expect(crossovers(series(1, 2, 4, 5), series(3, 3, 3, 3))).toEqual([{ date: "2024-01-03", direction: "up" }]);
  });

  it("acha o dia em que a linha passa para baixo da outra", () => {
    expect(crossovers(series(5, 4, 2), series(3, 3, 3))).toEqual([{ date: "2024-01-03", direction: "down" }]);
  });

  it("não conta o toque que volta para o mesmo lado", () => {
    expect(crossovers(series(1, 3, 1), series(3, 3, 3))).toEqual([]);
  });

  it("conta o empate seguido de virada como um cruzamento só", () => {
    expect(crossovers(series(1, 3, 5), series(3, 3, 3))).toEqual([{ date: "2024-01-03", direction: "up" }]);
  });

  it("ignora os dias que só uma das séries tem", () => {
    const a = series(1, 2, 5);
    const b = series(9, 3, 3).slice(1);
    expect(crossovers(a, b)).toEqual([{ date: "2024-01-03", direction: "up" }]);
  });

  it("devolve vazio sem pontos", () => {
    expect(crossovers([], series(1, 2))).toEqual([]);
  });
});
