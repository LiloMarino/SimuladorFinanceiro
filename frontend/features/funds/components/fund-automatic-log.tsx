import { Bot } from "lucide-react";
import { ErrorState } from "@/shared/components/error-state";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { ACTION_TONE, actionLabel, rowPrice, rowQuantity } from "@/shared/lib/strategy-orders";
import { displayDayMonth, displayMoney } from "@/shared/lib/utils/display";
import type { FundDetails, StrategyLogRow } from "@/types";
import { useFundStrategies } from "../hooks/queries/useFundStrategies";
import { useFundStrategy } from "../hooks/queries/useFundStrategy";
import { useFundStrategyLog } from "../hooks/queries/useFundStrategyLog";

const LAST_ORDERS = 8;

const orderValue = (row: StrategyLogRow) =>
  row.quantity !== null && row.price !== null ? displayMoney(Number(row.quantity) * Number(row.price)) : "—";

/** O que o automático fez pela carteira da gestora: as últimas ordens com o motivo de cada uma. */
export function FundAutomaticLog({ fund }: { fund: FundDetails }) {
  const mine = useFundStrategy(fund.id);
  const strategies = useFundStrategies();
  const log = useFundStrategyLog(fund.id, LAST_ORDERS, fund.automatic);

  const active = mine.data?.active ?? null;
  const name = strategies.data?.find((strategy) => strategy.key === active?.key)?.name;
  const rows = log.data?.items.filter((row) => row.kind === "order") ?? [];

  return (
    <Card>
      {/* Título */}
      <CardHeader>
        <CardTitle>O que o automático fez</CardTitle>
        <CardDescription>
          {name ?? "A estratégia"}
          {active ? `, desde ${displayDayMonth(active.since)}` : ""}
        </CardDescription>
      </CardHeader>

      {/* Ordens */}
      {log.error ? (
        <CardContent>
          <ErrorState title="Não deu para carregar as ordens" error={log.error} onRetry={() => void log.refetch()} />
        </CardContent>
      ) : log.isLoading ? (
        <CardContent>
          <Skeleton className="h-24" aria-busy="true" aria-label="Carregando as ordens" />
        </CardContent>
      ) : rows.length === 0 ? (
        <CardContent>
          <Empty variant="dashed">
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <Bot />
              </EmptyMedia>
              <EmptyTitle>Nenhuma ordem ainda</EmptyTitle>
              <EmptyDescription>
                Quando a estratégia operar a carteira, cada ordem aparece aqui, com o motivo.
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
        </CardContent>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Data</TableHead>
              <TableHead>Operação</TableHead>
              <TableHead>Ativo</TableHead>
              <TableHead numeric>Quantidade</TableHead>
              <TableHead numeric>Preço</TableHead>
              <TableHead numeric>Valor</TableHead>
              <TableHead>Por quê</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.id}>
                <TableCell>
                  <span className="font-mono text-muted-foreground">{displayDayMonth(row.event_date)}</span>
                </TableCell>
                <TableCell>
                  <b className={`font-semibold ${row.action ? ACTION_TONE[row.action] : ""}`}>
                    {row.action ? actionLabel(row.action) : "—"}
                  </b>
                </TableCell>
                <TableCell>
                  {row.ticker ? (
                    <Badge variant="secondary" size="tag" numeric>
                      {row.ticker}
                    </Badge>
                  ) : (
                    (row.asset_name ?? "—")
                  )}
                </TableCell>
                <TableCell numeric>{rowQuantity(row)}</TableCell>
                <TableCell numeric>{rowPrice(row)}</TableCell>
                <TableCell numeric>{orderValue(row)}</TableCell>
                <TableCell className="whitespace-normal">
                  <span className="text-secondary-foreground">{row.reason}</span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Card>
  );
}
