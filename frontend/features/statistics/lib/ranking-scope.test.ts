import { describe, expect, it } from "vitest";
import { visibleRankingRows } from "./ranking-scope";

const rows = [
  { name: "Ana", is_bot: false },
  { name: "Média Móvel", is_bot: true },
  { name: "Beto", is_bot: false },
];

describe("visibleRankingRows", () => {
  it("mantém todos por padrão", () => {
    expect(visibleRankingRows(rows, false)).toHaveLength(3);
  });

  it("tira os bots em 'Só pessoas', na mesma ordem", () => {
    expect(visibleRankingRows(rows, true).map((row) => row.name)).toEqual(["Ana", "Beto"]);
  });
});
