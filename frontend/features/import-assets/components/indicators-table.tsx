import { Fragment } from "react";
import { Info, RefreshCw } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Spinner } from "@/shared/components/ui/spinner";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { GROWTH, UNEMPLOYMENT } from "@/shared/lib/budget-metrics";
import type { MetricInfo } from "@/shared/lib/metric-info";
import type { SeriesCoverage } from "@/types";
import { useDownloadIndicators } from "../hooks/mutations/useDownloadIndicators";
import { useRefreshSeries } from "../hooks/mutations/useRefreshSeries";
import { FED_FUNDS_HINT } from "../lib/fed-metrics";
import { FOCUS_HINTS, FOCUS_IMPORT_NOTE } from "../lib/focus-metrics";
import { SERIES_DESCRIPTIONS } from "../lib/series-descriptions";
import type { TimelineRange } from "../lib/timeline";
import { CoverageBar, CoverageDates } from "./coverage-bar";
import { CoverageLegend, Swatch } from "./coverage-legend";
import { SeriesName } from "./series-name";
import { SeriesStatus } from "./series-status";
import { TimelineAxis } from "./timeline-axis";

const COLUMNS = 5;

// O que cada série da economia do país e do Focus mede, na dica ao lado do nome
const SERIES_HINTS: Record<string, MetricInfo> = {
  GDP_GROWTH: GROWTH,
  UNEMPLOYMENT: UNEMPLOYMENT,
  FED_FUNDS: FED_FUNDS_HINT,
  ...FOCUS_HINTS,
};

type Group = {
  kind: SeriesCoverage["kind"];
  label: string;
  /** A regra do que a partida faz depois do último dado, no cabeçalho do grupo */
  rule?: { text: string; swatch: "repeat" | "computed" };
};

const GROUPS: Group[] = [
  {
    kind: "INDICATOR",
    label: "Indicadores · Banco Central e B3",
    rule: { text: "Ganham futuro gerado. Sem ele, a partida repete o último valor", swatch: "repeat" },
  },
  {
    kind: "MACRO",
    label: "Economia do país · IBGE via Banco Central",
    rule: {
      text: "Depois do último dado, a partida calcula a partir da SELIC, do IPCA e da bolsa",
      swatch: "computed",
    },
  },
  { kind: "EXPECTATION", label: "Expectativas do mercado · Focus do Banco Central" },
];

type IndicatorsTableProps = {
  /** Indicadores, economia do país e Focus; os ativos têm a tabela deles */
  series: SeriesCoverage[];
  range: TimelineRange;
};

/** A linha de baixo do nome: o que o indicador é e, na economia do país, a exceção que ganha futuro gerado. */
function noteOf(item: SeriesCoverage): string | undefined {
  if (item.kind === "MACRO" && item.has_generated_future) return "exceção do grupo: ganha futuro gerado";
  return SERIES_DESCRIPTIONS[item.key];
}

/** Os indicadores num eixo de tempo comum, em grupos que dizem o que a partida faz depois do último dado. */
export function IndicatorsTable({ series, range }: IndicatorsTableProps) {
  const refreshOne = useRefreshSeries();
  const downloadAll = useDownloadIndicators();

  const busy = refreshOne.isPending || downloadAll.isPending;
  const updatingThis = (item: SeriesCoverage) => refreshOne.isPending && refreshOne.variables.key === item.key;

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Indicadores e expectativas</CardTitle>
        <CardDescription>{series.length} séries · baixadas do Banco Central, do IBGE e da B3</CardDescription>
        <CardAction>
          <Button size="sm" disabled={busy} onClick={() => downloadAll.mutate()}>
            {downloadAll.isPending ? <Spinner /> : <RefreshCw />}
            Atualizar todas
          </Button>
        </CardAction>
      </CardHeader>

      <CoverageLegend />

      <Table className="table-fixed">
        <TableHeader>
          <TableRow>
            <TableHead>Série</TableHead>
            <TableHead className="w-44">Dados reais</TableHead>
            <TableHead className="w-[34%]">
              <TimelineAxis range={range} />
            </TableHead>
            <TableHead className="w-36">Situação</TableHead>
            <TableHead className="w-32">
              <span className="sr-only">Ações</span>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {GROUPS.map((group) => {
            const items = series.filter((s) => s.kind === group.kind);
            if (items.length === 0) return null;
            return (
              <Fragment key={group.kind}>
                {/* Cabeçalho do grupo, com a regra do depois do último dado */}
                <TableRow variant="group">
                  <TableCell colSpan={COLUMNS} wrap>
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
                      <span className="text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">
                        {group.label}
                      </span>
                      {group.rule && (
                        <span className="ml-auto inline-flex items-center gap-2 text-[13px] font-normal text-muted-foreground">
                          {group.rule.text}
                          <Swatch kind={group.rule.swatch} />
                        </span>
                      )}
                    </div>
                  </TableCell>
                </TableRow>

                {group.kind === "EXPECTATION" && (
                  <TableRow variant="info">
                    <TableCell colSpan={COLUMNS} wrap variant="info">
                      <span className="flex items-start gap-2.5">
                        <Info className="mt-0.5 size-4 shrink-0" />
                        <span>
                          <b className="font-semibold">Importadas da pesquisa Focus do Banco Central.</b> Não ganham
                          futuro gerado: a barra termina na última pesquisa. Com pesquisa de até 30 dias, a partida a
                          usa; passado isso, usa a SELIC da história como o que o mercado espera.
                        </span>
                      </span>
                    </TableCell>
                  </TableRow>
                )}

                {items.map((item) => {
                  const hint = SERIES_HINTS[item.key];
                  return (
                    <TableRow key={item.key} className="h-15.5">
                      <TableCell wrap>
                        <SeriesName
                          series={item}
                          order="name-first"
                          hint={
                            hint && (
                              <MetricHint
                                metric={hint}
                                extra={
                                  item.kind === "EXPECTATION" ? (
                                    <p className="text-muted-foreground">{FOCUS_IMPORT_NOTE}</p>
                                  ) : undefined
                                }
                              />
                            )
                          }
                          note={noteOf(item)}
                        />
                      </TableCell>
                      <TableCell>
                        <CoverageDates series={item} />
                      </TableCell>
                      <TableCell>
                        <CoverageBar series={item} range={range} />
                      </TableCell>
                      <TableCell>
                        <SeriesStatus series={item} updating={updatingThis(item)} />
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="outline"
                          size="sm"
                          aria-label={`Atualizar ${item.name}`}
                          disabled={busy}
                          onClick={() => refreshOne.mutate(item)}
                        >
                          {updatingThis(item) ? <Spinner /> : <RefreshCw />}
                          Atualizar
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </Fragment>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}
