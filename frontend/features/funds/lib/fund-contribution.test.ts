import { describe, expect, it } from "vitest";
import { cashOf, contributionBody, contributionReady, pickedQuantity, picksValue } from "./fund-contribution";

const petr = { ticker: "PETR4", size: "300", reserved: "50", current_price: "30.00" } as never;
const vale = { ticker: "VALE3", size: "100", reserved: "0", current_price: "60.00" } as never;

describe("integralização", () => {
  it("lê o caixa digitado em reais", () => {
    expect(cashOf("R$ 1.234,56")).toBeCloseTo(1234.56, 6);
    expect(cashOf("")).toBe(0);
  });

  it("a quantidade vale até o que está livre (tamanho menos reservado)", () => {
    // 300 − 50 = 250 livres
    expect(pickedQuantity("250", petr)).toBe(250);
    expect(pickedQuantity("251", petr)).toBe(0);
    expect(pickedQuantity("0", petr)).toBe(0);
    expect(pickedQuantity("1,5", petr)).toBe(0);
  });

  it("soma o valor de mercado das ações marcadas", () => {
    // 100 × 30 + 10 × 60 = 3.600
    expect(picksValue({ PETR4: "100", VALE3: "10" }, [petr, vale])).toBe(3600);
  });

  it("pede algo levado e quantidades válidas", () => {
    expect(contributionReady("", {}, [petr], 1000)).toBe(false);
    expect(contributionReady("R$ 500,00", {}, [petr], 1000)).toBe(true);
    expect(contributionReady("R$ 1.500,00", {}, [petr], 1000)).toBe(false);
    expect(contributionReady("", { PETR4: "" }, [petr], 1000)).toBe(false);
    expect(contributionReady("", { PETR4: "10" }, [petr], 1000)).toBe(true);
  });

  it("monta o corpo com caixa e ações", () => {
    expect(contributionBody("R$ 500,00", { PETR4: "10" })).toEqual({
      cash: "500.00",
      stocks: [{ ticker: "PETR4", quantity: 10 }],
    });
    expect(contributionBody("", {}).cash).toBe("0.00");
  });
});
