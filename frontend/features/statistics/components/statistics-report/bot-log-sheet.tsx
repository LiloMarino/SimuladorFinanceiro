import { Bot } from "lucide-react";
import { ErrorState } from "@/shared/components/error-state";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/shared/components/ui/sheet";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { useLoadMoreOnVisible } from "@/shared/hooks/useLoadMoreOnVisible";
import { ACTION_TONE, actionLabel, plural, rowPrice, rowQuantity } from "@/shared/lib/strategy-orders";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { PlayerRef } from "@/types";
import { useBotLog } from "../../hooks/queries/useBotLog";

type BotLogSheetProps = {
  bot: PlayerRef;
  onClose: () => void;
};

/** "O que <bot> fez": as ordens do bot na partida, cada uma com o motivo, num painel lateral que fecha o log. */
export function BotLogSheet({ bot, onClose }: BotLogSheetProps) {
  const {
    data: pages,
    error,
    isLoading,
    refetch,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useBotLog(bot.simulation_id, bot.player_nickname);

  const sentinelRef = useLoadMoreOnVisible({ hasNextPage, isFetchingNextPage, fetchNextPage });

  const rows = pages?.flatMap((page) => page.items) ?? [];
  const total = pages?.at(-1)?.total ?? 0;

  return (
    <Sheet open onOpenChange={(open) => !open && onClose()}>
      <SheetContent size="xl">
        {/* Título */}
        <SheetHeader>
          <div className="flex items-center gap-2.5 pr-8">
            <PlayerAvatar nickname={bot.player_nickname} color={bot.color} bot size="lg" />
            <div className="grid gap-0.5">
              <SheetTitle>O que {bot.player_nickname} fez</SheetTitle>
              <SheetDescription>{plural(total, "ordem", "ordens")} na partida, cada uma com o motivo</SheetDescription>
            </div>
          </div>
        </SheetHeader>

        {/* Ordens */}
        <div className="flex-1 overflow-y-auto">
          {error ? (
            <div className="px-6 py-5">
              <ErrorState
                title="Não deu para carregar o log"
                description="A conexão com a partida caiu. Tente de novo em instantes."
                error={error}
                onRetry={() => void refetch()}
              />
            </div>
          ) : isLoading ? (
            <div className="grid gap-2 px-6 py-5" aria-busy="true" aria-label="Carregando o log">
              {[0, 1, 2].map((item) => (
                <Skeleton key={item} className="h-10" />
              ))}
            </div>
          ) : rows.length === 0 ? (
            <div className="px-6 py-5">
              <Empty variant="dashed">
                <EmptyHeader>
                  <EmptyMedia variant="icon">
                    <Bot />
                  </EmptyMedia>
                  <EmptyTitle>Nenhuma ordem</EmptyTitle>
                  <EmptyDescription>Este bot não mandou nenhuma ordem na partida.</EmptyDescription>
                </EmptyHeader>
              </Empty>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Dia</TableHead>
                  <TableHead>O que fez</TableHead>
                  <TableHead wrap>Ativo</TableHead>
                  <TableHead numeric>Qtd.</TableHead>
                  <TableHead numeric>Preço</TableHead>
                  <TableHead wrap>Por quê</TableHead>
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
                    <TableCell wrap>
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
                    <TableCell wrap>{row.reason}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {/* Sentinela: a próxima página vem quando ele entra na área rolável */}
          {hasNextPage && <div ref={sentinelRef} aria-hidden className="h-px" />}
        </div>

        <SheetFooter>
          <div className="flex items-center gap-1.5 text-[13px] text-muted-foreground">
            Mostrando {rows.length} de {total}
            {isFetchingNextPage && (
              <>
                <span>·</span>
                <Spinner className="size-3.5" />
                Carregando mais
              </>
            )}
          </div>
          <SheetClose render={<Button variant="outline" />}>Fechar</SheetClose>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
