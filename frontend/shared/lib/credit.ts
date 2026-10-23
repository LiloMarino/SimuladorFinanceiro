import type { CreditGrade } from "@/types";

export type GradeTone = "success" | "warning" | "destructive";

// AAA a A pagam o juro mais baixo; BBB a B ainda têm crédito, mais caro; CCC e D estão no limite ou fora dele
const GRADE_TONES: Record<CreditGrade, GradeTone> = {
  AAA: "success",
  AA: "success",
  A: "success",
  BBB: "warning",
  BB: "warning",
  B: "warning",
  CCC: "destructive",
  D: "destructive",
};

const GRADE_ORDER: CreditGrade[] = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D"];

/** A nota nova está abaixo da anterior? */
export function isDowngrade(before: CreditGrade, after: CreditGrade): boolean {
  return GRADE_ORDER.indexOf(after) > GRADE_ORDER.indexOf(before);
}

export function gradeTone(grade: CreditGrade): GradeTone {
  return GRADE_TONES[grade];
}

/** Taxa mensal equivalente à anual: (1 + anual)^(1/12) − 1, a mesma que a Tabela Price usa. */
export function monthlyEquivalent(annualRate: string | number): number {
  return (1 + Number(annualRate)) ** (1 / 12) - 1;
}

/** Spread como fração do ano (0.065) escrito em pontos ("+6,5"). */
export function displaySpread(spread: string | number): string {
  const points = Number(spread) * 100;
  return `+${points.toLocaleString("pt-BR", { maximumFractionDigits: 2 })}`;
}

/** Spread somado à SELIC, com espaço em volta do "+" ("0.05" → "SELIC + 5"). */
export function displaySelicSpread(spread: string | number): string {
  const points = Number(spread) * 100;
  return `SELIC + ${points.toLocaleString("pt-BR", { maximumFractionDigits: 2 })}`;
}

/** Fração inteira em percentual sem casas ("0.6" → "60%"). */
export function displayWholePercent(fraction: string | number): string {
  return `${Math.round(Number(fraction) * 100)}%`;
}

// O parâmetro da URL que abre o pagamento do atraso de um empréstimo
export const PAY_OVERDUE_PARAM = "pagar";

/** Rota da tela de crédito já com o pagamento do atraso do empréstimo aberto. */
export function payOverdueLink(loanId: string): string {
  return `/credit?${PAY_OVERDUE_PARAM}=${loanId}`;
}
