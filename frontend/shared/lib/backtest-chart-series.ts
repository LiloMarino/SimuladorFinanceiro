import type { LineSeries } from "@/shared/components/player-line-chart";
import type { BacktestParticipant, BacktestPoint } from "@/types";

/** As linhas do gráfico: uma por estratégia, o CDI tracejado, o Ibovespa pontilhado e o total aportado. */
export function chartSeries(participants: BacktestParticipant[], points: BacktestPoint[]): LineSeries[] {
  const strategies = participants.map<LineSeries>((participant, index) => ({
    key: participant.nickname,
    label: participant.nickname,
    color: `var(--${participant.color})`,
    emphasis: true,
    points: points.flatMap((point) => {
      const value = point.equity[index];
      return value === undefined ? [] : [{ date: point.day, value }];
    }),
  }));

  return [...strategies, ...referenceSeries(points)];
}

type ReferencePoint = Pick<BacktestPoint, "day" | "contributed" | "cdi" | "ibov">;

/** As linhas de referência: o CDI tracejado, o Ibovespa pontilhado e o total aportado. */
export function referenceSeries(points: ReferencePoint[]): LineSeries[] {
  const ibov = points.filter((point) => point.ibov !== null);
  return [
    {
      key: "cdi",
      label: "CDI",
      color: "var(--foreground)",
      dashed: true,
      points: points.map((point) => ({ date: point.day, value: point.cdi })),
    },
    ...(ibov.length > 0
      ? [
          {
            key: "ibov",
            label: "Ibovespa",
            color: "var(--faint-foreground)",
            dotted: true,
            points: ibov.map((point) => ({ date: point.day, value: point.ibov as string })),
          },
        ]
      : []),
    {
      key: "contributed",
      label: "Quanto foi aportado",
      color: "var(--muted-foreground)",
      muted: true,
      points: points.map((point) => ({ date: point.day, value: point.contributed })),
    },
  ];
}
