import { describe, expect, it } from "vitest";
import { isAtLimit, matchesQuery, shouldShowSearch, splitUnavailable } from "@/shared/lib/option-select";

describe("shouldShowSearch", () => {
  it("aparece a partir de 8 opções", () => {
    expect(shouldShowSearch(7)).toBe(false);
    expect(shouldShowSearch(8)).toBe(true);
  });

  it("o valor forçado vale sobre a contagem", () => {
    expect(shouldShowSearch(3, true)).toBe(true);
    expect(shouldShowSearch(40, false)).toBe(false);
  });
});

describe("splitUnavailable", () => {
  it("manda para o fim só a opção bloqueada com motivo", () => {
    const options = [
      { id: "a" },
      { id: "b", disabled: true, reason: "Já escolhida" },
      { id: "c", disabled: true },
      { id: "d" },
    ];
    const { available, unavailable } = splitUnavailable(options);
    expect(available.map((option) => option.id)).toEqual(["a", "c", "d"]);
    expect(unavailable.map((option) => option.id)).toEqual(["b"]);
  });
});

describe("matchesQuery", () => {
  const option = { label: "PETR4", description: "Petróleo Brasileiro", searchText: "PETR4 Petrobras" };

  it("busca por código, nome e descrição sem ligar para acento ou caixa", () => {
    expect(matchesQuery(option, "petr")).toBe(true);
    expect(matchesQuery(option, "PETROLEO")).toBe(true);
    expect(matchesQuery(option, "brasileiro")).toBe(true);
    expect(matchesQuery(option, "vale")).toBe(false);
  });

  it("consulta vazia mostra tudo", () => {
    expect(matchesQuery(option, "  ")).toBe(true);
  });
});

describe("isAtLimit", () => {
  it("só trava quando há teto e ele foi atingido", () => {
    expect(isAtLimit(["A", "B"], 2)).toBe(true);
    expect(isAtLimit(["A"], 2)).toBe(false);
    expect(isAtLimit(["A", "B"], null)).toBe(false);
  });
});
