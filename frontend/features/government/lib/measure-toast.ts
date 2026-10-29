import type { GovernmentNotice } from "@/types";
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
