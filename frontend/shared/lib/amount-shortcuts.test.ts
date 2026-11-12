import { describe, expect, it } from "vitest";
import { moneyToBody } from "@/shared/lib/utils/money-field";
import { applyFixed, applyShare, clearedAmount, visibleMode } from "./amount-shortcuts";

describe("visibleMode", () => {
  it("sem Shift vale o modo salvo", () => {
    expect(visibleMode("money", false)).toBe("money");
    expect(visibleMode("percent", false)).toBe("percent");
  });

  it("com Shift seguro mostra o outro modo", () => {
    expect(visibleMode("money", true)).toBe("percent");
    expect(visibleMode("percent", true)).toBe("money");
  });
});

describe("applyFixed", () => {
  it("soma o atalho ao que já está no campo: 1 mil + 5 mil = 6 mil", () => {
    const result = applyFixed("R$ 1.000,00", 5000, undefined);
    expect(moneyToBody(result.text)).toBe("6000.00");
    expect(result.capped).toBe(false);
  });

  it("clicar duas vezes soma duas vezes", () => {
    const once = applyFixed("R$ 0,00", 5000, undefined).text;
    expect(moneyToBody(applyFixed(once, 5000, undefined).text)).toBe("10000.00");
  });

  it("para no máximo e avisa: campo em 1 mil, caixa de 8 mil, +10 mil dá 8 mil", () => {
    const result = applyFixed("R$ 1.000,00", 10000, 8000);
    expect(moneyToBody(result.text)).toBe("8000.00");
    expect(result.capped).toBe(true);
  });

  it("chegar exatamente no máximo não conta como limitado", () => {
    expect(applyFixed("R$ 3.000,00", 5000, 8000).capped).toBe(false);
  });

  it("o campo vazio conta como zero", () => {
    expect(moneyToBody(applyFixed("", 5000, 8000).text)).toBe("5000.00");
  });

  it("o máximo com centavos quebrados trunca: 8000,019 vira 8000,01", () => {
    expect(moneyToBody(applyFixed("R$ 0,00", 10000, 8000.019).text)).toBe("8000.01");
  });

  it("máximo zero trava o campo em zero", () => {
    const result = applyFixed("R$ 0,00", 1000, 0);
    expect(moneyToBody(result.text)).toBe("0.00");
    expect(result.capped).toBe(true);
  });
});

describe("applyShare", () => {
  it("75% de R$ 100.000 são R$ 75.000", () => {
    expect(moneyToBody(applyShare(100000, 0.75))).toBe("75000.00");
  });

  it("máximo zero dá R$ 0,00", () => {
    expect(moneyToBody(applyShare(0, 0.5))).toBe("0.00");
  });
});

describe("clearedAmount", () => {
  it("zera o campo", () => {
    expect(moneyToBody(clearedAmount())).toBe("0.00");
  });
});
