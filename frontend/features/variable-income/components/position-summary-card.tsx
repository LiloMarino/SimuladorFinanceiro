import { Card } from "@/shared/components/ui/card";
import { formatMoney } from "@/shared/lib/utils/formatting";
import type { Position, StockDetails } from "@/types";
import clsx from "clsx";

export function PositionSummaryCard({
  position,
  stock,
  cash,
}: {
  position: Position | null;
  stock: StockDetails;
  cash: number;
}) {
  const size = position?.size ?? 0;
  const avgPrice = position?.avg_price ?? 0;
  return (
    <Card className="flex-1 bg-background p-4 border">
      <h3 className="font-medium mb-3">Resumo</h3>
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-muted-foreground">Você possui</p>
          <p className="font-bold">
            {size} ações ({formatMoney(size * stock.close)})
          </p>
        </div>
        <div>
          <p className="text-muted-foreground">Preço médio</p>
          <p className="font-bold">{formatMoney(avgPrice)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Lucro / Prejuízo</p>
          <p className={clsx("font-bold", size > 0 && stock.close - avgPrice >= 0 ? "text-green-600" : "text-red-600")}>
            {formatMoney(size * (stock.close - avgPrice))}
          </p>
        </div>
        <div>
          <p className="text-muted-foreground">Saldo em conta</p>
          <p className="font-bold">{formatMoney(cash)}</p>
        </div>
      </div>
    </Card>
  );
}
