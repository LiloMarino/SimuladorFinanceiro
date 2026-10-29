import type { GovernmentNotice } from "@/types";
import { displayDayMonth } from "@/shared/lib/utils/display";
import { closingSentence, deltaLabel } from "./approval";

export type MeasureToast = {
  tone: "success" | "info" | "warning" | "error";
  title: string;
  description: string;
};

/** O fechamento do mês para os filiados do partido do presidente: a aprovação e o que ela fez com o apoio. */
export function monthClosedToast(event: GovernmentNotice): MeasureToast {
  const approved = event.groups_approved ?? [];
  const reproved = event.groups_reproved ?? [];
  const abbr = event.party_abbr ?? "partido";
  const moved = deltaLabel(event.approval ?? 0, event.previous_approval ?? null);
  const effect = closingSentence(abbr, { approved, reproved, neutral: [] });
  return {
    tone: "info",
    title: "Mês fechado",
    description: `Aprovação ${event.approval ?? "?"}%${moved ? ` (${moved})` : ""}. ${effect}`.trim(),
  };
}

/** "Congresso aprovou por 54 a 47": o placar da votação de uma medida, para toda a sala. */
export function measureVotedToast(event: GovernmentNotice): MeasureToast {
  const approved = event.accepted === true;
  const yes = event.yes ?? 0;
  const no = event.no ?? 0;
  const defected = event.defected ?? 0;
  const against =
    defected > 0 ? ` ${defected} ${defected === 1 ? "deputado votou" : "deputados votaram"} contra a orientação.` : "";
  const title = event.measure_title ?? "A medida";
  return {
    tone: approved ? "success" : "warning",
    title: `Congresso ${approved ? "aprovou" : "rejeitou"} por ${approved ? yes : no} a ${approved ? no : yes}`,
    description: `${title}${approved && event.effective ? ` e vale em ${displayDayMonth(event.effective)}.` : "."}${against}`,
  };
}

/** O pedido de impeachment aberto, e o pedido rejeitado pela casa: o aprovado abre o diálogo. */
export function impeachmentToast(event: GovernmentNotice, needed: number): MeasureToast {
  if (event.kind === "IMPEACHMENT_REQUESTED") {
    return {
      tone: "warning",
      title: "Pedido de impeachment aberto",
      description: event.effective
        ? `A casa vota em ${displayDayMonth(event.effective)}.`
        : "A casa vota no mês que vem.",
    };
  }
  const yes = event.yes ?? 0;
  return {
    tone: "info",
    title: `Pedido rejeitado: ${yes} votos Sim, faltaram ${Math.max(needed - yes, 0)}`,
    description: "O presidente fica e a contagem de meses abaixo do piso recomeça do zero.",
  };
}
