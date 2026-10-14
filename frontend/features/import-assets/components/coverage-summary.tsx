import { Card, CardContent } from "@/shared/components/ui/card";
import { isOutdatedStock } from "@/shared/lib/series-coverage";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { SeriesCoverage } from "@/types";

const formatIso = (iso: string) => displayDate(parseLocalDate(iso));

/** Os três números do topo: o período que vale pra todos, o que há na base e o que pede atenção. */
export function CoverageSummary({ series }: { series: SeriesCoverage[] }) {
  const withData = series.filter((s) => s.start && s.real_end);
  // O período comum começa no início mais tardio e acaba no fim real mais cedo
  const latestStart = withData.reduce<SeriesCoverage | undefined>(
    (acc, s) => (!acc || (s.start as string) > (acc.start as string) ? s : acc),
    undefined,
  );
  const earliestEnd = withData.reduce<SeriesCoverage | undefined>(
    (acc, s) => (!acc || (s.real_end as string) < (acc.real_end as string) ? s : acc),
    undefined,
  );

  const indicators = series.filter((s) => s.kind === "INDICATOR").length;
  const stocks = series.length - indicators;
  const outdated = series.filter(isOutdatedStock).length;
  const unclassified = series.filter((s) => s.kind === "STOCK" && !s.segment).length;

  const stats = [
    {
      label: "Período com dado real pra todos",
      value:
        latestStart && earliestEnd ? (
          <span className="font-mono">
            {formatIso(latestStart.start as string)} → {formatIso(earliestEnd.real_end as string)}
          </span>
        ) : (
          "—"
        ),
      detail:
        latestStart && earliestEnd
          ? `Limitado por ${latestStart.key} (início) e ${earliestEnd.key} (fim)`
          : "Base sem dado",
    },
    {
      label: "Na base",
      value: `${indicators} ${indicators === 1 ? "indicador" : "indicadores"} · ${stocks} ${stocks === 1 ? "ativo" : "ativos"}`,
      detail: "Indicadores do Banco Central e ações da B3",
    },
    {
      label: "Precisam de atenção",
      value: `${outdated} ${outdated === 1 ? "desatualizada" : "desatualizadas"} · ${unclassified} sem setor`,
      detail: earliestEnd
        ? `Partidas depois de ${formatIso(earliestEnd.real_end as string)} repetem o preço de ${earliestEnd.key}`
        : "Nada pra ver aqui",
    },
  ];

  return (
    <div className="grid gap-3 md:grid-cols-3">
      {stats.map((stat) => (
        <Card key={stat.label} size="sm">
          <CardContent>
            <div className="grid gap-1">
              <span className="text-xs font-medium text-muted-foreground">{stat.label}</span>
              <span className="text-[17px] font-semibold">{stat.value}</span>
              <span className="text-xs text-muted-foreground">{stat.detail}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
