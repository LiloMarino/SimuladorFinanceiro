import type { ReactNode } from "react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { isOutdatedStock } from "@/shared/lib/series-coverage";
import { cn } from "@/shared/lib/utils";
import { displayDecimal, displayIsoDate } from "@/shared/lib/utils/display";
import type { GeneratedFuture, SeriesCoverage } from "@/types";
import { REGIME_NAMES, withMinus } from "../lib/future-readings";
import { displayRecordedAt } from "../lib/recorded-at";

type Stat = {
  label: string;
  value: ReactNode;
  detail: ReactNode;
  variant?: "warning";
};

type CoverageSummaryProps = {
  series: SeriesCoverage[];
  /** O futuro gravado; nulo quando não há, indefinido enquanto carrega */
  future: GeneratedFuture | null | undefined;
  onGenerate: () => void;
};

/** Os números do topo: o período que vale pra todos, o que há na base, o futuro gerado e o que pede atenção. */
export function CoverageSummary({ series, future, onGenerate }: CoverageSummaryProps) {
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

  const attentionDetail = () => {
    if (future) return `Partidas depois de ${displayIsoDate(future.until)} repetem o último valor`;
    if (!earliestEnd) return "Nada pra ver aqui";
    return (
      <>
        Partidas depois de {displayIsoDate(earliestEnd.real_end as string)} repetem o preço de {earliestEnd.key}
        {future === null && (
          <>
            {" "}
            ·{" "}
            <Button variant="link" size="xs" onClick={onGenerate}>
              Gerar o futuro
            </Button>
          </>
        )}
      </>
    );
  };

  const stats: Stat[] = [
    {
      label: "Período com dado real pra todos",
      value:
        latestStart && earliestEnd ? (
          <span className="font-mono">
            {displayIsoDate(latestStart.start as string)} → {displayIsoDate(earliestEnd.real_end as string)}
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
    ...(future
      ? [
          {
            label: "Futuro gerado",
            variant: "warning" as const,
            value: <span className="font-mono">até {displayIsoDate(future.until)}</span>,
            detail: (
              <>
                Semente <span className="font-mono">{future.seed}</span> · temperatura{" "}
                {displayDecimal(future.temperature)} · começo:{" "}
                {future.start_regime ? REGIME_NAMES[future.start_regime] : "hoje"} · choque{" "}
                {withMinus(String(future.inflation_shock))}
                {future.real_advanced_until && (
                  <>
                    <br />O real chegou até {displayIsoDate(future.real_advanced_until)} depois deste futuro
                  </>
                )}
                <br />
                Gravado {displayRecordedAt(future.generated_at)} ·{" "}
                {future.real_advanced_until ? (
                  <Button variant="warning" size="xs" onClick={onGenerate}>
                    Gerar de novo
                  </Button>
                ) : (
                  <Button variant="link" size="xs" onClick={onGenerate}>
                    Gerar de novo
                  </Button>
                )}
              </>
            ),
          },
        ]
      : []),
    {
      label: "Precisam de atenção",
      value: `${outdated} ${outdated === 1 ? "desatualizada" : "desatualizadas"} · ${unclassified} sem setor`,
      detail: attentionDetail(),
    },
  ];

  return (
    <div className={cn("grid gap-3", future ? "md:grid-cols-2 xl:grid-cols-4" : "md:grid-cols-3")}>
      {stats.map((stat) => (
        <Card key={stat.label} size="sm" variant={stat.variant}>
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
