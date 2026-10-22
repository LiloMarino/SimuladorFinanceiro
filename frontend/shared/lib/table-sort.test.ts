import { describe, expect, it } from "vitest";
import { nextTableSort, sortNumber, sortTableRows } from "./table-sort";

const rows = [
  { name: "AÇÃO10", price: "100.00", date: "2026-10-22" },
  { name: "ação2", price: "9.90", date: "2025-12-31" },
  { name: "Banco", price: "20.50", date: "2026-01-01" },
];
const columns = { name: (r: typeof rows[number]) => r.name, price: (r: typeof rows[number]) => sortNumber(r.price),
  date: (r: typeof rows[number]) => r.date };

describe("ordenação das tabelas", () => {
  it("compara preços numéricos em ambos os sentidos sem alterar a resposta da API", () => {
    expect(sortTableRows(rows, columns, { column: "price", direction: "asc" }).map(r => r.price)).toEqual(["9.90", "20.50", "100.00"]);
    expect(sortTableRows(rows, columns, { column: "price", direction: "desc" }).map(r => r.price)).toEqual(["100.00", "20.50", "9.90"]);
    expect(rows[0].price).toBe("100.00");
  });
  it("mantém ausentes no fim e não confunde zero ou negativos com ausência", () => {
    const data = [{ v: null }, { v: 0 }, { v: -2 }, { v: NaN }, { v: 10 }];
    expect(sortTableRows(data, { value: r => r.v }, { column: "value", direction: "desc" }).map(r => r.v)).toEqual([10, 0, -2, null, NaN]);
    expect(sortNumber(null)).toBeNull();
    expect(sortNumber("0")).toBe(0);
  });
  it("ordena texto naturalmente e datas pelo valor original", () => {
    expect(sortTableRows(rows, columns, { column: "name", direction: "asc" }).map(r => r.name)).toEqual(["ação2", "AÇÃO10", "Banco"]);
    expect(sortTableRows(rows, columns, { column: "date", direction: "asc" }).map(r => r.date)).toEqual(["2025-12-31", "2026-01-01", "2026-10-22"]);
  });
  it("preserva empates e a ordem original quando nenhuma coluna foi escolhida", () => {
    const data = [{ id: "a", v: 1 }, { id: "b", v: 1 }];
    expect(sortTableRows(data, { v: r => r.v }, { column: "v", direction: "desc" })).toEqual(data);
    expect(sortTableRows(rows, columns, null)).toEqual(rows);
  });
  it("alterna a direção e começa outra coluna em ordem crescente", () => {
    const first = nextTableSort(null, "price");
    expect(first).toEqual({ column: "price", direction: "asc" });
    expect(nextTableSort(first, "price")).toEqual({ column: "price", direction: "desc" });
    expect(nextTableSort(first, "name")).toEqual({ column: "name", direction: "asc" });
  });
});
