import type { ElectionPanel, GovernmentPanel, MeasureKind } from "@/types";
import { unguidedCount, unguidedDeadline } from "./house";

export type GovernmentPending = {
  /** Votações a caminho do plenário sem orientação da bancada, com o dia da mais próxima */
  unguided: { count: number; date: string | null } | null;
  /** Promessas da chapa que governa e ainda não andaram, com o dia da última votação que conta para elas */
  idlePromises: { titles: string[]; kind: MeasureKind; lastVote: string } | null;
};

/** O que o presidente ou o líder da bancada ainda decide no Governo; cada item tem prazo. */
export function governmentPending(panel: GovernmentPanel): GovernmentPending {
  const count = unguidedCount(panel.congress, panel.queue);
  const idle = panel.is_president ? (panel.promises?.items.filter((item) => item.state === "UNTOUCHED") ?? []) : [];
  const lastVote = panel.promises?.last_vote ?? null;
  const first = idle[0];

  return {
    unguided: count > 0 ? { count, date: unguidedDeadline(panel.queue) } : null,
    idlePromises:
      first && lastVote !== null && lastVote >= panel.today
        ? { titles: idle.map((item) => item.promise.title), kind: first.promise.kind, lastVote }
        : null,
  };
}

/** Quantos itens o selo da aba Suas ações do Governo conta. */
export function governmentPendingCount(pending: GovernmentPending): number {
  return (pending.unguided ? 1 : 0) + (pending.idlePromises ? 1 : 0);
}

export type ElectionPending = {
  /** A chapa do partido de quem lidera está sem vice e sem convite pendente */
  vice: boolean;
  /** A chapa do partido de quem lidera ainda não prometeu nada */
  promises: boolean;
};

/** O que o fundador ainda decide na chapa até o prazo de inscrição. */
export function electionPending(panel: ElectionPanel): ElectionPending {
  const mine = panel.my_party;
  const party = mine ? panel.parties.find((candidate) => candidate.id === mine.party_id) : undefined;
  const editing = !!party && !!mine?.is_founder && panel.can_edit_ticket;

  return {
    vice: editing && party.vice === null && party.vice_phase === "NONE",
    promises: editing && party.promises.length === 0,
  };
}

export function electionPendingCount(pending: ElectionPending): number {
  return (pending.vice ? 1 : 0) + (pending.promises ? 1 : 0);
}
