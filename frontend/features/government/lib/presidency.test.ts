import { describe, expect, it } from "vitest";
import { salariesLabel } from "./presidency";

describe("salariesLabel", () => {
  it("usa o singular só para um salário exato", () => {
    expect(salariesLabel("1.00")).toBe("1 salário");
    expect(salariesLabel("2.00")).toBe("2 salários");
    expect(salariesLabel("0.50")).toBe("0,5 salários");
  });

  it("escreve a vírgula e corta os zeros à direita", () => {
    expect(salariesLabel("2.35")).toBe("2,35 salários");
    expect(salariesLabel("48.000")).toBe("48 salários");
  });

  it("escreve zero no plural", () => {
    expect(salariesLabel("0")).toBe("0 salários");
  });
});
