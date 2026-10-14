import type { ReactNode } from "react";
import { Avatar, AvatarFallback } from "@/shared/components/ui/avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { ErrorState } from "@/shared/components/error-state";
import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import type ApiError from "@/shared/lib/models/ApiError";
import type { MetricInfo } from "@/shared/lib/metric-info";
import type { PlayerRef } from "@/types";
import { displayMetric } from "../../lib/metrics";
import { playerLabel } from "../../lib/player-label";

export interface ReportProps {
  simulationIds: number[];
  showSimulation: boolean;
  currentPlayerName?: string;
}

/** Aba sem dados: esqueleto enquanto carrega; com erro, só ela falha e oferece tentar de novo. */
export function TabStatus({
  loading,
  title,
  error,
  onRetry,
}: {
  loading: boolean;
  title: string;
  error?: ApiError | null;
  onRetry?: () => void;
}) {
  if (loading) {
    return (
      <div className="grid gap-5">
        <Skeleton className="h-32" />
        <Skeleton className="h-72" />
      </div>
    );
  }
  return (
    <Card>
      <CardContent>
        <ErrorState
          title={`Não deu pra carregar ${title}`}
          description="As outras abas continuam funcionando."
          error={error}
          onRetry={onRetry}
        />
      </CardContent>
    </Card>
  );
}

/** Card de gráfico com o nome da métrica, a dica e a descrição curta. */
export function ChartCard({
  metric,
  description,
  action,
  children,
}: {
  metric: MetricInfo;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-1">
            {metric.label}
            <MetricHint metric={metric} />
          </span>
        </CardTitle>
        <CardDescription>{description ?? metric.description}</CardDescription>
        {action && <CardAction>{action}</CardAction>}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

/** Avatar na cor do jogador, o nome e a marca de quem está vendo. */
export function PlayerCell({ label, color, isYou }: { label: string; color: string; isYou: boolean }) {
  return (
    <span className="flex items-center gap-2">
      <Avatar size="sm">
        <AvatarFallback color={color}>{label.charAt(0).toUpperCase()}</AvatarFallback>
      </Avatar>
      {label}
      {isYou && (
        <Badge variant="info" size="sm">
          você
        </Badge>
      )}
    </span>
  );
}

/** Escolhe um jogador quando o card mostra um por vez; com um jogador só, some. */
export function PlayerToggle({
  labels,
  current,
  onSelect,
  colorOf,
}: {
  labels: string[];
  current: string | undefined;
  onSelect: (label: string) => void;
  colorOf: (label: string) => string;
}) {
  if (labels.length < 2) return null;
  return (
    <ToggleGroup
      variant="segmented"
      aria-label="Jogador"
      value={current ? [current] : []}
      onValueChange={(values) => values[0] && onSelect(values[0])}
    >
      {labels.map((label) => (
        <ToggleGroupItem key={label} value={label}>
          <span className="size-2 rounded-full" style={{ backgroundColor: colorOf(label) }} aria-hidden="true" />
          {label}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}

export interface MetricColumn<T> {
  metric: MetricInfo;
  value: (row: T) => string | number | null | undefined;
  /** Destaca o melhor da sala: o maior ou o menor valor da coluna */
  best?: "max" | "min";
  tone?: (row: T) => "positive" | "negative" | undefined;
}

interface MetricsTableProps<T extends PlayerRef> {
  title: string;
  description?: string;
  rows: T[];
  columns: MetricColumn<T>[];
  showSimulation: boolean;
  currentPlayerName?: string;
  colorOf: (label: string) => string;
  extraColumn?: { header: ReactNode; cell: (row: T) => ReactNode };
  footer?: ReactNode;
}

/** Uma linha por jogador e uma coluna por métrica, cada uma com a sua dica; o melhor da sala em verde. */
export function MetricsTable<T extends PlayerRef>({
  title,
  description,
  rows,
  columns,
  showSimulation,
  currentPlayerName,
  colorOf,
  extraColumn,
  footer,
}: MetricsTableProps<T>) {
  const bestOf = columns.map((column) => {
    if (!column.best || rows.length < 2) return null;
    const values = rows
      .map((r) => column.value(r))
      .filter((v) => v !== null && v !== undefined)
      .map(Number);
    if (!values.length) return null;
    return column.best === "max" ? Math.max(...values) : Math.min(...values);
  });

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Jogador</TableHead>
            {extraColumn && <TableHead>{extraColumn.header}</TableHead>}
            {columns.map((column) => (
              <TableHead key={column.metric.label} numeric>
                <MetricLabel metric={column.metric} />
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => {
            const label = playerLabel(row, showSimulation);
            const isYou = row.player_nickname === currentPlayerName;
            return (
              <TableRow key={playerLabel(row, true)} variant={isYou ? "current" : "default"}>
                <TableCell>
                  <PlayerCell label={label} color={colorOf(label)} isYou={isYou} />
                </TableCell>
                {extraColumn && <TableCell>{extraColumn.cell(row)}</TableCell>}
                {columns.map((column, i) => {
                  const value = column.value(row);
                  const best =
                    bestOf[i] !== null && value !== null && value !== undefined && Number(value) === bestOf[i];
                  const tone = column.tone?.(row);
                  return (
                    <TableCell key={column.metric.label} numeric>
                      {best ? (
                        <Badge variant="success">{displayMetric(column.metric, value)}</Badge>
                      ) : (
                        <span
                          className={
                            tone === "negative" ? "text-destructive" : tone === "positive" ? "text-success" : undefined
                          }
                        >
                          {displayMetric(column.metric, value)}
                        </span>
                      )}
                    </TableCell>
                  );
                })}
              </TableRow>
            );
          })}
          {footer}
        </TableBody>
      </Table>
    </Card>
  );
}
