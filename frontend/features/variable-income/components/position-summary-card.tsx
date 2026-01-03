import { Card } from "@/shared/components/ui/card";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { Position, StockDetails } from "@/types";
import clsx from "clsx";

export function PositionSummaryCard({ stock, cash }: { stock: StockDetails; cash: number }) {
  const { data: position, setData: setPosition } = useQueryApi<Position>(`/api/portfolio/${stock.ticker}`);

  useRealtime(`position_update:${stock.ticker}`, ({ position }) => {
    setPosition(position);
  });

  const size = position?.size ?? 0;
  const avgPrice = position?.avg_price ?? 0;
  const currentPrice = stock.close;
  const pnl = size * (currentPrice - avgPrice);
  const pnlPct = avgPrice > 0 ? (currentPrice - avgPrice) / avgPrice : 0;
  const isProfit = pnl >= 0;
  return (
    <Card className="flex-1 bg-background p-4 border gap-4">
      <h3 className="font-medium">Resumo</h3>
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-muted-foreground">Você possui</p>
          <p className="font-bold">
            {size} ações ({displayMoney(size * currentPrice)})
          </p>
        </div>

        <div>
          <p className="text-muted-foreground">Saldo em conta</p>
          <p className="font-bold">{displayMoney(cash)}</p>
        </div>

        <div>
          <p className="text-muted-foreground">Preço médio</p>
          <p className="font-bold">{displayMoney(avgPrice)}</p>
        </div>

        <div>
          <p className="text-muted-foreground">Preço atual</p>
          <p className="font-bold">{displayMoney(currentPrice)}</p>
        </div>

        <div className="col-span-2">
          <p className="text-muted-foreground">Lucro / Prejuízo</p>
          <p className={clsx("font-bold", isProfit ? "text-green-600" : "text-red-600")}>
            {displayMoney(pnl)} ({displayPercent(pnlPct)})
          </p>
        </div>
      </div>
    </Card>
  );
}
