import { parseLocalDate } from "@/shared/lib/utils/display";
import type { RunoffRace, RunoffTransfer } from "@/types";

/** O dia seguinte a uma data ISO: de onde a contagem das ações do 2º turno recomeça. */
export function dayAfter(isoDate: string) {
  const next = parseLocalDate(isoDate);
  next.setDate(next.getDate() + 1);
  return `${next.getFullYear()}-${String(next.getMonth() + 1).padStart(2, "0")}-${String(next.getDate()).padStart(2, "0")}`;
}

/** O finalista à frente na última pesquisa do 2º turno; nulo sem pesquisa. */
export function runoffLeaderId(race: RunoffRace | null | undefined) {
  const poll = race?.polls.at(-1);
  if (!poll) return null;
  const ranked = poll.entries
    .filter((entry) => race?.finalists.includes(entry.party_id))
    .sort((a, b) => Number(b.points) - Number(a.points) || a.party_id - b.party_id);
  return ranked[0]?.party_id ?? null;
}

/** Em cada 100 eleitores do grupo que votaram no eliminado, quantos foram ao finalista na transferência. */
export function sentTo(group: RunoffTransfer["groups"][number], finalistId: number) {
  return Number(group.sent.find((entry) => entry.party_id === finalistId)?.points ?? 0);
}

/** Os indecisos que a declaração leva ao finalista apoiado, somados pelo peso de cada grupo (em pontos do eleitorado). */
export function followTotal(transfer: RunoffTransfer, weights: Map<string, string>) {
  return transfer.groups.reduce(
    (sum, group) => sum + Number(weights.get(group.group) ?? 0) * Number(group.would_follow),
    0,
  );
}
