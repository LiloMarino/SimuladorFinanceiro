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
  it("a emissão aberta diz as cotas e o preço fixo", () => {
    const text = movementText({
      day: "2024-03-04",
      type: "issuance_opened",
      quotas: "800",
      price: "125",
      amount: null,
      ticker: null,
    });
    expect(text).toContain("800 cotas");
    expect(text).toContain("125,00");
  });

  it("a emissão encerrada diz o que vendeu e o que entrou", () => {
    const text = movementText({
      day: "2024-03-22",
      type: "issuance_closed",
      quotas: "530",
      price: "125",
      amount: "66250",
      ticker: null,
    });
    expect(text).toContain("530 cotas vendidas");
    expect(text).toContain("66.250,00");
  });

  it("a recompra aberta diz a quantidade e o preço máximo", () => {
    const text = movementText({
      day: "2024-04-01",
      type: "buyback_opened",
      quotas: "300",
      price: "118",
      amount: null,
      ticker: null,
    });
    expect(text).toContain("300 cotas");
    expect(text).toContain("118,00");
  });
});
