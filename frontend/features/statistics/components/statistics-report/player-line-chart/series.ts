import type { SeriesPoint, TeamNaming } from "@/types";

/** Uma linha do gráfico: um jogador, ou uma referência tracejada (CDI, Ibovespa). */
export interface LineSeries {
  key: string;
  label: string;
  color: string;
  points: SeriesPoint[];
  dashed?: boolean;
  /** A linha de quem está vendo: mais grossa */
  emphasis?: boolean;
  /** Linha de contexto, mais apagada */
  muted?: boolean;
  /** Área leve sob a linha, para a série em destaque */
  area?: boolean;
  defaultVisible?: boolean;
  /** Equipe do jogador: o escudo dela aparece na legenda */
  team?: { index: number | null; naming: TeamNaming };
}
