import { ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { cn } from "@/shared/lib/utils";
import { displayMoney } from "@/shared/lib/utils/display";
import type { Order } from "@/types";
import { type BookViewer, isSyntheticOwner, ownsOrder } from "../lib/order-owner";
import { OrderOwnerBadge } from "./order-owner-badge";
import { BOOK_ROWS, type OrderBook, barShare, displayBookQuantity, largestQuantity } from "../lib/order-book";

type Side = Order["action"];
type PricedOrder = OrderBook["buys"][number];

const GRID: Record<Side, string> = {
  buy: "grid-cols-[34px_minmax(0,1fr)_64px_76px]",
  sell: "grid-cols-[76px_64px_minmax(0,1fr)_34px]",
};

type BookRowProps = {
  order: PricedOrder;
  side: Side;
  share: number;
  best: boolean;
  mine: boolean;
  pickable: boolean;
  onPick: (order: Order) => void;
};

function Maker({ order, mine }: { order: Order; mine: boolean }) {
  if (isSyntheticOwner(order)) return <span>{order.player_nickname}</span>;
  return (
    <>
      {order.player_nickname}
      {mine && <span className="font-normal text-muted-foreground"> (você)</span>}
      {order.owner === "bot" && <span className="font-normal text-muted-foreground"> robô</span>}
    </>
  );
}

function BookRow({ order, side, share, best, mine, pickable, onPick }: BookRowProps) {
  const price = displayMoney(order.limit_price);
  const verb = side === "sell" ? "Comprar" : "Vender";
  const numberAlign = side === "buy" ? "text-right" : "text-left";

  const synthetic = isSyntheticOwner(order);
  const cells = {
    avatar: (
      <span className="flex justify-center">
        <OrderOwnerBadge order={order} />
      </span>
    ),
    name: (
      <span
        className={cn(
          "block truncate text-[13px]",
          side === "sell" && "text-right",
          synthetic ? "text-muted-foreground" : "font-medium",
        )}
      >
        <span className={cn(pickable && "group-hover/row:hidden")}>
          <Maker order={order} mine={mine} />
        </span>
        {pickable && (
          <span className="hidden font-medium text-info group-hover/row:inline">
            {verb} a {price} →
          </span>
        )}
      </span>
    ),
    quantity: (
      <span className={cn("block font-mono text-[13px]", numberAlign, synthetic && "text-muted-foreground")}>
        {displayBookQuantity(order.remaining)}
      </span>
    ),
    price: (
      <span
        className={cn(
          "block font-mono text-[13px]",
          numberAlign,
          side === "buy" ? "text-success" : "text-destructive",
          best ? "font-bold" : "font-medium",
        )}
      >
        {price}
      </span>
    ),
  };
  // A venda espelha a compra: o preço fica junto ao centro e o avatar na borda de fora
  const content =
    side === "buy"
      ? [cells.avatar, cells.name, cells.quantity, cells.price]
      : [cells.price, cells.quantity, cells.name, cells.avatar];

  const rowClass = cn(
    "group/row relative grid h-9 w-full items-center gap-3 border-b border-border/50 px-4 text-left",
    GRID[side],
    mine && "bg-info-soft",
  );
  const bar = (
    <span
      aria-hidden="true"
      className={cn(
        "absolute inset-y-1.5 rounded-[3px]",
        side === "buy" ? "right-0 bg-success/10" : "left-0 bg-destructive/10",
      )}
      style={{ width: `${share * 100}%` }}
    />
  );
  const cellsInRow = content.map((cell, index) => (
    <span key={index} className="relative min-w-0">
      {cell}
    </span>
  ));

  return (
    <li>
      {pickable ? (
        <button
          type="button"
          data-book-row
          className={cn(
            rowClass,
            "cursor-pointer outline-none hover:bg-info-soft hover:ring-1 hover:ring-info-border hover:ring-inset focus-visible:ring-2 focus-visible:ring-ring/50",
          )}
          onClick={() => onPick(order)}
        >
          {bar}
          {cellsInRow}
        </button>
      ) : (
        <div data-book-row className={rowClass}>
          {bar}
          {cellsInRow}
        </div>
      )}
    </li>
  );
}

type BookColumnProps = {
  side: Side;
  orders: PricedOrder[];
  largest: number;
  viewer: BookViewer;
  pickable: boolean;
  onPick: (order: Order) => void;
};

function BookColumn({ side, orders, largest, viewer, pickable, onPick }: BookColumnProps) {
  const title = side === "buy" ? "Compra" : "Venda";

  return (
    <section aria-label={title} className="min-w-0">
      <header
        className={cn(
          "grid items-center gap-3 border-b border-border bg-subtle px-4 py-2 text-xs font-medium text-muted-foreground",
          GRID[side],
        )}
      >
        <span
          className={cn(
            "col-span-2 min-w-0 truncate font-semibold",
            side === "buy" ? "text-success" : "order-last text-right text-destructive",
          )}
        >
          {title} · {orders.length} {orders.length === 1 ? "ordem" : "ordens"}
        </span>
        <span className={side === "buy" ? "text-right" : "order-2 text-left"}>Qtd.</span>
        <span className={side === "buy" ? "text-right" : "order-1 text-left"}>Preço</span>
      </header>
      {orders.length === 0 ? (
        <p className="px-4 py-3 text-xs text-muted-foreground">Sem ofertas de {side === "buy" ? "compra" : "venda"}.</p>
      ) : (
        <ul>
          {orders.map((order, index) => {
            const mine = ownsOrder(order, viewer);
            return (
              <BookRow
                key={order.id}
                order={order}
                side={side}
                share={barShare(order, largest)}
                best={index === 0}
                mine={mine}
                pickable={pickable && !mine}
                onPick={onPick}
              />
            );
          })}
        </ul>
      )}
    </section>
  );
}

type OrderBookColumnsProps = {
  book: OrderBook;
  viewer: BookViewer;
  /** Com a estratégia automática ligada a boleta é só leitura: a linha não prepara ordem */
  pickable: boolean;
  expanded: boolean;
  onToggle: () => void;
  onPick: (order: Order) => void;
};

/** Compras à esquerda, vendas à direita, as melhores ofertas junto ao centro. */
export function OrderBookColumns({ book, viewer, pickable, expanded, onToggle, onPick }: OrderBookColumnsProps) {
  const largest = largestQuantity(book);
  const buys = expanded ? book.buys : book.buys.slice(0, BOOK_ROWS);
  const sells = expanded ? book.sells : book.sells.slice(0, BOOK_ROWS);
  const hasMore = book.buys.length > BOOK_ROWS || book.sells.length > BOOK_ROWS;

  return (
    <>
      <div className="grid grid-cols-2 divide-x divide-border border-t border-border">
        <BookColumn side="buy" orders={buys} largest={largest} viewer={viewer} pickable={pickable} onPick={onPick} />
        <BookColumn side="sell" orders={sells} largest={largest} viewer={viewer} pickable={pickable} onPick={onPick} />
      </div>
      {hasMore && (
        <div className="flex justify-center border-t border-border py-2">
          <Button variant="ghost" size="sm" onClick={onToggle}>
            {expanded
              ? `Mostrar só as ${BOOK_ROWS} mais perto do preço`
              : `Mostrar todas · ${book.buys.length} compras e ${book.sells.length} vendas`}
            {expanded ? <ChevronUp /> : <ChevronDown />}
          </Button>
        </div>
      )}
    </>
  );
}

const SKELETON_NAME_WIDTHS = ["60%", "77%", "94%", "71%", "88%", "65%", "82%", "70%"];

export function OrderBookColumnsSkeleton() {
  return (
    <div className="grid grid-cols-2">
      {(["buy", "sell"] as const).map((side) => (
        <div key={side} className="min-w-0">
          <Skeleton className="h-7" />
          {SKELETON_NAME_WIDTHS.map((width) => (
            <div key={width} className="flex h-9 items-center gap-2.5 px-4">
              <Skeleton className="h-5 w-[34px]" />
              <Skeleton className="h-3" style={{ width }} />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
