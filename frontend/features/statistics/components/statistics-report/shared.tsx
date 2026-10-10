import type { ReactNode } from "react";
import { Spinner } from "@/shared/components/ui/spinner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import type { PlayerRef } from "@/types";
import { playerLabel } from "../../lib/player-label";
import { displayMetric, type MetricInfo } from "../../lib/metrics";
import { MetricHint, MetricLabel } from "./metric-hint";

export interface ReportProps {
  simulationIds: number[];
  showSimulation: boolean;
  currentPlayerName?: string;
}

export function TabStatus({ loading }: { loading: boolean }) {
  return (
    <div className="flex h-72 items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
      {loading ? <Spinner className="size-6" /> : "Erro ao carregar as estatísticas."}
    </div>
  );
}

interface ChartCardProps {
  metric: MetricInfo;
  description?: string;
  children: ReactNode;
}

/** Card de gráfico com o nome da métrica, a dica e a descrição curta. */
export function ChartCard({ metric, description, children }: ChartCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-1">
          {metric.label}
          <MetricHint metric={metric} />
        </CardTitle>
        <CardDescription>{description ?? metric.description}</CardDescription>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

export interface MetricColumn<T> {
  metric: MetricInfo;
  value: (row: T) => string | number | null | undefined;
  className?: (row: T) => string;
}

interface MetricsTableProps<T extends PlayerRef> {
  title: string;
  rows: T[];
  columns: MetricColumn<T>[];
  showSimulation: boolean;
  currentPlayerName?: string;
  footer?: ReactNode;
}

/** Uma linha por jogador e uma coluna por métrica, cada uma com a sua dica. */
export function MetricsTable<T extends PlayerRef>({
  title,
  rows,
  columns,
  showSimulation,
  currentPlayerName,
  footer,
}: MetricsTableProps<T>) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Jogador</TableHead>
              {columns.map((column) => (
                <TableHead key={column.metric.label} className="text-center">
                  <MetricLabel metric={column.metric} />
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow
                key={playerLabel(row, true)}
                className={row.player_nickname === currentPlayerName ? "bg-primary/5 font-semibold" : ""}
              >
                <TableCell>{playerLabel(row, showSimulation)}</TableCell>
                {columns.map((column) => (
                  <TableCell key={column.metric.label} className={`text-center ${column.className?.(row) ?? ""}`}>
                    {displayMetric(column.metric, column.value(row))}
                  </TableCell>
                ))}
              </TableRow>
            ))}
            {footer}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
