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
      nickname: null,
      share: null,
    });
    expect(text).toContain("1.600 cotas");
    expect(text).toContain("160.000,00");
  });

  it("a transferência da fusão é uma fusão, não um aporte", () => {
    const text = movementText({
      day: "2024-03-04",
      type: "merger",
      quotas: "300",
      price: null,
      amount: "30000",
      ticker: "PETR4",
      nickname: null,
      share: null,
    });
    expect(text).toContain("Fusão");
    expect(text).toContain("300 de PETR4");
    expect(text).not.toContain("Integralização");
  });

  it("o rendimento diz o total pago aos cotistas", () => {
    const text = movementText({
      day: "2024-02-05",
      type: "distribution",
      quotas: null,
      price: null,
      amount: "9500",
      ticker: null,
      nickname: null,
      share: null,
    });
    expect(text).toContain("9.500,00");
    expect(text).toContain("pago aos cotistas");
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
        nickname: null,
        share: null,
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
        nickname: null,
        share: null,
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
      nickname: null,
      share: null,
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
      nickname: null,
      share: null,
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
      nickname: null,
      share: null,
    });
    expect(text).toContain("300 cotas");
    expect(text).toContain("118,00");
  });

  it("a entrada do co-gestor diz quem é e a parte das taxas", () => {
    const text = movementText({
      day: "2024-03-04",
      type: "comanager_joined",
      quotas: null,
      price: null,
      amount: null,
      ticker: null,
      nickname: "Ana",
      share: "0.2000",
    });
    expect(text).toBe("Ana virou co-gestor, com 20% das taxas");
  });

  it("a saída do co-gestor diz quem deixou a gestão", () => {
    const text = movementText({
      day: "2024-03-09",
      type: "comanager_left",
      quotas: null,
      price: null,
      amount: null,
      ticker: null,
      nickname: "Ana",
      share: null,
    });
    expect(text).toBe("Ana deixou a gestão");
  });

  it("a emissão dirigida diz as cotas, quem comprou e o preço", () => {
    const text = movementText({
      day: "2024-05-06",
      type: "directed_issuance",
      quotas: "1000",
      price: "110.44",
      amount: null,
      ticker: null,
      nickname: "Duda",
      share: null,
    });
    expect(text).toContain("1.000 cotas");
    expect(text).toContain("Duda");
    expect(text).toContain("110,44");
  });
});
