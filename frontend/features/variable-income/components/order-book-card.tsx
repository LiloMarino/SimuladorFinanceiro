import { useState } from "react";
import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { MarketMark } from "@/shared/components/market-mark";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { useAuth } from "@/shared/hooks/useAuth";
import { useMyStrategy } from "@/shared/hooks/queries/useMyStrategy";
import { displayDate, displayMoney, displayQuantity, parseLocalDate } from "@/shared/lib/utils/display";
import type { Order } from "@/types";
import { useTrades } from "../hooks/queries/useTrades";
import { useCancelOrder } from "../hooks/mutations/useCancelOrder";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { sortNumber } from "@/shared/lib/table-sort";

type Tab = "OPEN" | "HISTORY";

// Hora da ordem, no relógio de quem olha
const displayTime = (isoDateTime: string) =>
  new Intl.DateTimeFormat("pt-BR", { hour: "2-digit", minute: "2-digit" }).format(new Date(isoDateTime));

function Player({
  nickname,
  color,
  isYou,
  market = false,
}: {
  nickname: string;
  color: string | null | undefined;
  isYou: boolean;
  market?: boolean;
}) {
  // O Mercado é uma entidade do simulador: marca própria, sem "(você)"
  if (market) {
    return (
      <span className="flex items-center gap-2 font-medium">
        <MarketMark size="sm" />
        Mercado
      </span>
    );
  }
  return (
    <span className="flex items-center gap-2">
      <PlayerAvatar nickname={nickname} color={color ?? undefined} size="sm" />
      {nickname}
      {isYou && <span className="text-muted-foreground">(você)</span>}
    </span>
  );
}

function Side({ action }: { action: string }) {
  return action === "buy" ? <Badge variant="success">Compra</Badge> : <Badge variant="destructive">Venda</Badge>;
}

/** O que a ordem já executou: tamanho menos o que falta. */
const executedQuantity = (o: Order) => displayQuantity(String(Number(o.size) - Number(o.remaining)));

/** Ordens de todos os jogadores no ativo: as abertas e as execuções da sala. */
export function OrderBookCard({ ticker, orders }: { ticker: string; orders: Order[] }) {
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>("OPEN");

  const open = orders.filter((o) => o.status === "pending" || o.status === "partial");
  const myPartial = open.filter((o) => o.status === "partial" && o.player_nickname === user?.nickname);

  const { data: trades } = useTrades(ticker, { enabled: tab === "HISTORY" });
  const openSort = useTableSort(open, {
    date: (o) => o.created_at,
    player: (o) => o.player_nickname,
    side: (o) => (o.action === "buy" ? "Compra" : "Venda"),
    quantity: (o) => Number(o.size),
    price: (o) => sortNumber(o.limit_price),
    status: (o) => (o.status === "partial" ? "Parcial" : "Pendente"),
  });
  const tradeSort = useTableSort(trades ?? [], {
    date: (t) => t.event_date,
    player: (t) => t.player_nickname,
    side: (t) => (t.action === "buy" ? "Compra" : "Venda"),
    quantity: (t) => Number(t.quantity),
    price: (t) => Number(t.price),
  });

  const cancel = useCancelOrder(ticker);
  // Com o automático ligado as ordens abertas são da estratégia: só ela cancela
  const automatic = !!useMyStrategy().data?.active;

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Livro de ofertas da sala</CardTitle>
        <CardDescription>Ordens dos jogadores e do Mercado em {ticker}.</CardDescription>
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
                Sua {o.action === "buy" ? "compra" : "venda"} de {displayQuantity(o.size)} {ticker} executou{" "}
                {executedQuantity(o)}. As outras {displayQuantity(o.remaining)} seguem abertas até alguém{" "}
                {o.action === "buy" ? "vender" : "comprar"}
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
                <SortableTableHead {...openSort.header("date")} label="Quando" />
                <SortableTableHead {...openSort.header("player")} label="Quem" />
                <SortableTableHead {...openSort.header("side")} label="Lado" />
                <SortableTableHead {...openSort.header("quantity")} label="Qtd." numeric />
                <SortableTableHead {...openSort.header("price")} label="Preço" numeric />
                <SortableTableHead {...openSort.header("status")} label="Situação" />
                <TableHead>
                  <span className="sr-only">Ações</span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {openSort.rows.map((o) => {
                const mine = o.player_nickname === user?.nickname;
                return (
                  <TableRow key={o.id} variant={o.synthetic ? "subtle" : "default"}>
                    <TableCell>
                      <span className="font-mono text-xs text-muted-foreground">{displayTime(o.created_at)}</span>
                    </TableCell>
                    <TableCell>
                      <Player nickname={o.player_nickname} color={o.player_color} isYou={mine} market={o.synthetic} />
                    </TableCell>
                    <TableCell>
                      <Side action={o.action} />
                    </TableCell>
                    <TableCell numeric>{displayQuantity(o.size)}</TableCell>
                    <TableCell numeric>{o.limit_price === null ? "a mercado" : displayMoney(o.limit_price)}</TableCell>
                    <TableCell>
                      {o.status === "partial" ? (
                        <Badge variant="warning">
                          Parcial · {executedQuantity(o)} de {displayQuantity(o.size)}
                        </Badge>
                      ) : (
                        <Badge variant="info">Aberta</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {mine && !automatic && o.status === "pending" && (
                        <Button
                          variant="outline"
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
              <SortableTableHead {...tradeSort.header("date")} label="Quando" />
              <SortableTableHead {...tradeSort.header("player")} label="Quem" />
              <SortableTableHead {...tradeSort.header("side")} label="Lado" />
              <SortableTableHead {...tradeSort.header("quantity")} label="Qtd." numeric />
              <SortableTableHead {...tradeSort.header("price")} label="Preço" numeric />
            </TableRow>
          </TableHeader>
          <TableBody>
            {tradeSort.rows.map((t, i) => (
              <TableRow key={`${t.event_date}-${i}`}>
                <TableCell>
                  <span className="font-mono">{displayDate(parseLocalDate(t.event_date))}</span>
                </TableCell>
                <TableCell>
                  <Player
                    nickname={t.player_nickname}
                    color={t.player_color}
                    isYou={t.player_nickname === user?.nickname}
                  />
                </TableCell>
                <TableCell>
                  <Side action={t.action} />
                </TableCell>
                <TableCell numeric>{displayQuantity(t.quantity)}</TableCell>
                <TableCell numeric>{displayMoney(t.price)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Card>
  );
}
