import { Card } from "@/shared/components/ui/card";
import { displayMoney, displayPercent, isLoss } from "@/shared/lib/utils/display";
import type { Position, StockDetails } from "@/types";
import clsx from "clsx";

type PositionSummaryCardProps = {
  stock: StockDetails;
  position: Position | null;
};

export function PositionSummaryCard({ stock, position }: PositionSummaryCardProps) {
  const size = position?.size ?? 0;
  const reserved = position?.reserved ?? 0;
  const returnValue = position?.return_value ?? "0";
  return (
    <Card className="flex-1 bg-background p-4 border gap-4">
      <h3 className="font-medium">Resumo</h3>
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-muted-foreground">Você possui</p>
          <p className="font-bold">
            {size} ações {reserved > 0 ? ` (${reserved} reservadas)` : ""}
          </p>
        </div>

        <div>
          <p className="text-muted-foreground">Valor total da posição</p>
          <p className="font-bold">{displayMoney(position?.current_value ?? "0")}</p>
        </div>

        <div>
          <p className="text-muted-foreground">Preço médio</p>
          <p className="font-bold">{displayMoney(position?.avg_price ?? "0")}</p>
        </div>

        <div>
          <p className="text-muted-foreground">Preço atual</p>
          <p className="font-bold">{displayMoney(stock.close)}</p>
        </div>

        <div className="col-span-2">
          <p className="text-muted-foreground">Lucro / Prejuízo</p>
          <p className={clsx("font-bold", isLoss(returnValue) ? "text-red-600" : "text-green-600")}>
            {displayMoney(returnValue)} ({displayPercent(position?.return_pct ?? "0")})
          </p>
        </div>
      </div>
    </Card>
  );
}
