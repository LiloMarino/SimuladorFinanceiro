import { parseLocalDate } from "@/shared/lib/utils/display";
import type { SeriesCoverage } from "@/types";

const STALE_AFTER_DAYS = 2;
const DAY_MS = 1000 * 60 * 60 * 24;

/** Ação cujo último preço tem mais de 2 dias: o pregão de ontem já devia estar lá. */
export function isOutdatedStock(series: SeriesCoverage): boolean {
  if (series.kind !== "STOCK") return false;
  if (!series.real_end) return true;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return (today.getTime() - parseLocalDate(series.real_end).getTime()) / DAY_MS > STALE_AFTER_DAYS;
}
