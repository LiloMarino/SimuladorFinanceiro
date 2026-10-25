import { describe, expect, it } from "vitest";
import { displayBotParam } from "./bot-param";

describe("displayBotParam", () => {
  it("junta o número e a unidade", () => {
    expect(displayBotParam({ label: "Média curta", value: 50, unit: "dias" })).toBe("50 dias");
  });

  it("cola o % ao número", () => {
    expect(displayBotParam({ label: "Quanto do saldo por compra", value: 20, unit: "%" })).toBe("20%");
  });

  it("lista as ações e resume as que passam de cinco", () => {
    const tickers = ["PETR4", "VALE3", "ITUB4", "BBDC4", "WEGE3", "ABEV3", "B3SA3"];
    // 7 ações: 5 por extenso e 2 no "+2"
    expect(displayBotParam({ label: "Ações", value: tickers, unit: null })).toBe(
      "PETR4, VALE3, ITUB4, BBDC4, WEGE3 +2",
    );
    expect(displayBotParam({ label: "Ações", value: tickers.slice(0, 2), unit: null })).toBe("PETR4, VALE3");
  });

  it("mostra o ativo único como texto", () => {
    expect(displayBotParam({ label: "Ativo", value: "BOVA11", unit: null })).toBe("BOVA11");
  });
});
