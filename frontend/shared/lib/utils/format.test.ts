import { describe, expect, it } from "vitest";
import { formatQuantityInput, quantityToInput } from "./format";

describe("formatQuantityInput", () => {
  it("ativo inteiro aceita só dígitos", () => {
    expect(formatQuantityInput("12,5", false)).toBe("125");
    expect(formatQuantityInput("abc7", false)).toBe("7");
  });

  it("cripto aceita uma vírgula e até oito casas", () => {
    expect(formatQuantityInput("0,123456789", true)).toBe("0,12345678");
    expect(formatQuantityInput("1,2,3", true)).toBe("1,23");
  });

  it("cripto troca o ponto pela vírgula", () => {
    expect(formatQuantityInput("0.5", true)).toBe("0,5");
  });
});

describe("quantityToInput", () => {
  it("trunca nas casas do ativo, sem arredondar para cima", () => {
    expect(quantityToInput("293.333333339", true)).toBe("293,33333333");
    expect(quantityToInput(7.9, false)).toBe("7");
  });

  it("devolve o máximo exato da string da API", () => {
    expect(quantityToInput("0.04400000", true)).toBe("0,044");
  });
});
