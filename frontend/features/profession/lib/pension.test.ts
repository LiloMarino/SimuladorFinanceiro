import { describe, expect, it } from "vitest";
import { convertedIncome, monthsText, planTime, redeemSplit } from "./pension";

describe("planTime", () => {
  it("escreve anos e meses no singular e no plural", () => {
    expect(planTime(40)).toBe("3 anos e 4 meses");
    expect(planTime(12)).toBe("1 ano");
    expect(planTime(13)).toBe("1 ano e 1 mês");
    expect(planTime(5)).toBe("5 meses");
  });
});

describe("redeemSplit", () => {
  it("cobra o IR sobre o valor inteiro", () => {
    expect(redeemSplit(20000, "0.30")).toEqual({ tax: 6000, net: 14000 });
  });
});

describe("convertedIncome", () => {
  it("rende o valor vezes a fração mensal do juro real", () => {
    expect(convertedIncome(20000, "0.0065405")).toBe(130.81);
  });
});

describe("monthsText", () => {
  it("concorda no singular", () => {
    expect(monthsText(1)).toBe("1 mês");
    expect(monthsText(8)).toBe("8 meses");
  });
});
