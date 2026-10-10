import type { SeriesCoverage } from "@/types";

// Indexadores da renda fixa: a partida só nasce com os três cobertos no início
const RATE_SERIES = ["CDI", "SELIC", "IPCA"];

export type CoverageCheck = {
  /** Indexadores sem dado no dia de início: bloqueiam a partida */
  missingAtStart: SeriesCoverage[];
  /** Séries cujo dado real acaba antes da data final: dali em diante vale o último valor */
  endingBeforeEnd: SeriesCoverage[];
};

/** Datas em ISO ("2020-01-06") se comparam como texto. O IPCA é mensal e vale desde o dia 1. */
export function checkCoverage(coverage: SeriesCoverage[], startDate: string, endDate: string): CoverageCheck {
  const missingAtStart = coverage.filter((s) => {
    if (s.kind !== "INDICATOR" || !RATE_SERIES.includes(s.key)) return false;
    const reference = s.key === "IPCA" ? `${startDate.slice(0, 8)}01` : startDate;
    return !s.start || s.start > reference;
  });
  const endingBeforeEnd = coverage.filter((s) => s.real_end && s.real_end < endDate);

  return { missingAtStart, endingBeforeEnd };
}
