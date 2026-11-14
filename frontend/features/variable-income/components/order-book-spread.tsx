import { Skeleton } from "@/shared/components/ui/skeleton";
import { InfoHint } from "@/shared/components/info-hint";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import { type OrderBook, type Spread, spreadPercentDigits } from "../lib/order-book";

type OrderBookSpreadProps = {
  book: OrderBook;
  spread: Spread | null;
};

/** Faixa entre o cabeçalho e as colunas: o que quem vende na hora recebe, a diferença e o que quem compra na hora paga. */
export function OrderBookSpread({ book, spread }: OrderBookSpreadProps) {
  const bestBuy = book.buys[0]?.limit_price;
  const bestSell = book.sells[0]?.limit_price;

  return (
    <div className="mx-5 mb-3 grid grid-cols-[1fr_auto_1fr] items-stretch overflow-hidden rounded-[10px] border border-border">
      {/* Melhor compra */}
      <div className="flex items-center justify-end gap-2.5 bg-success-soft px-4 py-2.5">
        <p className="text-right text-xs text-success">
          Melhor compra
          <br />
          <span className="text-muted-foreground">vender a mercado recebe</span>
        </p>
        <span className="font-mono text-lg font-bold text-success">
          {bestBuy === undefined ? "—" : displayMoney(bestBuy)}
        </span>
      </div>
      {/* Diferença */}
      <div className="flex min-w-37.5 flex-col items-center justify-center bg-subtle px-4 py-1.5">
        <span className="flex items-center gap-1 text-xs text-muted-foreground">
          diferença
          <InfoHint label="O que é a diferença">
            Distância entre a melhor venda e a melhor compra. Abaixo de 0,5% do preço, entrar e sair é barato; acima de
            2%, comprar e vender na hora já custa caro.
          </InfoHint>
        </span>
        <span className="font-mono text-sm font-semibold">
          {spread
            ? `${displayMoney(spread.amount)} · ${displayPercent(spread.percent, spreadPercentDigits(spread.percent))}`
            : "—"}
        </span>
      </div>
      {/* Melhor venda */}
      <div className="flex items-center gap-2.5 bg-destructive-soft px-4 py-2.5">
        <span className="font-mono text-lg font-bold text-destructive">
          {bestSell === undefined ? "—" : displayMoney(bestSell)}
        </span>
        <p className="text-xs text-destructive">
          Melhor venda
          <br />
          <span className="text-muted-foreground">comprar a mercado paga</span>
        </p>
      </div>
    </div>
  );
}

export function OrderBookSpreadSkeleton() {
  return <Skeleton className="mx-5 mb-3 h-14" />;
}
