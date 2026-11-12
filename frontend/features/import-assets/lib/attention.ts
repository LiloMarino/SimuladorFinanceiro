import { isOutdatedStock } from "@/shared/lib/series-coverage";
import type { SeriesCoverage } from "@/types";

/** A série pede atenção: sem dado, ação com preço velho ou ação sem setor. */
export const needsAttention = (series: SeriesCoverage) =>
  !series.real_end || isOutdatedStock(series) || (series.kind === "STOCK" && !series.segment);
