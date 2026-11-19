import { describe, expect, it } from "vitest";
import { MAX_COMANAGERS, maxSharePoints } from "./fund-comanager-shares";

describe("partes dos co-gestores", () => {
  it("a gestora aceita até 3 co-gestores", () => {
    expect(MAX_COMANAGERS).toBe(3);
  });

  it("a régua deixa ao menos 1 ponto para o principal", () => {
    expect(maxSharePoints(0)).toBe(99);
    expect(maxSharePoints(35)).toBe(64);
    expect(maxSharePoints(99)).toBe(0);
    expect(maxSharePoints(100)).toBe(0);
  });
});
