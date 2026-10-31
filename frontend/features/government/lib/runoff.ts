import { parseLocalDate } from "@/shared/lib/utils/display";
import type { ElectionRound, RunoffRace, RunoffTransfer } from "@/types";

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

/** Os indecisos que ainda sobram do partido que saiu, somados pelo peso de cada grupo (em pontos do eleitorado). */
export function undecidedNow(transfer: RunoffTransfer, weights: Map<string, string>) {
  return transfer.groups.reduce(
    (sum, group) => sum + Number(weights.get(group.group) ?? 0) * Number(group.undecided_now),
    0,
  );
}

/** Os indecisos em pontos inteiros, concordando com o número: "1 ponto segue indeciso", "3 pontos seguem indecisos". */
export function undecidedPointsText(points: number) {
  const whole = Math.round(points);
  return whole === 1 ? "1 ponto segue indeciso" : `${whole} pontos seguem indecisos`;
}

/** O 1º turno que levou ao 2º: o último 1º turno apurado antes dele. */
export function firstRoundBefore(results: ElectionRound[], runoff: ElectionRound) {
  return results.filter((result) => result.round === 1 && result.date < runoff.date).at(-1);
}

/** A virada: o vencedor do 2º turno terminou o 1º atrás do outro finalista; devolve a distância em pontos de voto válido. */
export function turnaroundGap(first: ElectionRound | undefined, runoff: ElectionRound) {
  if (!first || runoff.winner === null) return null;
  const shares = runoff.finalists.map((id) => ({
    id,
    share: Number(first.parties.find((party) => party.party_id === id)?.share ?? 0),
  }));
  const leader = shares.reduce((best, item) => (item.share > best.share ? item : best));
  if (leader.id === runoff.winner) return null;
  const winner = shares.find((item) => item.id === runoff.winner);
  return winner ? (leader.share - winner.share) * 100 : null;
}

/** A parte dos votos do 2º turno em que a barra ganha a linha dos 50%. */
export const RUNOFF_MAJORITY = 50;
