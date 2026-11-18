import { describe, expect, it } from "vitest";
import { distributedOf, rateToBody, rateToPoints } from "./fund-distribution";

describe("rendimentos da gestora", () => {
  it("converte a fração do servidor em pontos da régua e de volta", () => {
    expect(rateToPoints("0.9500")).toBe(95);
    expect(rateToPoints("0.0000")).toBe(0);
    expect(rateToBody(95)).toBe("0.9500");
    expect(rateToBody(100)).toBe("1.0000");
  });

  it("a parte distribuída incide só sobre lucro positivo", () => {
    expect(distributedOf(10_000, 95)).toBeCloseTo(9_500, 6);
    expect(distributedOf(-500, 95)).toBe(0);
    expect(distributedOf(10_000, 0)).toBe(0);
  });
});
