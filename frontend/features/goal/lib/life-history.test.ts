import { describe, expect, it } from "vitest";
import { Wrench, Zap } from "lucide-react";
import type { LifeHistoryRow } from "@/types";
import { lifeRowIcon, lifeRowText } from "./life-history";

const row = (overrides: Partial<LifeHistoryRow>): LifeHistoryRow => ({
  event_date: "2024-10-15",
  category: "UNEXPECTED",
  kind: "UNEXPECTED_EXPENSE",
  cash_after: "1000.00",
  ...overrides,
});

describe("texto do histórico da vida real", () => {
  it("imprevisto usa o nome do evento, ou o genérico", () => {
    expect(lifeRowText(row({ label: "Conserto do carro" }), "0.08")).toBe("Conserto do carro");
    expect(lifeRowText(row({ label: null }), "0.08")).toBe("Imprevisto");
  });

  it("a demissão tira o salário do mês seguinte", () => {
    expect(lifeRowText(row({ category: "LAYOFF", kind: "LAYOFF" }), "0.08")).toBe("Salário de novembro não entrou");
    expect(lifeRowText(row({ category: "LAYOFF", kind: "LAYOFF", event_date: "2024-12-20" }), "0.08")).toBe(
      "Salário de janeiro não entrou",
    );
  });

  it("o cheque especial entra, sai e cobra juros pela taxa do mês", () => {
    expect(lifeRowText(row({ category: "OVERDRAFT", kind: "OVERDRAFT_STARTED" }), "0.08")).toBe("Caixa ficou negativo");
    expect(lifeRowText(row({ category: "OVERDRAFT", kind: "OVERDRAFT_ENDED" }), "0.08")).toBe(
      "Caixa voltou ao positivo",
    );
    expect(lifeRowText(row({ category: "OVERDRAFT", kind: "OVERDRAFT_INTEREST" }), "0.08")).toBe("Juros de 8% ao mês");
  });
});

describe("ícone do histórico", () => {
  it("o imprevisto conhecido tem ícone próprio; o resto usa o do tipo", () => {
    expect(lifeRowIcon(row({ life_event_key: "REPAIR" }))).toBe(Wrench);
    expect(lifeRowIcon(row({ life_event_key: "OUTRO" }))).toBe(Zap);
    expect(lifeRowIcon(row({ life_event_key: null }))).toBe(Zap);
  });
});
