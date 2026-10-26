import { useState } from "react";
import { useLocation } from "react-router-dom";
import { History } from "lucide-react";
import { ErrorState } from "@/shared/components/error-state";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableFooter,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { unexpectedLabel } from "@/shared/lib/financial-independence";
import { displayDate, displaySignedMoney, parseLocalDate } from "@/shared/lib/utils/display";
import type { LifeHistoryCategory, LifeHistoryPage, LifeStatus, LifeHistorySort } from "@/types";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSortState } from "@/shared/hooks/useTableSort";
import { useLifeHistory } from "../hooks/queries/useLifeHistory";
import { LIFE_HISTORY_KINDS, lifeRowIcon, lifeRowText } from "../lib/life-history";

type Filter = "ALL" | LifeHistoryCategory;

const FILTERS: {
  value: Filter;
  label: string;
  count: (counts: LifeHistoryPage["counts"]) => number;
}[] = [
  { value: "ALL", label: "Tudo", count: (c) => c.all },
  { value: "UNEXPECTED", label: "Imprevistos", count: (c) => c.unexpected },
  { value: "LAYOFF", label: "Demissões", count: (c) => c.layoff },
  { value: "OVERDRAFT", label: "Cheque especial", count: (c) => c.overdraft },
];

const COLUMNS = 5;

type LifeHistoryProps = {
  life: LifeStatus;
};

