import type { YearReview } from "@/types";

/** "Retrospectiva de 2002". */
export function summaryTitle({ year }: Pick<YearReview, "year">) {
  return `Retrospectiva de ${year}`;
}
