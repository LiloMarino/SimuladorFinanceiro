import { useState } from "react";
import { Bot, CircleAlert, CircleCheck, Power } from "lucide-react";
import { ErrorState } from "@/shared/components/error-state";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { StrategyAction, StrategyLogFilter, StrategyLogKind, StrategyLogRow } from "@/types";
import { useStrategyLog } from "../hooks/queries/useStrategyLog";
import { actionLabel, rowPrice, rowQuantity, STATUS_BADGE } from "../lib/strategy-display";

const FILTERS: { value: StrategyLogFilter; label: string }[] = [
  { value: "all", label: "Tudo" },
  { value: "orders", label: "Ordens" },
  { value: "modes", label: "Ligou e desligou" },
];

const ACTION_TONE: Record<StrategyAction, string> = {
  buy: "text-success",
  sell: "text-destructive",
  cancel: "text-muted-foreground",
  invest: "text-primary",
  redeem: "text-foreground",
};

const MODE_ICON: Record<Exclude<StrategyLogKind, "order">, { icon: typeof Power; tone: string }> = {
  enabled: { icon: CircleCheck, tone: "text-success" },
  switched: { icon: CircleCheck, tone: "text-success" },
  params: { icon: CircleCheck, tone: "text-success" },
  resumed: { icon: CircleCheck, tone: "text-success" },
  disabled: { icon: Power, tone: "text-muted-foreground" },
  error: { icon: CircleAlert, tone: "text-destructive" },
  error_seen: { icon: CircleCheck, tone: "text-muted-foreground" },
};

/** O registro da partida inteira: cada ordem com o motivo e as mudanças de modo. */
export function StrategyLog() {
  const [filter, setFilter] = useState<StrategyLogFilter>("all");
  const {
    data: pages,
    error,
    isLoading,
    refetch,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useStrategyLog(filter);

  const rows = pages?.flatMap((page) => page.items) ?? [];
  const total = pages?.at(-1)?.total ?? 0;

  return (
    <Card>
      {/* Título e filtro */}
      <CardHeader>
        <CardTitle>O que a estratégia fez</CardTitle>
        <CardDescription>A partida toda: cada ordem com o motivo, e quando ligou, desligou ou deu erro</CardDescription>
        <CardAction>
          <ToggleGroup
            variant="segmented"
            aria-label="Filtrar o registro"
            value={[filter]}
            onValueChange={(values) => values[0] && setFilter(values[0] as StrategyLogFilter)}
          >
            {FILTERS.map(({ value, label }) => (
              <ToggleGroupItem key={value} value={value}>
                {label}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </CardAction>
      </CardHeader>

      {/* Linhas */}
      {error ? (
        <CardContent>
          <ErrorState
            title="Não deu para carregar o registro"
            description="A conexão com a partida caiu. As ordens da estratégia seguem valendo."
            error={error}
            onRetry={() => void refetch()}
          />
        </CardContent>
      ) : isLoading ? (
        <CardContent>
          <div className="grid gap-2" aria-busy="true" aria-label="Carregando o registro">
            {[0, 1, 2].map((item) => (
              <Skeleton key={item} className="h-10" />
            ))}
          </div>
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
                Quando você ligar uma estratégia, cada ordem dela aparece aqui, com o motivo.
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
        </CardContent>
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Dia</TableHead>
                <TableHead>O que fez</TableHead>
                <TableHead>Ativo</TableHead>
                <TableHead numeric>Qtd.</TableHead>
                <TableHead numeric>Preço</TableHead>
                <TableHead>Por quê</TableHead>
                <TableHead>Situação</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((row) =>
                row.kind === "order" ? <OrderRow key={row.id} row={row} /> : <ModeRow key={row.id} row={row} />,
              )}
            </TableBody>
          </Table>

          <CardContent>
            <div className="flex items-center gap-1.5 text-[13px] text-muted-foreground">
              Mostrando {rows.length} de {total}
              {hasNextPage && (
                <>
                  <span>·</span>
                  <Button variant="link" size="sm" disabled={isFetchingNextPage} onClick={() => void fetchNextPage()}>
                    Carregar mais
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </>
      )}
    </Card>
  );
}

function DayCell({ row }: { row: StrategyLogRow }) {
  return (
    <TableCell>
      <span className="font-mono text-muted-foreground">{displayDayMonth(row.event_date)}</span>
    </TableCell>
  );
}

function OrderRow({ row }: { row: StrategyLogRow }) {
  const status = row.status ? STATUS_BADGE[row.status] : null;

  return (
    <TableRow>
      <DayCell row={row} />
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
      <TableCell className="whitespace-normal">
        <span className="text-secondary-foreground">{row.reason}</span>
        {row.detail && <span className="block text-xs text-destructive">{row.detail}</span>}
      </TableCell>
      <TableCell>
        {status && (
          <Badge variant={status.variant} size="sm">
            {status.label}
          </Badge>
        )}
      </TableCell>
    </TableRow>
  );
}

function ModeRow({ row }: { row: StrategyLogRow }) {
  const { icon: Icon, tone } = MODE_ICON[row.kind as Exclude<StrategyLogKind, "order">];

  return (
    <TableRow variant="subtle">
      <DayCell row={row} />
      <TableCell colSpan={6} className="whitespace-normal">
        <span className="flex items-center gap-2">
          {row.reason}
          <Icon className={`size-[15px] shrink-0 ${tone}`} />
        </span>
      </TableCell>
    </TableRow>
  );
}
