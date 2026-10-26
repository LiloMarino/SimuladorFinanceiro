import { displayDecimal } from "@/shared/lib/utils/display";

const MONTHS_PER_YEAR = 12;

/** Faixa de taxa de retirada que o servidor aceita, como fração ao ano (0,04 = 4%). */
export const WITHDRAWAL_RATE_RANGE = { min: 0.01, max: 0.1 } as const;

/** Imprevistos sorteados por ano, na ordem do seletor. */
export const UNEXPECTED_OPTIONS = [
  { perYear: 0, label: "Nenhum" },
  { perYear: 1, label: "Raros" },
  { perYear: 3, label: "Normais" },
  { perYear: 6, label: "Frequentes" },
] as const;

/** Valores com que o servidor cria a partida; o formulário volta a eles quando um campo escondido fica inválido. */
export const LIFE_DEFAULTS = {
  monthlySalary: "8000.00",
  monthlyExpense: "5000.00",
  unexpectedPerYear: 3,
  withdrawalRate: "0.04",
  inflationAdjusted: false,
} as const;

export function unexpectedLabel(perYear: number) {
  return UNEXPECTED_OPTIONS.find((o) => o.perYear === perYear)?.label ?? `${perYear} por ano`;
}

/** O patrimônio que paga a despesa do ano retirando `withdrawalRate` dele. */
export function independenceGoal(monthlyExpense: number, withdrawalRate: number) {
  return (MONTHS_PER_YEAR * monthlyExpense) / withdrawalRate;
}

/** Quantas despesas anuais a meta pede: 1 ÷ taxa (4% → 25). */
export function annualExpenseMultiple(withdrawalRate: number) {
  return 1 / withdrawalRate;
}

/** "25×": quantas despesas anuais a meta pede. */
export function displayAnnualMultiple(withdrawalRate: number) {
  return `${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(annualExpenseMultiple(withdrawalRate))}×`;
}

export function displayAnnualExpenseMultiple(withdrawalRate: number) {
  return `${displayAnnualMultiple(withdrawalRate)} a despesa anual`;
}

/** "0.04" do servidor → "4" do campo (percentual ao ano). */
export function withdrawalRateToField(rate: string | number) {
  return displayDecimal(Number(rate) * 100);
}

/** 0.08 → "8%", 0.085 → "8,5%": a taxa como o jogador a escreve. */
export function displayRatePercent(rate: string | number) {
  return `${displayDecimal(Number(rate) * 100)}%`;
}
