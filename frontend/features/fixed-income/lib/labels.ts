import { differenceInCalendarMonths } from "date-fns";
import { parseLocalDate } from "@/shared/lib/utils/display";
import type { FixedIncomeOffer } from "@/types";

export const INVESTMENT_TYPE_LABELS: Record<FixedIncomeOffer["investment_type"], string> = {
  CDB: "CDB",
  LCI: "LCI",
  LCA: "LCA",
  "Tesouro Direto": "Tesouro",
};

export const RATE_KIND_LABELS: Record<FixedIncomeOffer["rate_index"], string> = {
  CDI: "pós-fixado",
  SELIC: "pós-fixado",
  IPCA: "híbrido",
  Prefixado: "prefixado",
};

/** "em 2 anos", "em 8 meses": quanto falta para o vencimento, contado da data da simulação. */
export function timeToMaturity(maturity: string, today: string) {
  const months = differenceInCalendarMonths(parseLocalDate(maturity), parseLocalDate(today));
  if (months >= 12) {
    const years = Math.floor(months / 12);
    return `em ${years} ${years === 1 ? "ano" : "anos"}`;
  }
  return months > 0 ? `em ${months} ${months === 1 ? "mês" : "meses"}` : "este mês";
}
