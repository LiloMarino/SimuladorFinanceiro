import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Avatar, AvatarFallback } from "@/shared/components/ui/avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { useAuth } from "@/shared/hooks/useAuth";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { stringToColor } from "@/shared/lib/utils";
import { displayDate, displayMoney, parseLocalDate } from "@/shared/lib/utils/display";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { Order, Trade } from "@/types";

type Tab = "OPEN" | "HISTORY";

function Player({ nickname, isYou }: { nickname: string; isYou: boolean }) {
  return (
    <span className="flex items-center gap-2">
      <Avatar size="sm">
        <AvatarFallback color={stringToColor(nickname)}>{nickname.charAt(0).toUpperCase()}</AvatarFallback>
      </Avatar>
      {nickname}
      {isYou && <span className="text-muted-foreground">(você)</span>}
    </span>
  );
}

function Side({ action }: { action: string }) {
  return action === "buy" ? <Badge variant="success">Compra</Badge> : <Badge variant="destructive">Venda</Badge>;
}

/** Ordens de todos os jogadores no ativo: as abertas e as execuções da sala. */
export function OrderBookCard({ ticker, orders }: { ticker: string; orders: Order[] }) {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>("OPEN");

  const open = orders.filter((o) => !o.synthetic && (o.status === "pending" || o.status === "partial"));
  const myPartial = open.filter((o) => o.status === "partial" && o.player_nickname === user?.nickname);

  const { data: trades } = useApiQuery({
    queryKey: queryKeys.trades(ticker),
    queryFn: ({ signal }) => apiFetch<Trade[]>(`/api/variable-income/${ticker}/trades`, { signal }),
    enabled: tab === "HISTORY",
  });

  const cancel = useApiMutation({
    mutationFn: (orderId: string) =>
      apiFetch(`/api/variable-income/${ticker}/orders`, { method: "DELETE", body: { order_id: orderId } }),
    onError: (err) => toastApiError(err),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKeys.variableIncomeOrders(ticker) }),
  });

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Livro de ofertas da sala</CardTitle>
        <CardDescription>Ordens de todos os jogadores em {ticker}.</CardDescription>
        <CardAction>
          <ToggleGroup
            variant="segmented"
            aria-label="Ordens"
            value={[tab]}
            onValueChange={(values) => values[0] && setTab(values[0] as Tab)}
          >
            <ToggleGroupItem value="OPEN">Abertas · {open.length}</ToggleGroupItem>
            <ToggleGroupItem value="HISTORY">Histórico</ToggleGroupItem>
          </ToggleGroup>
        </CardAction>
      </CardHeader>

      {/* Execução parcial: o que falta e a que preço */}
      {tab === "OPEN" &&
        myPartial.map((o) => (
          <div key={o.id} className="px-5 pb-3">
            <Alert variant="warning">
              <TriangleAlert />
              <AlertDescription>
                Sua {o.action === "buy" ? "compra" : "venda"} de {o.size} {ticker} executou {o.size - o.remaining}. As
                outras {o.remaining} seguem abertas até alguém {o.action === "buy" ? "vender" : "comprar"}
                {o.limit_price !== null ? ` a ${displayMoney(o.limit_price)}` : ""}.
              </AlertDescription>
            </Alert>
          </div>
        ))}

      {tab === "OPEN" ? (
        open.length === 0 ? (
          <Empty>
            <EmptyHeader>
              <EmptyTitle>Nenhuma ordem aberta</EmptyTitle>
              <EmptyDescription>Ordens limitadas que ainda não executaram ficam aqui.</EmptyDescription>
            </EmptyHeader>
          </Empty>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Quem</TableHead>
                <TableHead>Lado</TableHead>
                <TableHead numeric>Qtd.</TableHead>
                <TableHead numeric>Preço</TableHead>
                <TableHead>Situação</TableHead>
                <TableHead>
                  <span className="sr-only">Ações</span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {open.map((o) => {
                const mine = o.player_nickname === user?.nickname;
                return (
                  <TableRow key={o.id}>
                    <TableCell>
                      <Player nickname={o.player_nickname} isYou={mine} />
                    </TableCell>
                    <TableCell>
                      <Side action={o.action} />
                    </TableCell>
                    <TableCell numeric>{o.size}</TableCell>
                    <TableCell numeric>{o.limit_price === null ? "a mercado" : displayMoney(o.limit_price)}</TableCell>
                    <TableCell>
                      {o.status === "partial" ? (
                        <Badge variant="warning">
                          Parcial · {o.size - o.remaining} de {o.size}
                        </Badge>
                      ) : (
                        <Badge variant="info">Aberta</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {mine && (
                        <Button
                          variant="ghost"
                          size="sm"
                          disabled={cancel.isPending}
                          onClick={() => cancel.mutate(o.id)}
                        >
                          Cancelar
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )
      ) : !trades || trades.length === 0 ? (
        <Empty>
          <EmptyHeader>
            <EmptyTitle>Nenhum negócio ainda</EmptyTitle>
            <EmptyDescription>As compras e vendas executadas na sala aparecem aqui.</EmptyDescription>
          </EmptyHeader>
        </Empty>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Quando</TableHead>
              <TableHead>Quem</TableHead>
              <TableHead>Lado</TableHead>
              <TableHead numeric>Qtd.</TableHead>
              <TableHead numeric>Preço</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {trades.map((t, i) => (
              <TableRow key={`${t.event_date}-${i}`}>
                <TableCell>
                  <span className="font-mono">{displayDate(parseLocalDate(t.event_date))}</span>
                </TableCell>
                <TableCell>
                  <Player nickname={t.player_nickname} isYou={t.player_nickname === user?.nickname} />
                </TableCell>
                <TableCell>
                  <Side action={t.action} />
                </TableCell>
                <TableCell numeric>{t.quantity}</TableCell>
                <TableCell numeric>{displayMoney(t.price)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Card>
  );
}
