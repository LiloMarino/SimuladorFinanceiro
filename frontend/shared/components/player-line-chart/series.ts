import type { SeriesPoint, TeamNaming } from "@/types";

/** Uma linha do gráfico: um jogador, ou uma referência tracejada (CDI, Ibovespa). */
export interface LineSeries {
  key: string;
  label: string;
  color: string;
  points: SeriesPoint[];
  dashed?: boolean;
  /** Referência em pontos, para distinguir de uma tracejada na mesma tela */
  dotted?: boolean;
  /** A linha de quem está vendo: mais grossa */
  emphasis?: boolean;
  /** Linha de contexto, mais apagada */
  muted?: boolean;
  /** Área leve sob a linha, para a série em destaque */
  area?: boolean;
  defaultVisible?: boolean;
  /** Séries do mesmo grupo dividem uma só entrada da legenda (ex.: "Outras equipes · média") */
  legendGroup?: { key: string; label: string };
  /** Equipe do jogador: o escudo dela aparece na legenda */
  team?: { index: number | null; naming: TeamNaming };
}
