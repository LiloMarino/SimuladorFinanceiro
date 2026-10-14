import { Fragment, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { RefreshCw, TriangleAlert } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Spinner } from "@/shared/components/ui/spinner";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { queryKeys } from "@/shared/lib/queryKeys";
import { isOutdatedStock } from "@/shared/lib/series-coverage";
import { cn } from "@/shared/lib/utils";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { AssetClass, SeriesCoverage } from "@/types";
import { timelineRange, timelineTicks } from "../lib/timeline";
import { ClassifyRow } from "./classify-row";
import { CoverageBar } from "./coverage-bar";

const ASSET_CLASS_LABELS: Record<AssetClass, string> = {
  STOCK: "Ação",
  FII: "FII",
  ETF: "ETF",
  BDR: "BDR",
};

const COLUMNS = 5;

type Filter = "ALL" | "ATTENTION";

const needsAttention = (s: SeriesCoverage) => !s.real_end || isOutdatedStock(s) || (s.kind === "STOCK" && !s.segment);

type SeriesTableProps = {
  series: SeriesCoverage[];
  classifying: string | null;
  onClassify: (key: string | null) => void;
};

/** As séries da base num eixo de tempo comum, com a situação de cada uma. */
export function SeriesTable({ series, classifying, onClassify }: SeriesTableProps) {
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<Filter>("ALL");
  const invalidateCoverage = () => queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() });

  const refreshOne = useApiMutation({
    mutationFn: (item: SeriesCoverage) =>
      item.kind === "INDICATOR"
        ? apiFetch(`/api/import-assets/indicators/${item.key}`, { method: "POST" })
        : apiFetch("/api/import-assets/yfinance", { method: "POST", body: { ticker: item.key, overwrite: false } }),
    onError: (err) => toastApiError(err),
    onSettled: invalidateCoverage,
  });
  const refreshOutdated = useApiMutation({
    mutationFn: (tickers: string[]) =>
      apiFetch("/api/import-assets/yfinance/batch", { method: "POST", body: { tickers, overwrite: false } }),
    onError: (err) => toastApiError(err),
    onSettled: invalidateCoverage,
  });
  const assetClass = useApiMutation({
    mutationFn: ({ ticker, value }: { ticker: string; value: AssetClass }) =>
      apiFetch(`/api/import-assets/stocks/${ticker}/asset-class`, { method: "PUT", body: { asset_class: value } }),
    onError: (err) => toastApiError(err),
    onSettled: invalidateCoverage,
  });

  const range = timelineRange(series);
  const ticks = timelineTicks(range);
  const outdated = series.filter(isOutdatedStock);
  const attentionCount = series.filter(needsAttention).length;
  const visible = filter === "ATTENTION" ? series.filter(needsAttention) : series;
  const groups = [
    { label: "Indicadores · Banco Central e B3", items: visible.filter((s) => s.kind === "INDICATOR") },
    { label: "Ativos", items: visible.filter((s) => s.kind === "STOCK") },
  ].filter((g) => g.items.length > 0);

  const busy = refreshOne.isPending || refreshOutdated.isPending;

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

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Série</TableHead>
            <TableHead>Setor · segmento</TableHead>
            <TableHead className="w-full min-w-56">
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
            </TableHead>
            <TableHead>Situação</TableHead>
            <TableHead>
              <span className="sr-only">Ações</span>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {groups.map((group) => (
            <Fragment key={group.label}>
              <TableRow variant="group">
                <TableCell colSpan={COLUMNS}>
                  <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
                    {group.label}
                  </span>
                </TableCell>
              </TableRow>
              {group.items.map((item) => {
                const stale = isOutdatedStock(item);
                return (
                  <Fragment key={`${item.kind}-${item.key}`}>
                    <TableRow variant={stale ? "warning" : "default"}>
                      {/* Série */}
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="grid">
                            <span className={cn("font-mono font-semibold", stale && "text-destructive")}>
                              {item.key}
                            </span>
                            {item.name !== item.key && (
                              <span className="max-w-40 truncate text-xs text-muted-foreground" title={item.name}>
                                {item.name}
                              </span>
                            )}
                          </div>
                          {item.asset_class && (
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
                          )}
                        </div>
                      </TableCell>

                      {/* Setor · segmento */}
                      <TableCell>
                        {item.kind === "INDICATOR" ? (
                          <span className="text-faint-foreground">—</span>
                        ) : item.segment ? (
                          <Button
                            variant="link"
                            size="xs"
                            title={`${item.segment.sector} · ${item.segment.segment}`}
                            onClick={() => onClassify(item.key)}
                          >
                            <span className="max-w-40 truncate">
                              {item.segment.sector} · {item.segment.segment}
                            </span>
                          </Button>
                        ) : (
                          <span className="flex items-center gap-2">
                            <Badge variant="secondary" size="sm">
                              Sem setor
                            </Badge>
                            <Button variant="link" size="xs" onClick={() => onClassify(item.key)}>
                              Classificar
                            </Button>
                          </span>
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
                        ) : (
                          <Badge variant="success">● Em dia</Badge>
                        )}
                      </TableCell>

                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon-sm"
                          aria-label={`Atualizar ${item.key}`}
                          disabled={busy}
                          onClick={() => refreshOne.mutate(item)}
                        >
                          {refreshOne.isPending && refreshOne.variables?.key === item.key ? <Spinner /> : <RefreshCw />}
                        </Button>
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
