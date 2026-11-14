import { useState } from "react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { Button } from "@/shared/components/ui/button";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/shared/components/ui/table";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { useAuth } from "@/shared/hooks/useAuth";
import { displayDate, displayMoney, displayQuantity, parseLocalDate } from "@/shared/lib/utils/display";
import { useTrades } from "../hooks/queries/useTrades";

/** Quantos negócios aparecem antes do "Ver mais negócios". */
const VISIBLE_TRADES = 10;

/** Negócios fechados no ativo: quem comprou ou vendeu, quanto e a que preço. */
export function TradeHistory({ ticker }: { ticker: string }) {
  const { user } = useAuth();
  const { data: trades } = useTrades(ticker);
  const [showAll, setShowAll] = useState(false);

  const sort = useTableSort(trades ?? [], {
    date: (t) => t.event_date,
    player: (t) => t.player_nickname,
    quantity: (t) => Number(t.quantity),
    price: (t) => Number(t.price),
  });

  if (!trades || trades.length === 0) {
    return (
      <Empty>
        <EmptyHeader>
          <EmptyTitle>Nenhum negócio ainda</EmptyTitle>
          <EmptyDescription>As compras e vendas executadas na sala aparecem aqui.</EmptyDescription>
        </EmptyHeader>
      </Empty>
    );
  }

  const rows = showAll ? sort.rows : sort.rows.slice(0, VISIBLE_TRADES);

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <SortableTableHead {...sort.header("date")} label="Quando" />
            <SortableTableHead {...sort.header("player")} label="Comprou · vendeu" />
            <SortableTableHead {...sort.header("quantity")} label="Qtd." numeric />
            <SortableTableHead {...sort.header("price")} label="Preço" numeric />
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((t, i) => (
            <TableRow key={`${t.event_date}-${i}`}>
              <TableCell>
                <span className="font-mono">{displayDate(parseLocalDate(t.event_date))}</span>
              </TableCell>
              <TableCell>
                <span className="flex items-center gap-2">
                  <PlayerAvatar nickname={t.player_nickname} color={t.player_color} size="sm" />
                  {t.player_nickname}
                  {t.player_nickname === user?.nickname && <span className="text-muted-foreground">(você)</span>}
                  <span className="text-muted-foreground">{t.action === "buy" ? "comprou" : "vendeu"}</span>
                </span>
              </TableCell>
              <TableCell numeric>{displayQuantity(t.quantity)}</TableCell>
              <TableCell numeric>{displayMoney(t.price)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!showAll && trades.length > VISIBLE_TRADES && (
        <div className="flex justify-center border-t border-border py-2">
          <Button variant="ghost" size="sm" onClick={() => setShowAll(true)}>
            Ver mais negócios
          </Button>
        </div>
      )}
    </>
  );
}
