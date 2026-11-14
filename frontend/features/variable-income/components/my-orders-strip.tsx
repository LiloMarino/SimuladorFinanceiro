import { Link } from "react-router-dom";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Progress } from "@/shared/components/ui/progress";
import { displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import type { Order } from "@/types";
import { displayDayMonth } from "../lib/order-book";

type MyOrdersStripProps = {
  orders: Order[];
  /** Melhor compra do livro, a régua do "quanto falta" das compras limitadas */
  bestBuy: number | undefined;
  /** Com a estratégia automática ligada só ela cancela */
  automatic: boolean;
  cancelling: boolean;
  onCancel: (order: Order) => void;
};

/** O que já executou da ordem: tamanho menos o que falta. */
const executedQuantity = (order: Order) => Number(order.size) - Number(order.remaining);

function MyOrder({
  order,
  bestBuy,
  automatic,
  cancelling,
  onCancel,
}: Omit<MyOrdersStripProps, "orders"> & { order: Order }) {
  const partial = order.status === "partial";
  const gap =
    order.action === "buy" && order.limit_price !== null && bestBuy !== undefined ? bestBuy - order.limit_price : 0;

  return (
    <li data-book-row className="grid gap-1 px-3 py-2">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        <PlayerAvatar
          nickname={order.player_nickname}
          color={order.player_color ?? undefined}
          bot={order.player_is_bot}
          size="sm"
        />
        <span className="text-[13px] font-medium">
          {order.player_nickname} <span className="font-normal text-muted-foreground">(você)</span>
        </span>
        <Badge variant={order.action === "buy" ? "success" : "destructive"}>
          {order.action === "buy" ? "Compra" : "Venda"}
        </Badge>
        <span className="font-mono text-[13px]">
          {displayQuantity(order.size)}{" "}
          {order.limit_price === null ? "a mercado" : `a ${displayMoney(order.limit_price)}`}
        </span>
        <span className="text-xs text-muted-foreground">limitada · desde {displayDayMonth(order.placed_on)}</span>
        {partial && (
          <span className="flex items-center gap-2 text-xs text-warning">
            <Progress
              value={(executedQuantity(order) / Number(order.size)) * 100}
              size="sm"
              indicatorTone="warning"
              className="w-[60px] flex-nowrap"
              aria-label="Quanto da ordem já executou"
            />
            executou {displayQuantity(String(executedQuantity(order)))} de {displayQuantity(order.size)}
          </span>
        )}
        {!automatic && (
          <Button
            variant="outline-destructive"
            size="sm"
            className="ml-auto"
            disabled={cancelling}
            onClick={() => onCancel(order)}
          >
            {partial ? `Cancelar as ${displayQuantity(order.remaining)} restantes` : "Cancelar"}
          </Button>
        )}
      </div>
      {gap > 0 && bestBuy !== undefined && (
        <p className="text-xs text-muted-foreground">
          {displayMoney(gap)} abaixo da melhor compra ({displayMoney(bestBuy)}): executa se o preço cair até lá.
        </p>
      )}
    </li>
  );
}

/** Faixa no topo do livro com as ordens abertas do jogador, sempre à vista. */
export function MyOrdersStrip({ orders, ...rest }: MyOrdersStripProps) {
  if (orders.length === 0) return null;

  return (
    <section aria-label="Suas ordens" className="mx-5 mb-3 rounded-[10px] border border-info-border bg-info-soft">
      <h4 className="px-3 pt-2 text-xs font-semibold tracking-wide text-info uppercase">
        Suas ordens · {orders.length}
      </h4>
      {rest.automatic && (
        <p className="flex flex-wrap items-center gap-x-2 px-3 pt-1 text-xs text-info">
          A estratégia automática cuida das suas ordens: ela cancela e refaz a cada pregão.
          <Button variant="link" size="sm" nativeButton={false} render={<Link to="/strategies" />}>
            Ver estratégia
          </Button>
        </p>
      )}
      <ul className="divide-y divide-info-border">
        {orders.map((order) => (
          <MyOrder key={order.id} order={order} {...rest} />
        ))}
      </ul>
    </section>
  );
}
