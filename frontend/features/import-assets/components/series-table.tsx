import { Fragment, useState } from "react";
import { ChevronDown, Eraser, RefreshCw, TriangleAlert } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Spinner } from "@/shared/components/ui/spinner";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { GROWTH, UNEMPLOYMENT } from "@/shared/lib/budget-metrics";
import type { MetricInfo } from "@/shared/lib/metric-info";
import { isOutdatedStock } from "@/shared/lib/series-coverage";
import { cn } from "@/shared/lib/utils";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { AssetClass, SeriesCoverage } from "@/types";
import { useChangeAssetClass } from "../hooks/mutations/useChangeAssetClass";
import { useCorrectPriceErrors } from "../hooks/mutations/useCorrectPriceErrors";
import { useRefreshOutdatedStocks } from "../hooks/mutations/useRefreshOutdatedStocks";
import { useRefreshSeries } from "../hooks/mutations/useRefreshSeries";
import { timelineRange, timelineTicks } from "../lib/timeline";
import { ClassifyRow } from "./classify-row";
import { CorrectedDaysHint } from "./corrected-days-hint";
import { CoverageBar } from "./coverage-bar";
import { DeleteStockButton } from "./delete-stock-button";
import { TruncatedText } from "./truncated-text";
import { MetricHint } from "@/shared/components/metric-hint";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";

const ASSET_CLASS_LABELS: Record<AssetClass, string> = {
  STOCK: "Ação",
  FII: "FII",
  ETF: "ETF",
  BDR: "BDR",
  CRYPTO: "Cripto",
};

const COLUMNS = 6;

// O que cada série da economia do país mede, na dica ao lado do nome
const MACRO_HINTS: Record<string, MetricInfo> = { GDP_GROWTH: GROWTH, UNEMPLOYMENT: UNEMPLOYMENT };

type Filter = "ALL" | "ATTENTION";

const needsAttention = (s: SeriesCoverage) => !s.real_end || isOutdatedStock(s) || (s.kind === "STOCK" && !s.segment);

type SeriesTableProps = {
  series: SeriesCoverage[];
  classifying: string | null;
  onClassify: (key: string | null) => void;
};

