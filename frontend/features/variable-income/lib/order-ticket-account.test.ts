import { describe, expect, it } from "vitest";
import { ticketAccountHeading, ticketAccountSubmitLabel } from "./order-ticket-account";

const manager = { fund_id: 3, name: "Aurora Gestão", role: "manager" } as const;
const comanager = { fund_id: 3, name: "Aurora Gestão", role: "comanager" } as const;
const sovereign = { fund_id: 0, name: "Fundo Soberano", role: "president" } as const;

describe("ticketAccountHeading", () => {
  it("a gestora opera 'pela' e o Fundo Soberano 'pelo'", () => {
    expect(ticketAccountHeading(manager)).toBe("Operando pela Aurora Gestão");
    expect(ticketAccountHeading(sovereign)).toBe("Operando pelo Fundo Soberano");
  });

  it("o co-gestor vê o papel dele no cabeçalho", () => {
    expect(ticketAccountHeading(comanager)).toBe("Operando pela Aurora Gestão · você é co-gestor");
  });
});

describe("ticketAccountSubmitLabel", () => {
  it("comprar e vender pela gestora dizem o ativo e a conta", () => {
    expect(ticketAccountSubmitLabel(manager, "buy", "WEGE3")).toBe("Comprar WEGE3 pela gestora");
    expect(ticketAccountSubmitLabel(manager, "sell", "WEGE3")).toBe("Vender WEGE3 pela gestora");
  });

  it("o Fundo Soberano diz o nome dele", () => {
    expect(ticketAccountSubmitLabel(sovereign, "buy", "WEGE3")).toBe("Comprar pelo Fundo Soberano");
    expect(ticketAccountSubmitLabel(sovereign, "sell", "WEGE3")).toBe("Vender pelo Fundo Soberano");
  });
});
