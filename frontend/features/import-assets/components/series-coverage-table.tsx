import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { seriesCoverageOptions } from "@/shared/lib/queries/seriesCoverageOptions";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { SeriesCoverage } from "@/types";
import { CoverageBar, type TimelineRange } from "./coverage-bar";

const STALE_AFTER_DAYS = 2;
const DAY_MS = 1000 * 60 * 60 * 24;

// Ação cujo último preço tem mais de 2 dias: o pregão de ontem já devia estar lá
function isOutdatedStock(series: SeriesCoverage): boolean {
  if (series.kind !== "STOCK") return false;
  if (!series.real_end) return true;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return (today.getTime() - parseLocalDate(series.real_end).getTime()) / DAY_MS > STALE_AFTER_DAYS;
}

// Intervalo comum das barras: do início mais antigo ao fim mais recente
function timelineRange(series: SeriesCoverage[]): TimelineRange {
  const dates = series
    .flatMap((s) => [s.start, s.generated_end ?? s.real_end])
    .filter((d): d is string => !!d)
    .map((d) => parseLocalDate(d).getTime());
  return { start: Math.min(...dates), end: Math.max(...dates) };
}

function formatDay(isoDate: string | null): string {
  return isoDate ? displayDate(parseLocalDate(isoDate)) : "—";
}

export function SeriesCoverageTable() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery(seriesCoverageOptions());

  const invalidateCoverage = () => queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() });

  const stockMutation = useApiMutation({
    mutationFn: (ticker: string) =>
      apiFetch("/api/import-assets/yfinance", { method: "POST", body: { ticker, overwrite: false } }),
    onSettled: invalidateCoverage,
  });
  const stockBatchMutation = useApiMutation({
    mutationFn: (tickers: string[]) =>
      apiFetch("/api/import-assets/yfinance/batch", { method: "POST", body: { tickers, overwrite: false } }),
    onSettled: invalidateCoverage,
  });
  const indicatorMutation = useApiMutation({
    mutationFn: (series: string) => apiFetch(`/api/import-assets/indicators/${series}`, { method: "POST" }),
    onSettled: invalidateCoverage,
  });
  const allIndicatorsMutation = useApiMutation({
    mutationFn: () => apiFetch("/api/import-assets/indicators", { method: "POST" }),
    onSettled: invalidateCoverage,
  });

  const [updatingKeys, setUpdatingKeys] = useState<Set<string>>(new Set());
  const [updatingAll, setUpdatingAll] = useState(false);

  const series = data ?? [];
  const range = timelineRange(series);

  async function updateSeries(item: SeriesCoverage) {
    setUpdatingKeys((prev) => new Set(prev).add(item.key));
    const toastId = toast.loading(`Atualizando ${item.name}...`);
    try {
      if (item.kind === "INDICATOR") {
        await indicatorMutation.mutateAsync(item.key);
      } else {
        await stockMutation.mutateAsync(item.key);
      }
      toast.success(`${item.name} atualizado!`, { id: toastId });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : `Falha ao atualizar ${item.name}.`, { id: toastId });
    } finally {
      setUpdatingKeys((prev) => {
        const next = new Set(prev);
        next.delete(item.key);
        return next;
      });
    }
  }

  // Indicadores sempre; ações só as desatualizadas
  async function updateAll() {
    setUpdatingAll(true);
    const outdatedTickers = series.filter(isOutdatedStock).map((s) => s.key);
    const toastId = toast.loading("Atualizando indicadores e ações desatualizadas...");
    try {
      await allIndicatorsMutation.mutateAsync();
      if (outdatedTickers.length > 0) {
        await stockBatchMutation.mutateAsync(outdatedTickers);
      }
      toast.success("Séries atualizadas!", { id: toastId });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao atualizar as séries.", { id: toastId });
    } finally {
      setUpdatingAll(false);
    }
  }

  const isBusy = updatingAll || updatingKeys.size > 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <div>
          <CardTitle className="text-xl">Séries da base</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            Depois do fim do dado real, a partida usa o último valor conhecido de cada série.
          </p>
        </div>
        <Button variant="warning" size="sm" disabled={isBusy} onClick={updateAll}>
          {updatingAll ? "Atualizando..." : "Atualizar todos"}
        </Button>
      </CardHeader>

      <CardContent className="overflow-x-auto pt-0">
        {isLoading && <p className="text-sm text-muted-foreground py-6 text-center">Carregando...</p>}

        {!isLoading && (
          <Table>
            <TableHeader>
              <TableRow>
                {["Série", "Início", "Fim do dado real", "Fim do dado gerado", "Linha do tempo", "Ação"].map((h) => (
                  <TableHead key={h} className="text-center">
                    {h}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>

            <TableBody>
              {series.map((item) => {
                const outdated = isOutdatedStock(item);
                const updating = updatingKeys.has(item.key);

                return (
                  <TableRow key={`${item.kind}-${item.key}`} className="text-center [&>td]:py-3">
                    <TableCell className="text-left">
                      <div className="flex items-center gap-2">
                        <Badge variant={item.kind === "INDICATOR" ? "default" : "secondary"}>
                          {item.kind === "INDICATOR" ? "Indicador" : "Ação"}
                        </Badge>
                        <span className={outdated ? "font-medium text-destructive" : "font-medium"}>{item.key}</span>
                        {item.name !== item.key && <span className="text-muted-foreground text-xs">{item.name}</span>}
                      </div>
                    </TableCell>
                    <TableCell>{formatDay(item.start)}</TableCell>
                    <TableCell className={outdated ? "text-destructive" : ""}>{formatDay(item.real_end)}</TableCell>
                    <TableCell>{formatDay(item.generated_end)}</TableCell>
                    <TableCell>
                      <CoverageBar series={item} range={range} />
                    </TableCell>
                    <TableCell>
                      <Button
                        variant={outdated ? "warning" : "outline"}
                        size="sm"
                        disabled={updating || updatingAll}
                        onClick={() => updateSeries(item)}
                      >
                        {updating ? "Atualizando..." : "Atualizar"}
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
