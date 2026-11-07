import type { GovernmentNotice } from "@/types";
import { displayDayMonth, displayShortDate } from "@/shared/lib/utils/display";
import type { MeasureToast } from "./measure-toast";

/** A proposta que chega ao fundador do partido convidado: de quem, e até quando responder. */
export function federationProposedToast(event: GovernmentNotice): MeasureToast {
  const sender = event.party_abbr ?? "partido";
  const receiver = event.partner_abbr ?? "seu partido";
  const until = event.effective ? `Responda até ${displayDayMonth(event.effective)}; ` : "";
  return {
    tone: "info",
    title: `O ${sender} propõe federação ao ${receiver}`,
    description: `${until}sem resposta, a proposta expira.`,
  };
}

/** A resposta ao fundador que propôs: federação formada, com a data até quando vale, ou recusada. */
export function federationAnsweredToast(event: GovernmentNotice): MeasureToast {
  const receiver = event.party_abbr ?? "partido";
  const name = event.federation_name ?? "federação";
  if (event.accepted) {
    const until = event.effective ? ` Vale até ${displayShortDate(event.effective)}.` : "";
    return { tone: "success", title: `O ${receiver} aceitou a federação`, description: `${name} formada.${until}` };
  }
  return {
    tone: "warning",
    title: `O ${receiver} recusou a federação`,
    description: `A proposta da ${name} foi recusada.`,
  };
}

/** A saída antes do prazo, para o fundador do partido que ficou: a federação se desfez na hora. */
export function federationLeftToast(event: GovernmentNotice): MeasureToast {
  const abbr = event.party_abbr ?? "partido";
  const name = event.federation_name ?? "federação";
  return {
    tone: "warning",
    title: `O ${abbr} deixou a federação`,
    description: `A ${name} acabou na hora para os dois partidos.`,
  };
}
