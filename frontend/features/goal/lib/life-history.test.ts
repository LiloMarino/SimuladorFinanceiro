import { describe, expect, it } from "vitest";
import { Wrench, Zap } from "lucide-react";
import type { LifeHistoryRow } from "@/types";
import { lifeRowIcon, lifeRowText } from "./life-history";

const row = (overrides: Partial<LifeHistoryRow>): LifeHistoryRow => ({
  event_date: "2024-10-15",
  category: "UNEXPECTED",
  kind: "UNEXPECTED_EXPENSE",
  life_event_key: null,
  label: null,
  amount: null,
  cash_after: "1000.00",
  ...overrides,
});

describe("texto do histórico da vida real", () => {
  it("imprevisto usa o nome do evento, ou o genérico", () => {
    expect(lifeRowText(row({ label: "Conserto do carro" }))).toBe("Conserto do carro");
    expect(lifeRowText(row({ label: null }))).toBe("Imprevisto");
  });

  it("a perda de renda tira o mês seguinte", () => {
    expect(lifeRowText(row({ category: "LAYOFF", kind: "LAYOFF" }))).toBe("Renda de novembro não entrou");
    expect(lifeRowText(row({ category: "LAYOFF", kind: "LAYOFF", event_date: "2024-12-20" }))).toBe(
      "Renda de janeiro não entrou",
    );
  });

  it("a demissão cita o desemprego da partida quando o servidor manda", () => {
    expect(lifeRowText(row({ category: "LAYOFF", kind: "LAYOFF", label: "Desemprego de 12,3%" }))).toBe(
      "Renda de novembro não entrou · Desemprego de 12,3%",
    );
  });

  it("as mudanças do orçamento mostram a origem que o servidor escreve", () => {
    const label = "Salário base reajustado para R$ 8.800,00: IPCA de 4,5% e PIB de 3,1%";
    expect(lifeRowText(row({ category: "BUDGET", kind: "SALARY_READJUSTED", label }))).toBe(label);
    expect(lifeRowText(row({ category: "BUDGET", kind: "OVERDRAFT_RATE_CHANGED", label: null }))).toBe(
      "Cheque especial",
    );
  });

  it("o cheque especial entra, sai e cobra juros", () => {
    expect(lifeRowText(row({ category: "OVERDRAFT", kind: "OVERDRAFT_STARTED" }))).toBe("Caixa ficou negativo");
    expect(lifeRowText(row({ category: "OVERDRAFT", kind: "OVERDRAFT_ENDED" }))).toBe("Caixa voltou ao positivo");
    expect(lifeRowText(row({ category: "OVERDRAFT", kind: "OVERDRAFT_INTEREST" }))).toBe("Juros do cheque especial");
  });
});

describe("ícone do histórico", () => {
  it("o imprevisto conhecido tem ícone próprio; o resto usa o do tipo", () => {
    expect(lifeRowIcon(row({ life_event_key: "REPAIR" }))).toBe(Wrench);
    expect(lifeRowIcon(row({ life_event_key: "OUTRO" }))).toBe(Zap);
    expect(lifeRowIcon(row({ life_event_key: null }))).toBe(Zap);
  });
});