/** As séries da base num eixo de tempo comum, com a situação de cada uma. */
export function SeriesTable({ series, classifying, onClassify }: SeriesTableProps) {
  const [filter, setFilter] = useState<Filter>("ALL");

  const refreshOne = useRefreshSeries();
  const refreshOutdated = useRefreshOutdatedStocks();
  const correctErrors = useCorrectPriceErrors();
  const assetClass = useChangeAssetClass();

  const range = timelineRange(series);
  const ticks = timelineTicks(range);
  const outdated = series.filter(isOutdatedStock);
  const attentionCount = series.filter(needsAttention).length;
  const sorting = useTableSort(filter === "ATTENTION" ? series.filter(needsAttention) : series, {
    series: (s) => s.key,
    assetClass: (s) => (s.asset_class ? ASSET_CLASS_LABELS[s.asset_class] : null),
    sector: (s) => (s.segment ? `${s.segment.sector} · ${s.segment.segment}` : null),
    end: (s) => s.real_end,
    status: (s) =>
      !s.real_end
        ? "Sem dado"
        : isOutdatedStock(s)
          ? `Parou em ${s.real_end}`
          : s.kind === "STOCK" && !s.segment
            ? "Sem setor"
            : "Em dia",
  });
  const visible = sorting.rows;
  const groups = [
    { label: "Indicadores · Banco Central e B3", items: visible.filter((s) => s.kind === "INDICATOR") },
    { label: "Economia do país · IBGE via Banco Central", items: visible.filter((s) => s.kind === "MACRO") },
    { label: "Ativos", items: visible.filter((s) => s.kind === "STOCK") },
  ].filter((g) => g.items.length > 0);

  const busy = refreshOne.isPending || refreshOutdated.isPending || correctErrors.isPending;
  const updatingThis = (item: SeriesCoverage) => refreshOne.isPending && refreshOne.variables.key === item.key;

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Séries da base</CardTitle>
        <CardDescription>{series.length} séries · a linha mostra até onde vai o dado real de cada uma</CardDescription>
        <CardAction>
          <div className="flex items-center gap-2">
            <ToggleGroup
              variant="segmented"
              aria-label="Filtrar séries"
              value={[filter]}
              onValueChange={(values) => values[0] && setFilter(values[0] as Filter)}
            >
              <ToggleGroupItem value="ALL">Todas</ToggleGroupItem>
              <ToggleGroupItem value="ATTENTION">Precisam de atenção · {attentionCount}</ToggleGroupItem>
            </ToggleGroup>
            <Button size="sm" variant="outline" disabled={busy} onClick={() => correctErrors.mutate()}>
              {correctErrors.isPending ? <Spinner /> : <Eraser />}
              Corrigir erros de dado
            </Button>
            <Button
              size="sm"
              disabled={busy || outdated.length === 0}
              onClick={() => refreshOutdated.mutate(outdated.map((s) => s.key))}
            >
              {refreshOutdated.isPending ? <Spinner /> : <RefreshCw />}
              Atualizar desatualizadas ({outdated.length})
            </Button>
          </div>
        </CardAction>
      </CardHeader>

      <Table className="table-fixed">
        <TableHeader>
          <TableRow className="*:align-top">
            <SortableTableHead label="Série" {...sorting.header("series")} className="w-[18%]" />
            <SortableTableHead label="Classe" {...sorting.header("assetClass")} className="w-24" />
            <SortableTableHead label="Setor · segmento" {...sorting.header("sector")} className="w-[16%]" />
            <SortableTableHead label="Dados reais até" {...sorting.header("end")}>
              {/* Eixo comum da linha do tempo */}
              <div className="relative h-4">
                {ticks.map((tick) => (
                  <span
                    key={tick.label}
                    className="absolute -translate-x-1/2 font-mono"
                    style={{ left: `${tick.position}%` }}
                  >
                    {tick.label}
                  </span>
                ))}
                <span className="absolute right-0">hoje</span>
              </div>
            </SortableTableHead>
            <SortableTableHead label="Situação" {...sorting.header("status")} className="w-44" />
            <TableHead className="w-40">
              <span className="sr-only">Ações</span>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {groups.length === 0 && (
            <TableEmptyRow colSpan={COLUMNS}>
              <span className="text-muted-foreground">Nenhuma série precisa de atenção.</span>
            </TableEmptyRow>
          )}
          {groups.map((group) => (
            <Fragment key={group.label}>
              <TableRow variant="group">
                <TableCell colSpan={COLUMNS}>
                  <span className="text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">
                    {group.label}
                  </span>
                </TableCell>
              </TableRow>
              {group.items.map((item) => {
                const stale = isOutdatedStock(item);
                const hint = MACRO_HINTS[item.key];
                return (
                  <Fragment key={`${item.kind}-${item.key}`}>
                    <TableRow variant={stale ? "warning" : "default"} className="h-15.5">
                      {/* Série */}
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="grid min-w-0 flex-1">
                            <TruncatedText className={cn("font-mono font-semibold", stale && "text-destructive")}>
                              {item.key}
                            </TruncatedText>
                            {item.name !== item.key && (
                              <TruncatedText className="text-xs text-muted-foreground">{item.name}</TruncatedText>
                            )}
                          </div>
                          {hint && <MetricHint metric={hint} />}
                          <CorrectedDaysHint days={item.corrected_days} />
                        </div>
                      </TableCell>

                      {/* Classe */}
                      <TableCell>
                        {item.asset_class ? (
                          <Select
                            items={ASSET_CLASS_LABELS}
                            value={item.asset_class}
                            disabled={assetClass.isPending}
                            onValueChange={(value) =>
                              assetClass.mutate({ ticker: item.key, value: value as AssetClass })
                            }
                          >
                            <SelectTrigger size="sm" aria-label={`Classe de ${item.key}`}>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {Object.entries(ASSET_CLASS_LABELS).map(([value, label]) => (
                                <SelectItem key={value} value={value}>
                                  {label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        ) : (
                          <span className="text-faint-foreground">—</span>
                        )}
                      </TableCell>

                      {/* Setor · segmento */}
                      <TableCell>
                        {item.kind !== "STOCK" ? (
                          <span className="text-faint-foreground">—</span>
                        ) : item.segment ? (
                          <button
                            type="button"
                            onClick={() => onClassify(item.key)}
                            className="flex max-w-full items-start gap-1.5 text-left"
                          >
                            <span className="grid min-w-0">
                              <TruncatedText className="text-[13px]">{item.segment.sector}</TruncatedText>
                              <TruncatedText className="text-xs text-muted-foreground">
                                {item.segment.segment}
                              </TruncatedText>
                            </span>
                            <ChevronDown className="mt-0.5 size-3.5 shrink-0 text-faint-foreground" />
                          </button>
                        ) : (
                          <button
                            type="button"
                            onClick={() => onClassify(item.key)}
                            className="flex items-center gap-1.5 text-[13px] font-medium text-warning"
                          >
                            Classificar
                            <ChevronDown className="size-3.5 shrink-0" />
                          </button>
                        )}
                      </TableCell>

                      <TableCell>
                        <CoverageBar series={item} range={range} />
                      </TableCell>

                      {/* Situação */}
                      <TableCell>
                        {!item.real_end ? (
                          <Badge variant="destructive">Sem dado</Badge>
                        ) : stale ? (
                          <Badge variant="warning">
                            <TriangleAlert />
                            Parou em {displayDate(parseLocalDate(item.real_end))}
                          </Badge>
                        ) : item.kind === "STOCK" && !item.segment ? (
                          <Badge variant="secondary">Sem setor</Badge>
                        ) : (
                          <Badge variant="success">● Em dia</Badge>
                        )}
                      </TableCell>

                      <TableCell>
                        <div className="flex items-center justify-end gap-1">
                          {/* Só a linha desatualizada pede a ação por extenso */}
                          {stale ? (
                            <Button variant="outline" size="sm" disabled={busy} onClick={() => refreshOne.mutate(item)}>
                              {updatingThis(item) ? <Spinner /> : <RefreshCw />}
                              Atualizar
                            </Button>
                          ) : (
                            <Button
                              variant="ghost"
                              size="icon-sm"
                              aria-label={`Atualizar ${item.key}`}
                              disabled={busy}
                              onClick={() => refreshOne.mutate(item)}
                            >
                              {updatingThis(item) ? <Spinner /> : <RefreshCw />}
                            </Button>
                          )}
                          {item.kind === "STOCK" && <DeleteStockButton stock={item} disabled={busy} />}
                        </div>
                      </TableCell>
                    </TableRow>

                    {classifying === item.key && (
                      <ClassifyRow series={item} columns={COLUMNS} onClose={() => onClassify(null)} />
                    )}
                  </Fragment>
                );
              })}
            </Fragment>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}
