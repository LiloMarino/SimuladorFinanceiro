import { displayPercent, displayShortDate } from "@/shared/lib/utils/display";
import type { GovernmentNotice } from "@/types";
import type { MeasureToast } from "./measure-toast";

const percent = (share: string) => displayPercent(share, 1, { trim: true });

/** O resultado de um turno para toda a sala: quem venceu, ou quem vai ao 2º turno e quem pode declarar apoio. */
export function roundResultToast(event: GovernmentNotice): MeasureToast {
  const round = event.round ?? 1;
  if (event.winner_abbr) {
    const name = event.winner_name ?? `O candidato do ${event.winner_abbr}`;
    const inauguration = event.inauguration ? ` Posse em ${displayShortDate(event.inauguration)}.` : "";
    return {
      tone: "success",
      title: `Resultado do ${round}º turno`,
      description: `${name} (${event.winner_abbr}) venceu${round === 1 ? " já no 1º turno" : ""} com ${percent(event.winner_share ?? "0")} dos votos válidos.${inauguration}`,
    };
  }
  const leaders = Object.entries(event.endorsers ?? {}).map(([abbr, founder]) => `${founder} (${abbr})`);
  const declare =
    leaders.length > 0
      ? ` ${leaders.join(" e ")} ${leaders.length === 1 ? "pode declarar" : "podem declarar"} apoio a um dos dois.`
      : "";
  const when = event.runoff ? `, em ${displayShortDate(event.runoff)}` : "";
  return {
    tone: "info",
    title: `Resultado do ${round}º turno`,
    description: `${(event.finalists ?? []).join(" e ")} vão ao 2º turno${when}.${declare}`,
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
