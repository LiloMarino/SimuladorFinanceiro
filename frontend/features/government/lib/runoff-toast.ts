import { displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionRound, GovernmentNotice } from "@/types";
import type { MeasureToast } from "./measure-toast";

const percent = (share: string) => `${(Number(share) * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%`;

/** O resultado de um turno para toda a sala: quem venceu, ou quem vai ao 2º turno e quem pode declarar apoio. */
export function roundResultToast(panel: ElectionPanel, result: ElectionRound): MeasureToast {
  const winner = result.parties.find((party) => party.party_id === result.winner);
  if (winner) {
    const name = winner.candidate?.name ?? `O candidato do ${winner.abbr}`;
    return {
      tone: "success",
      title: `Resultado do ${result.round}º turno`,
      description: `${name} (${winner.abbr}) venceu${result.round === 1 ? " já no 1º turno" : ""} com ${percent(winner.share)} dos votos válidos. Posse em ${displayShortDate(panel.dates.inauguration)}.`,
    };
  }
  const finalists = result.parties.filter((party) => result.finalists.includes(party.party_id));
  const eliminated = result.parties.filter((party) => !result.finalists.includes(party.party_id));
  const leaders = eliminated
    .map((party) => panel.parties.find((candidate) => candidate.id === party.party_id))
    .filter((party) => party?.founder)
    .map((party) => `${party?.founder} (${party?.abbr})`);
  const declare =
    leaders.length > 0
      ? ` ${leaders.join(" e ")} ${leaders.length === 1 ? "pode declarar" : "podem declarar"} apoio a um dos dois.`
      : "";
  return {
    tone: "info",
    title: `Resultado do ${result.round}º turno`,
    description: `${finalists.map((party) => party.abbr).join(" e ")} vão ao 2º turno, em ${displayShortDate(panel.dates.runoff)}.${declare}`,
  };
}

/** A declaração de apoio do partido eliminado, para toda a sala. */
export function endorsementToast(event: GovernmentNotice): MeasureToast {
  const abbr = event.party_abbr ?? "partido";
  const who = event.actor ? `${event.actor} (${abbr})` : `O ${abbr}`;
  if (event.rival_abbr) {
    return {
      tone: "info",
      title: `${who} declarou apoio ao ${event.rival_abbr}`,
      description: "O efeito nos indecisos aparece na próxima pesquisa.",
    };
  }
  return {
    tone: "info",
    title: `${who} declarou neutralidade`,
    description: `Os indecisos do ${abbr} ficam para as campanhas disputarem.`,
  };
}