/** "Histórico" do viver de renda: imprevistos, demissões e cheque especial, do mais recente ao mais antigo. */
export function LifeHistory({ life }: LifeHistoryProps) {
  const [filter, setFilter] = useState<Filter>("ALL");
  const sorting = useTableSortState<LifeHistorySort>({ column: "date", direction: "desc" });
  const {
    data: pages,
    isPending,
    error,
    refetch,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
    isFetching,
  } = useLifeHistory(filter === "ALL" ? null : filter, sorting.sort!);
  // O aviso que levou até aqui marca a linha do evento
  const highlightDate = (useLocation().state as { highlightDate?: string } | null)?.highlightDate;

  const counts = pages?.[0]?.counts;
  const rows = pages?.flatMap((page) => page.items) ?? [];
  const remaining = (pages?.[0]?.total ?? 0) - rows.length;
  const interestPaid = Number(pages?.[0]?.interest_paid ?? 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Histórico</CardTitle>
        <CardDescription>
          O que aconteceu na partida. Clique nos cabeçalhos para ordenar todo o histórico. Os imprevistos são iguais
          para todos; o caixa depois é o seu.
        </CardDescription>
        <CardAction>
          <ToggleGroup
            variant="segmented"
            aria-label="Filtrar o histórico"
            value={[filter]}
            onValueChange={(values) => values[0] && setFilter(values[0] as Filter)}
          >
            {FILTERS.map((option) => (
              <ToggleGroupItem key={option.value} value={option.value}>
                {option.label}
                {counts && ` · ${option.count(counts)}`}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </CardAction>
      </CardHeader>

      {error && !pages ? (
        <div className="px-5">
          <ErrorState
            title="Não deu pra carregar o histórico"
            description="A partida continua rodando. Tente de novo."
            error={error}
            onRetry={() => void refetch()}
          />
        </div>
      ) : (
        <Table aria-busy={isFetching}>
          <TableHeader>
            <TableRow>
              <SortableTableHead {...sorting.header("date")} label="Data na partida" />
              <SortableTableHead {...sorting.header("type")} label="Tipo" />
              <SortableTableHead {...sorting.header("description")} label="O que foi" />
              <SortableTableHead {...sorting.header("amount")} label="Valor" numeric />
              <SortableTableHead {...sorting.header("cash")} label="Seu caixa depois" numeric />
            </TableRow>
          </TableHeader>
          <TableBody>
            {isPending && <HistorySkeleton />}
            {!isPending && rows.length === 0 && (
              <TableEmptyRow colSpan={COLUMNS}>
                <HistoryEmpty
                  filtered={filter !== "ALL" && (counts?.all ?? 0) > 0}
                  perYear={life.unexpected_per_year}
                />
              </TableEmptyRow>
            )}
            {rows.map((row) => {
              const kind = LIFE_HISTORY_KINDS[row.kind];
              const Icon = lifeRowIcon(row);
              const amount = row.amount === null ? null : Number(row.amount);
              const isNew = row.event_date === highlightDate;
              return (
                <TableRow
                  key={`${row.event_date}-${row.kind}-${row.life_event_key ?? ""}-${row.cash_after}`}
                  variant={isNew ? "highlight" : "default"}
                >
                  <TableCell numeric>{displayDate(parseLocalDate(row.event_date))}</TableCell>
                  <TableCell>
                    <Badge variant={kind.badge}>{kind.tag}</Badge>
                  </TableCell>
                  <TableCell>
                    <span className="flex items-center gap-2">
                      <Icon className="size-4 shrink-0 text-muted-foreground" />
                      {lifeRowText(row, life.overdraft_monthly_rate)}
                      {isNew && (
                        <Badge variant="info" size="sm">
                          novo
                        </Badge>
                      )}
                    </span>
                  </TableCell>
                  <TableCell numeric>
                    {row.kind === "LAYOFF" ? (
                      <span className="font-sans text-muted-foreground">Sem salário</span>
                    ) : amount === null ? (
                      <span className="text-muted-foreground">—</span>
                    ) : (
                      <span className={amount < 0 ? "text-destructive" : undefined}>{displaySignedMoney(amount)}</span>
                    )}
                  </TableCell>
                  <TableCell numeric>
                    <span className={Number(row.cash_after) < 0 ? "text-destructive" : undefined}>
                      {displaySignedMoney(row.cash_after)}
                    </span>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
          {/* Juros do cheque especial da partida inteira */}
          {interestPaid > 0 && (
            <TableFooter>
              <TableRow>
                <TableCell colSpan={3} variant="group">
                  Juros pagos na partida
                </TableCell>
                <TableCell numeric>
                  <span className="text-destructive">{displaySignedMoney(-interestPaid)}</span>
                </TableCell>
                <TableCell />
              </TableRow>
            </TableFooter>
          )}
        </Table>
      )}

      {/* Mais linhas */}
      {hasNextPage && (
        <div className="flex justify-center border-t border-muted px-5 pt-4">
          <Button variant="outline" size="sm" disabled={isFetching} onClick={() => void fetchNextPage()}>
            {isFetchingNextPage && <Spinner />}
            Mostrar mais · {remaining} {remaining === 1 ? "anterior" : "anteriores"}
          </Button>
        </div>
      )}
    </Card>
  );
}

function HistorySkeleton() {
  return Array.from({ length: 4 }, (_, i) => (
    <TableRow key={i}>
      {Array.from({ length: COLUMNS }, (_, j) => (
        <TableCell key={j}>
          <Skeleton className="h-3.5 w-full max-w-28" />
        </TableCell>
      ))}
    </TableRow>
  ));
}

function HistoryEmpty({ filtered, perYear }: { filtered: boolean; perYear: number }) {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <History />
        </EmptyMedia>
        <EmptyTitle>{filtered ? "Nada neste filtro" : "Nada aconteceu ainda"}</EmptyTitle>
        <EmptyDescription>
          {filtered
            ? "Escolha outro filtro para ver o resto do histórico."
            : perYear > 0
              ? `Com imprevistos ${unexpectedLabel(perYear)}, espere uns ${perYear} por ano. Quando um chegar, ele aparece aqui, com o que foi e quanto saiu do caixa.`
              : "Os imprevistos estão desligados nesta partida. Se o caixa ficar negativo, o cheque especial aparece aqui."}
        </EmptyDescription>
      </EmptyHeader>
    </Empty>
  );
}
