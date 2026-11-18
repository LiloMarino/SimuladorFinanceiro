import { describe, expect, it } from "vitest";
import { holdingAfterBuy, holdingAfterSell, premiumPaid, quotaOrderOutlook } from "./fund-quota-order";

describe("ágio pago", () => {
  it("é quantidade × (preço − patrimônio por cota)", () => {
    // 100 × (141,60 − 128,40) = 1.320
    expect(premiumPaid(100, 141.6, 128.4)).toBeCloseTo(1320, 6);
  });
});

describe("cotas depois da ordem", () => {
  it("compra com emissão aumenta o total", () => {
    // 1.000 + 500 = 1.500 de 10.000 + 500 = 10.500 → 14,29%
    const after = holdingAfterBuy(1000, 10_000, 500, true);
    expect(after.quotas).toBe(1500);
    expect(after.share).toBeCloseTo(1500 / 10_500, 6);
  });

  it("compra no mercado só muda de dono", () => {
    // 1.500 de 10.000 = 15%
    expect(holdingAfterBuy(1000, 10_000, 500, false).share).toBeCloseTo(0.15, 6);
  });

  it("venda reduz a parte sem mexer no total", () => {
    // 5.800 − 799 = 5.001 de 10.000
    const after = holdingAfterSell(5800, 10_000, 799);
    expect(after.quotas).toBe(5001);
    expect(after.share).toBeCloseTo(0.5001, 6);
  });
});

describe("quotaOrderOutlook", () => {
  const base = { mine: 5800, total: 10_000, nav: 128.4, price: 141.6, quantity: 100, issued: false, manager: false };

  it("a compra acima do patrimônio por cota paga ágio", () => {
    // ágio pago: 100 × (141,60 − 128,40) = 1.320; taxa: 141,60 ÷ 128,40 − 1 = 10,28%
    const outlook = quotaOrderOutlook({ ...base, action: "buy" });
    expect(outlook.premiumPaid).toBeCloseTo(1320, 6);
    expect(outlook.premiumRate).toBeCloseTo(0.1028, 4);
  });

  it("a venda não paga ágio", () => {
    expect(quotaOrderOutlook({ ...base, action: "sell" }).premiumPaid).toBeNull();
  });

  it("o gestor que vende além do mínimo de controle perde o controle", () => {
    // Mínimo 5.001; vender 800 deixa 5.000 (50%): abaixo do controle
    const outlook = quotaOrderOutlook({ ...base, action: "sell", manager: true, quantity: 800 });
    expect(outlook.losesControl).toBe(true);
    expect(outlook.after.quotas).toBe(5000);
  });

  it("o botão Vender só N leva o gestor até o mínimo de controle", () => {
    // 5.800 − 5.001 = 799 cotas vendáveis, e vender 799 mantém o controle
    const outlook = quotaOrderOutlook({ ...base, action: "sell", manager: true, quantity: 800 });
    expect(outlook.sellable).toBe(799);
    expect(quotaOrderOutlook({ ...base, action: "sell", manager: true, quantity: 799 }).losesControl).toBe(false);
  });

  it("quem não é o gestor principal não tem controle a perder", () => {
    expect(quotaOrderOutlook({ ...base, action: "sell", manager: false, quantity: 800 }).losesControl).toBe(false);
  });
});
