import { describe, expect, it } from "vitest";
import { fakeOrderPreview } from "./fake-order-preview";

describe("prévia do palco", () => {
  it("100 ações a R$ 38,12 custam R$ 3.812,00 e deixam R$ 96.188,00 no caixa", () => {
    // 100 × 38,12 = 3.812,00; 100.000,00 − 3.812,00 = 96.188,00
    const preview = fakeOrderPreview({ action: "buy", quantity: "100", limit_price: null });
    expect(preview.price).toBe("38.12");
    expect(preview.total).toBe("3812.00");
    expect(preview.cash_after).toBe("96188.00");
  });

  it("a ordem limitada usa o preço limite: 100 × R$ 37,50 = R$ 3.750,00", () => {
    const preview = fakeOrderPreview({ action: "buy", quantity: "100", limit_price: 37.5 });
    expect(preview.price).toBe("37.50");
    expect(preview.total).toBe("3750.00");
  });

  it("sem quantidade o total é zero e o caixa fica inteiro", () => {
    const preview = fakeOrderPreview({ action: "buy", quantity: "0", limit_price: null });
    expect(preview.total).toBe("0.00");
    expect(preview.cash_after).toBe("100000.00");
  });

  it("o máximo é quanto o caixa paga: 100.000 ÷ 38,12 = 2.623 ações", () => {
    expect(fakeOrderPreview({ action: "buy", quantity: "1" }).max_quantity).toBe("2623");
  });
});
