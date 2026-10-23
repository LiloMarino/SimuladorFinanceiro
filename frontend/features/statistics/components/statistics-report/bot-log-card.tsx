import { Bot, X } from "lucide-react";
import { ErrorState } from "@/shared/components/error-state";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { ACTION_TONE, actionLabel, plural, rowPrice, rowQuantity } from "@/shared/lib/strategy-orders";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { PlayerRef } from "@/types";
import { useBotLog } from "../../hooks/queries/useBotLog";

type BotLogCardProps = {
  bot: PlayerRef;
  onClose: () => void;
};

/** "O que <bot> fez": as ordens do bot na partida, cada uma com o motivo. */
export function BotLogCard({ bot, onClose }: BotLogCardProps) {
  const {
    data: pages,
    error,
    isLoading,
    refetch,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useBotLog(bot.simulation_id, bot.player_nickname);

  const rows = pages?.flatMap((page) => page.items) ?? [];
  const total = pages?.at(-1)?.total ?? 0;

  return (
    <Card>
      {/* Título */}
      <CardHeader>
        <div className="flex items-center gap-2.5">
          <PlayerAvatar nickname={bot.player_nickname} color={bot.color} bot size="lg" />
          <div className="grid gap-1">
            <CardTitle>O que {bot.player_nickname} fez</CardTitle>
            <CardDescription>
              {plural(total, "ordem", "ordens")} na partida, cada uma com o motivo
            </CardDescription>
          </div>
        </div>
        <CardAction>
          <Button type="button" variant="outline" size="sm" onClick={onClose}>
            Fechar
            <X />
          </Button>
        </CardAction>
      </CardHeader>

      {/* Ordens */}
      {error ? (
        <CardContent>
          <ErrorState
            title="Não deu para carregar o log"
            description="A conexão com a partida caiu. Tente de novo em instantes."
            error={error}
            onRetry={() => void refetch()}
          />
        </CardContent>
      ) : isLoading ? (
        <CardContent>
          <div className="grid gap-2" aria-busy="true" aria-label="Carregando o log">
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
              <EmptyTitle>Nenhuma ordem</EmptyTitle>
              <EmptyDescription>Este bot não mandou nenhuma ordem na partida.</EmptyDescription>
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
                  <TableCell className="whitespace-normal">{row.reason}</TableCell>
                </TableRow>
              ))}
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
