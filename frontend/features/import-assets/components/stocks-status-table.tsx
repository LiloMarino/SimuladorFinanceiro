import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Button } from "@/shared/components/ui/button";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { displayDate } from "@/shared/lib/utils/display";
import { toast } from "sonner";

interface StockStatus {
  ticker: string;
  last_date: string | null;
}

function parseLocalDate(dateStr: string): Date {
  const [year, month, day] = dateStr.split("-").map(Number);
  return new Date(year, month - 1, day);
}

function isOutdated(lastDate: string | null): boolean {
  if (!lastDate) return true;
  const last = parseLocalDate(lastDate);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diffDays = (today.getTime() - last.getTime()) / (1000 * 60 * 60 * 24);
  return diffDays > 2;
}

export function StocksStatusTable() {
  const queryClient = useQueryClient();
  const { data, isLoading: loading } = useApiQuery({
    queryKey: queryKeys.importAssetsStatus(),
    queryFn: ({ signal }) => apiFetch<StockStatus[]>("/api/import-assets/status", { signal }),
  });

  const invalidateStatus = () => queryClient.invalidateQueries({ queryKey: queryKeys.importAssetsStatus() });

  const batchMutation = useApiMutation({
    mutationFn: (payload: { tickers: string[]; overwrite: boolean }) =>
      apiFetch("/api/import-assets/yfinance/batch", { method: "POST", body: payload }),
    onSettled: invalidateStatus,
  });
  const singleMutation = useApiMutation({
    mutationFn: (payload: { ticker: string; overwrite: boolean }) =>
      apiFetch("/api/import-assets/yfinance", { method: "POST", body: payload }),
    onSettled: invalidateStatus,
  });

  const [updatingTickers, setUpdatingTickers] = useState<Set<string>>(new Set());
  const [updatingAll, setUpdatingAll] = useState(false);

  const stocks = data ?? [];
  const outdatedStocks = stocks.filter((s) => isOutdated(s.last_date));
  const anyOutdated = outdatedStocks.length > 0;

  async function updateTicker(ticker: string) {
    setUpdatingTickers((prev) => new Set(prev).add(ticker));
    const toastId = toast.loading(`Atualizando ${ticker}...`);
    try {
      await singleMutation.mutateAsync({ ticker, overwrite: false });
      toast.success(`${ticker} atualizado com sucesso!`, { id: toastId });
    } catch {
      toast.error(`Falha ao atualizar ${ticker}.`, { id: toastId });
    } finally {
      setUpdatingTickers((prev) => {
        const next = new Set(prev);
        next.delete(ticker);
        return next;
      });
    }
  }

  async function updateAll() {
    if (!anyOutdated) return;
    setUpdatingAll(true);
    const tickers = outdatedStocks.map((s) => s.ticker);
    const toastId = toast.loading(`Atualizando ${tickers.length} ativos...`);
    try {
      await batchMutation.mutateAsync({ tickers, overwrite: false });
      toast.success(`${tickers.length} ativos atualizados com sucesso!`, { id: toastId });
    } catch {
      toast.error("Falha ao atualizar ativos em lote.", { id: toastId });
    } finally {
      setUpdatingAll(false);
    }
  }

  const isBusy = updatingAll || updatingTickers.size > 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <CardTitle className="text-xl">Status dos Ativos</CardTitle>
        <Button variant="warning" size="sm" disabled={!anyOutdated || isBusy} onClick={updateAll}>
          {updatingAll ? "Atualizando..." : "Atualizar Todos"}
        </Button>
      </CardHeader>

      <CardContent className="overflow-x-auto pt-0">
        {loading && <p className="text-sm text-muted-foreground py-6 text-center">Carregando...</p>}

        {!loading && stocks.length === 0 && (
          <p className="text-sm text-muted-foreground py-6 text-center">Nenhum ativo importado ainda.</p>
        )}

        {!loading && stocks.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                {["Ativo", "Última Entrada", "Ação"].map((h) => (
                  <TableHead key={h} className="text-center">
                    {h}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>

            <TableBody>
              {stocks.map((stock) => {
                const outdated = isOutdated(stock.last_date);
                const updating = updatingTickers.has(stock.ticker);

                return (
                  <TableRow key={stock.ticker} className="text-center [&>td]:py-3">
                    <TableCell className={outdated ? "font-medium text-red-600" : ""}>{stock.ticker}</TableCell>
                    <TableCell className={outdated ? "text-red-600" : ""}>
                      {stock.last_date ? displayDate(parseLocalDate(stock.last_date)) : "—"}
                    </TableCell>
                    <TableCell>
                      {outdated ? (
                        <Button
                          variant="warning"
                          size="sm"
                          disabled={updating || updatingAll}
                          onClick={() => updateTicker(stock.ticker)}
                        >
                          {updating ? "Atualizando..." : "Atualizar"}
                        </Button>
                      ) : (
                        <span className="text-muted-foreground text-sm">—</span>
                      )}
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
