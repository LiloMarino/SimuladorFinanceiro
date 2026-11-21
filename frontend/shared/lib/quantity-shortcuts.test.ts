import { describe, expect, it } from "vitest";
import { QUANTITY_SHARES, quantityOfShare, shareLabel } from "./quantity-shortcuts";

describe("quantityOfShare", () => {
  it("o total devolve o limite inteiro: 1.120 cotas vira 1120", () => {
    expect(quantityOfShare("1120", 1, false)).toBe("1120");
  });

  it("a fração trunca na unidade quando o ativo é inteiro: 25% de 1.001 é 250", () => {
    expect(quantityOfShare(1001, 0.25, false)).toBe("250");
  });

  it("a fração mantém as casas do ativo fracionável: 50% de 0,5 é 0,25", () => {
    expect(quantityOfShare("0.5", 0.5, true)).toBe("0,25");
  });

  it("limite zero preenche zero", () => {
    expect(quantityOfShare(0, 0.5, false)).toBe("0");
  });
});

describe("shareLabel", () => {
  it("frações em porcentagem e o total pelo nome dado", () => {
    expect(QUANTITY_SHARES.map((share) => shareLabel(share, "Máx"))).toEqual(["25%", "50%", "Máx"]);
    expect(shareLabel(1, "Tudo")).toBe("Tudo");
  });
});
