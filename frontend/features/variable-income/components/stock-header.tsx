import type { StockDetails } from "@/types";
import clsx from "clsx";
import { TrendingDown, TrendingUp } from "lucide-react";

export function StockHeader({ stock }: { stock: StockDetails }) {
  const isPositive = stock.change >= 0;
  return (
    <div className="flex justify-between items-center mb-6">
      <div>
        <h2 className="text-2xl font-bold">{stock.ticker}</h2>
        <p className="text-muted-foreground">{stock.name}</p>
      </div>
      <div className="text-right">
        <h3 className="text-3xl font-bold text-gray-800 dark:text-gray-100">R$ {stock.close.toFixed(2)}</h3>
        <div
          className={clsx(
            "flex items-center justify-end gap-1 font-medium",
            isPositive ? "text-green-600" : "text-red-600"
          )}
        >
          {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          <span>{stock.change_pct}</span>
          <span className="text-muted-foreground">(R$ {stock.change.toFixed(2)})</span>
        </div>
      </div>
    </div>
  );
}
