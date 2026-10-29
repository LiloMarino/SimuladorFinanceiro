import type { GovernmentNotice } from "@/types";
import { displayDayMonth } from "@/shared/lib/utils/display";
import { groupsLabel, monthlyLabel } from "./base";
import type { MeasureToast } from "./measure-toast";

const seatsText = (count: number | null) => (count === null ? "" : `${count}`);

/** A resposta ao presidente: aceita (a base cresce e a emenda começa) ou recusada (nova proposta só depois do prazo de espera). */
export function dealAnsweredToast(event: GovernmentNotice): MeasureToast {
  const abbr = event.party_abbr ?? "partido";
  const who = event.actor ?? `O ${abbr}`;
  const before = seatsText(event.seats_before ?? null);
  const after = seatsText(event.seats_after ?? null);

  if (event.accepted) {
    const until = event.effective ? `, até ${displayDayMonth(event.effective)}` : "";
    const amount = event.amount ? ` Emenda de ${monthlyLabel(event.amount)} a partir de hoje.` : "";
    return {
      tone: "success",
      title: event.actor ? `${who} aceitou: o ${abbr} entra na base` : `${abbr} aceitou entrar na base`,
      description: `Base de ${before} para ${after} cadeiras${until}.${amount}`,
    };
  }
  const retry = event.effective ? ` Nova proposta a partir de ${displayDayMonth(event.effective)}.` : "";
  return {
    tone: "warning",
    title: event.actor ? `${who} recusou a proposta` : `${abbr} recusou a proposta`,
    description: `O ${abbr} segue fora da base, que continua com ${after} cadeiras.${retry}`,
  };
}

/** A quebra para o lado que sofreu: o governo cortou a emenda ou o aliado saiu da base. */
export function dealBrokenToast(event: GovernmentNotice): MeasureToast {
  const abbr = event.party_abbr ?? "partido";
  const government = event.rival_abbr ?? "governo";
  const before = seatsText(event.seats_before ?? null);
  const after = seatsText(event.seats_after ?? null);
  const groups = groupsLabel(event.groups_reproved ?? []);

  if (event.broken_by_ally) {
    return {
      tone: "error",
      title: `O ${abbr} saiu da base`,
      description: `A base caiu de ${before} para ${after} cadeiras. ${groups} culpam o ${abbr}.`,
    };
  }
  return {
    tone: "error",
    title: `O governo ${government} rompeu o acordo com o ${abbr}`,
    description: `A emenda às suas bases parou. ${groups} culpam o ${government}.`,
  };
}

/** O fim de prazo e o fim na posse do novo Congresso: sem quebra, sem rejeição. */
export function dealEndedToast(event: GovernmentNotice): MeasureToast {
  const abbrs = event.party_abbr ?? "";
  const newCongress = event.accepted === true;
  return {
    tone: "info",
    title: newCongress ? "Acordos encerrados na posse do novo Congresso" : `Acordo com o ${abbrs} chegou ao fim`,
    description: newCongress
      ? `${abbrs} saem da base sem quebra. Negocie com as bancadas novas.`
      : `O prazo venceu sem quebra: a base perde as cadeiras do ${abbrs}.`,
  };
}
