import { displayDayMonth } from "@/shared/lib/utils/display";
import type { GovernmentNotice } from "@/types";

export type CalendarToast = {
  tone: "info" | "warning";
  title: string;
  description: string;
};

/** Os lembretes do calendário, sem pausa: as chapas para fechar e a véspera do 1º turno. */
export function calendarToast(event: GovernmentNotice): CalendarToast | null {
  if (!event.ticket_deadline || !event.first_round) return null;
  switch (event.kind) {
    case "TICKETS_CLOSING":
      return {
        tone: "warning",
        title: `As chapas fecham em ${displayDayMonth(event.ticket_deadline)}`,
        description: "O partido precisa de candidato (e de vice, se quiser) registrado até lá.",
      };
    case "ELECTION_EVE":
      return {
        tone: "info",
        title: `O 1º turno é em ${displayDayMonth(event.first_round)}`,
        description: "As chapas já fecharam: o resultado sai na apuração do dia.",
      };
    default:
      return null;
  }
}
