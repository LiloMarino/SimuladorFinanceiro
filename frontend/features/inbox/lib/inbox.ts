import { displayMonthName, parseLocalDate } from "@/shared/lib/utils/display";
import type { InboxEntry, MonthSummary } from "@/types";

/** "Resumo de novembro de 2002" ou "Retrospectiva de 2002". */
export function entryTitle(content: InboxEntry["content"]) {
  if (content.kind === "YEAR_REVIEW") return `Retrospectiva de ${content.year}`;
  return `Resumo de ${displayMonthName(content.month)} de ${parseLocalDate(content.month).getFullYear()}`;
}

/** "2º de 5" e quanto andou desde o resumo anterior. */
export function displayRanking({ position, players, change }: NonNullable<MonthSummary["ranking"]>) {
  const place = `${position}º de ${players}`;
  if (change === null) return place;
  if (change === 0) return `${place}, manteve a posição`;
  const steps = Math.abs(change);
  return `${place}, ${change > 0 ? "subiu" : "desceu"} ${steps} ${steps === 1 ? "posição" : "posições"}`;
}
