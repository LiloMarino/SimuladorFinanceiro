import { displayDayMonth, displayPercent } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";

export type RoundToast = {
  tone: "success" | "info" | "warning";
  title: string;
  description: string;
  /** O aviso de quem ficou fora do 2º turno leva à doação */
  donate?: boolean;
};

/**
 * O toast do resultado de um turno para quem tem partido: segue, vence, fica de fora ou perde.
 * Quem não é filiado só vê o diálogo do resultado.
 */
export function roundToast(panel: ElectionPanel): RoundToast | null {
  const result = panel.last_result;
  const mineId = panel.my_party?.party_id;
  if (!result || mineId === undefined) return null;

  const ranked = [...result.parties].sort((a, b) => Number(b.share) - Number(a.share) || a.party_id - b.party_id);
  const place = ranked.findIndex((party) => party.party_id === mineId) + 1;
  const mine = ranked[place - 1];
  if (!mine) return null;

  const share = displayPercent(mine.share, 0);
  const winner = result.parties.find((party) => party.party_id === result.winner);

  if (winner) {
    if (winner.party_id === mineId) {
      return {
        tone: "success",
        title: "Seu partido venceu a eleição",
        description: `O ${mine.abbr} levou com ${share} no ${result.round}º turno.`,
      };
    }
    return {
      tone: "info",
      title: `O ${mine.abbr} não venceu a eleição`,
      description: `${place}º lugar, com ${share} dos votos válidos. O ${winner.abbr} levou no ${result.round}º turno.`,
    };
  }

  const finalists = result.parties.filter((party) => result.finalists.includes(party.party_id));
  if (result.finalists.includes(mineId)) {
    const rival = finalists.find((party) => party.party_id !== mineId);
    return {
      tone: "info",
      title: "Seu partido vai ao 2º turno",
      description: `O ${mine.abbr} teve ${share} dos válidos e enfrenta o ${rival?.abbr}. Votação em ${displayDayMonth(panel.dates.runoff)}.`,
    };
  }

  const names = finalists.map((party) => `ao ${party.abbr}`).join(" ou ");
  return {
    tone: "warning",
    title: `O ${mine.abbr} ficou fora do 2º turno`,
    description: `${place}º lugar, com ${share} dos válidos. Até ${displayDayMonth(panel.dates.donation_deadline)}, você pode doar ${names}.`,
    donate: true,
  };
}

/** A linha de contexto do toast de doação: a favor de quem lidera a simulação do 2º turno, ou contra. */
export function donationContext(panel: ElectionPanel | undefined, targetAbbr: string): string | null {
  const leader = panel?.parties.find((party) => party.id === panel.runoff_simulation?.winner);
  if (!leader) return null;
  return leader.abbr === targetAbbr
    ? `A favor do ${leader.abbr}, que lidera a simulação do 2º turno.`
    : `Contra o ${leader.abbr}, que lidera a simulação do 2º turno.`;
}
