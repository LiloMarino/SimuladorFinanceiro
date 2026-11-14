import { describe, expect, it } from "vitest";
import { movementText } from "./fund-movements";

describe("movementText", () => {
  it("a integralização diz o valor levado e as cotas recebidas", () => {
    const text = movementText({
      day: "2024-01-02",
      type: "contribution",
      quotas: "1600",
      price: null,
      amount: "160000",
      ticker: null,
    });
    expect(text).toContain("1.600 cotas");
    expect(text).toContain("160.000,00");
  });

  it("o relatório mensal não traz número", () => {
    expect(
      movementText({
        day: "2024-02-01",
        type: "report_published",
        quotas: null,
        price: null,
        amount: null,
        ticker: null,
      }),
    ).toBe("Relatório mensal publicado");
  });

  it("a compra do gestor cita o ativo", () => {
    expect(
      movementText({
        day: "2024-02-01",
        type: "manager_buy",
        quotas: "100",
        price: null,
        amount: null,
        ticker: "PETR4",
      }),
    ).toBe("O gestor comprou 100 de PETR4");
  });
});
