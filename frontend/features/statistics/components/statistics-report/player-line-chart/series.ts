import type { SeriesPoint } from "@/types";

/** Uma linha do gráfico: um jogador, ou uma referência tracejada (CDI, Ibovespa). */
export interface LineSeries {
  key: string;
  label: string;
  color: string;
  points: SeriesPoint[];
  dashed?: boolean;
  defaultVisible?: boolean;
}
