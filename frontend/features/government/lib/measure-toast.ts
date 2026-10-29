import type { GovernmentApproval, GovernmentNotice } from "@/types";
import { closingSentence, deltaLabel } from "./approval";
import { lowStreakLabel } from "./government";

export type MeasureToast = {
  tone: "success" | "info" | "warning" | "error";
  title: string;
  description: string;
};

/** Aviso ao presidente de quantos fechamentos abaixo do piso ainda separam o governo do impeachment. */
export function warningToast(
  event: GovernmentNotice,
  approval: Pick<GovernmentApproval, "floor" | "impeachment_months">,
): MeasureToast {
  const months = event.months_below_floor ?? 0;
  const left = Math.max(0, approval.impeachment_months - months);
  const consequence =
    left <= 1
      ? "Se o próximo fechamento ficar abaixo do piso, o impeachment tira você do governo."
      : `Mais ${left} fechamentos abaixo do piso e o impeachment tira você do governo.`;
  return {
    tone: "error",
    title: lowStreakLabel({ low_streak: months, ...approval }),
    description: `Aprovação de ${event.approval ?? "?"}% no fechamento do mês. ${consequence}`,
  };
}

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
