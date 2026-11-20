import { describe, expect, it } from "vitest";
import { splitRecent } from "./recent-split";

describe("splitRecent", () => {
  it("até 4 itens todos ficam no seletor", () => {
    const items = [2018, 2022, 2026, 2030];
    expect(splitRecent(items)).toEqual({ row: items, older: [] });
  });

  it("com 5 ou mais ficam os 3 mais recentes e o resto vai para o Anteriores", () => {
    const { row, older } = splitRecent([2014, 2018, 2022, 2026, 2030]);
    expect(row).toEqual([2022, 2026, 2030]);
    expect(older).toEqual([2014, 2018]);
  });

  it("uma lista vazia não tem nada à vista nem atrás do Anteriores", () => {
    expect(splitRecent([])).toEqual({ row: [], older: [] });
  });
});
