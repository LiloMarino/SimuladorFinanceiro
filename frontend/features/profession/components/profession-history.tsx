import { useState } from "react";
import { History } from "lucide-react";
import { ErrorState } from "@/shared/components/error-state";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
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
import { useLifeHistory } from "@/shared/hooks/queries/useLifeHistory";
import { useLoadMoreOnVisible } from "@/shared/hooks/useLoadMoreOnVisible";
import { LIFE_HISTORY_KINDS, lifeRowIcon, lifeRowText } from "@/shared/lib/life-history";
import type { TableSort } from "@/shared/lib/table-sort";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { LifeHistorySort } from "@/types";
import { isPlayerAction } from "../lib/series";

type Filter = "ALL" | "PLAYER" | "GAME";

const NEWEST_FIRST: TableSort<LifeHistorySort> = { column: "date", direction: "desc" };
const COLUMNS = 3;

/** "Histórico de uso": o que o jogador fez na profissão e o que o jogo mudou nela, do mais recente ao mais antigo. */
export function ProfessionHistory() {
  const [filter, setFilter] = useState<Filter>("ALL");
  const {
    data: pages,
    isPending,
    error,
    refetch,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  } = useLifeHistory("PROFESSION", NEWEST_FIRST);
  const sentinelRef = useLoadMoreOnVisible({ hasNextPage, isFetchingNextPage, fetchNextPage });

  const all = pages?.flatMap((page) => page.items) ?? [];
  const player = all.filter(isPlayerAction);
  const rows = filter === "ALL" ? all : filter === "PLAYER" ? player : all.filter((row) => !isPlayerAction(row));
  // Com mais páginas por carregar, a contagem é a das linhas já lidas
  const more = hasNextPage ? "+" : "";
  const counts: Record<Filter, string> = {
    ALL: `${all.length}${more}`,
    PLAYER: `${player.length}${more}`,
    GAME: `${all.length - player.length}${more}`,
  };
  const filters: { value: Filter; label: string }[] = [
    { value: "ALL", label: "Tudo" },
    { value: "PLAYER", label: "Suas ações" },
    { value: "GAME", label: "Do jogo" },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Histórico de uso</CardTitle>
        <CardDescription>O que você fez e o que o jogo mudou na sua profissão</CardDescription>
        <CardAction>
          <ToggleGroup
            variant="segmented"
            aria-label="Filtrar o histórico da profissão"
            value={[filter]}
            onValueChange={(values) => values[0] && setFilter(values[0] as Filter)}
          >
            {filters.map((option) => (
              <ToggleGroupItem key={option.value} value={option.value}>
                {option.label}
                {pages && ` · ${counts[option.value]}`}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </CardAction>
      </CardHeader>

      {error && !pages ? (
        <div className="px-5">
          <ErrorState
            title="Não deu para carregar o histórico"
            description="A partida continua rodando. Tente de novo."
            error={error}
            onRetry={() => void refetch()}
          />
        </div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Data na partida</TableHead>
              <TableHead>Origem</TableHead>
              <TableHead>O que foi</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isPending && <HistorySkeleton />}
            {!isPending && rows.length === 0 && (
              <TableEmptyRow colSpan={COLUMNS}>
                <HistoryEmpty filter={filter} />
              </TableEmptyRow>
            )}
            {rows.map((row) => {
              const Icon = lifeRowIcon(row);
              const fromPlayer = isPlayerAction(row);
              return (
                <TableRow key={`${row.event_date}-${row.kind}-${row.life_event_key ?? ""}-${row.cash_after}`}>
                  <TableCell numeric>{displayDate(parseLocalDate(row.event_date))}</TableCell>
                  <TableCell>
                    <Badge variant={fromPlayer ? "success" : LIFE_HISTORY_KINDS[row.kind].badge}>
                      {fromPlayer ? "Sua ação" : "Do jogo"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className="flex items-center gap-2">
                      <Icon className="size-4 shrink-0 text-muted-foreground" />
                      {lifeRowText(row)}
                    </span>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}

      {/* Mais linhas: a próxima página vem quando o sentinela entra na área visível */}
      {hasNextPage && (
        <div
          ref={sentinelRef}
          className="flex items-center justify-center gap-2 border-t border-muted px-5 pt-4 text-[13px] text-muted-foreground"
        >
          {isFetchingNextPage && <Spinner />}
          Carregando as anteriores
        </div>
      )}
    </Card>
  );
}

function HistorySkeleton() {
  return Array.from({ length: 3 }, (_, i) => (
    <TableRow key={i}>
      {Array.from({ length: COLUMNS }, (_, j) => (
        <TableCell key={j}>
          <Skeleton className="h-3.5 w-full max-w-28" />
        </TableCell>
      ))}
    </TableRow>
  ));
}

const EMPTY_TEXTS: Record<Filter, { title: string; description: string }> = {
  ALL: {
    title: "Nada aconteceu ainda",
    description: "Cada mudança da sua profissão, sua ou do jogo, aparece aqui com a data na partida.",
  },
  PLAYER: {
    title: "Você ainda não mexeu na profissão",
    description: "Ligar ou desligar a hora extra aparece aqui.",
  },
  GAME: {
    title: "O jogo ainda não mudou nada",
    description: "Troca de profissão e o fim da hora extra com a recessão aparecem aqui.",
  },
};

function HistoryEmpty({ filter }: { filter: Filter }) {
  const text = EMPTY_TEXTS[filter];
  return (
    <Empty>
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <History />
        </EmptyMedia>
        <EmptyTitle>{text.title}</EmptyTitle>
        <EmptyDescription>{text.description}</EmptyDescription>
      </EmptyHeader>
    </Empty>
  );
}
