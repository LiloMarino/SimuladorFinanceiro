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

  it("o imprevisto bom usa o nome do evento, ou o genérico", () => {
    expect(lifeRowText(row({ kind: "UNEXPECTED_INCOME", label: "Restituição do imposto de renda" }))).toBe(
      "Restituição do imposto de renda",
    );
    expect(lifeRowText(row({ kind: "UNEXPECTED_INCOME", label: null }))).toBe("Imprevisto");
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

  it("a troca de profissão nomeia o destino, ou fica genérica", () => {
    expect(lifeRowText(row({ category: "PROFESSION", kind: "PROFESSION_SWITCHED", life_event_key: "CLT" }))).toBe(
      "Mudou de profissão para CLT",
    );
    expect(lifeRowText(row({ category: "PROFESSION", kind: "PROFESSION_SWITCHED", life_event_key: null }))).toBe(
      "Mudou de profissão",
    );
  });

  it("a hora extra liga, desliga e acaba com a recessão", () => {
    const action = (key: string) => row({ category: "PROFESSION", kind: "PROFESSION_ACTION", life_event_key: key });
    expect(lifeRowText(action("overtime_on"))).toBe("Ligou a hora extra");
    expect(lifeRowText(action("overtime_off"))).toBe("Desligou a hora extra");
    expect(lifeRowText(action("overtime_ended"))).toBe("A hora extra acabou com a recessão");
    expect(lifeRowText(action("overtime_available"))).toBe("A hora extra pode voltar");
  });

  it("o Locador tem um texto para cada passo dos imóveis", () => {
    const action = (key: string) => row({ category: "PROFESSION", kind: "PROFESSION_ACTION", life_event_key: key });
    expect(lifeRowText(action("property_bought"))).toBe("Comprou um imóvel");
    expect(lifeRowText(action("property_sold"))).toBe("Vendeu um imóvel");
    expect(lifeRowText(action("property_vacated"))).toBe("Um imóvel ficou vago");
    expect(lifeRowText(action("property_rented"))).toBe("Um imóvel voltou ao aluguel");
  });

  it("o Administrador tem um texto para a troca de setor e para o concurso", () => {
    const action = (key: string) => row({ category: "PROFESSION", kind: "PROFESSION_ACTION", life_event_key: key });
    expect(lifeRowText(action("sector_exporter"))).toBe("Pediu a troca para o setor Exportador");
    expect(lifeRowText(action("exam_enrolled"))).toBe("Inscreveu-se no concurso para Servidor");
    expect(lifeRowText(action("exam_passed"))).toBe("Passou no concurso para Servidor");
    expect(lifeRowText(action("exam_failed"))).toBe("Não passou no concurso para Servidor");
  });

  it("o saque do FGTS na demissão diz que veio com a multa", () => {
    expect(lifeRowText(row({ category: "PROFESSION", kind: "FGTS_WITHDRAWAL" }))).toBe(
      "Saque do FGTS com a multa de 40%",
    );
  });
});

describe("ícone do histórico", () => {
  it("o imprevisto conhecido tem ícone próprio; o resto usa o do tipo", () => {
    expect(lifeRowIcon(row({ life_event_key: "REPAIR" }))).toBe(Wrench);
    expect(lifeRowIcon(row({ life_event_key: "OUTRO" }))).toBe(Zap);
    expect(lifeRowIcon(row({ life_event_key: null }))).toBe(Zap);
  });
});
