import { payOverdueLink } from "@/shared/lib/credit";
import type { Pending, PendingType } from "@/types";

/** A ação que resolve a pendência: o texto do botão e a rota (com o diálogo que a página abre ao chegar). */
export type PendingTarget = {
  label: string;
  to: string;
  state?: { dialog: "vice" | "campaign" | "contribution" };
};

const TARGETS: Record<PendingType, (item: Pending) => PendingTarget> = {
  OVERDUE_INSTALLMENT: (item) => ({
    label: "Pagar",
    to: item.loan_id ? payOverdueLink(item.loan_id) : "/credit",
  }),
  NEGATIVE_CASH: () => ({ label: "Ver carteira", to: "/portfolio" }),
  IMPEACHMENT_RISK: () => ({ label: "Ver governo", to: "/government" }),
  SELIC_MEETING: () => ({ label: "Marcar a SELIC", to: "/government?tab=accounts" }),
  CASH_SHORT: () => ({ label: "Ver crédito", to: "/credit" }),
  STRATEGY_ERROR: () => ({ label: "Religar", to: "/strategies" }),
  UNGUIDED_VOTE: () => ({ label: "Orientar", to: "/government?tab=congress" }),
  VICE_INVITE: () => ({ label: "Responder", to: "/election", state: { dialog: "vice" } }),
  DEAL_PROPOSAL: () => ({ label: "Responder", to: "/government?tab=accounts&deal=answer" }),
  DEAL_DEMAND: () => ({ label: "Responder", to: "/government?tab=accounts" }),
  CAMPAIGN_OPEN: () => ({ label: "Ver eleição", to: "/election", state: { dialog: "campaign" } }),
  UNPAID_CONTRIBUTION: () => ({ label: "Mudar valor", to: "/election", state: { dialog: "contribution" } }),
};

export function pendingTarget(item: Pending): PendingTarget {
  return TARGETS[item.type](item);
}

/** Quantas pendências são graves: a contagem do cabeçalho e a cor do número no menu. */
export function severeCount(items: Pending[]): number {
  return items.filter((item) => item.severity === "SEVERE").length;
}

/** "3 graves" ou "1 grave" */
export function severeLabel(count: number): string {
  return `${count} ${count === 1 ? "grave" : "graves"}`;
}

/** As pendências que nasceram entre duas leituras da lista, pela chave. */
export function bornSince(before: ReadonlySet<string>, items: Pending[]): Pending[] {
  return items.filter((item) => !before.has(item.key));
}

/** A gravidade que o ponto do item do menu mostra: a pior entre as pendências dos tipos dele, ou nenhuma. */
export function menuDotSeverity(items: Pending[] | undefined, types: PendingType[]): Pending["severity"] | undefined {
  const mine = (items ?? []).filter((item) => types.includes(item.type));
  if (mine.length === 0) return undefined;
  return mine.some((item) => item.severity === "SEVERE") ? "SEVERE" : "WARNING";
}
