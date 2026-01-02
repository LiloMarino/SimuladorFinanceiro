import { displayMoney } from "@/shared/lib/utils/display";
import type { StockDetails } from "@/types";
import clsx from "clsx";

export function StockMiniStats({ stock }: { stock: StockDetails }) {
  const isPositive = stock.change >= 0;
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      {[
        { label: "Volume", value: stock.volume.toLocaleString() },
        { label: "Variação Dia", value: stock.change_pct, color: isPositive ? "text-green-600" : "text-red-600" },
        { label: "Mín. do Dia", value: displayMoney(stock.low) },
        { label: "Máx. do Dia", value: displayMoney(stock.high) },
      ].map((item, idx) => (
        <div key={idx} className="border rounded-lg p-4 bg-background hover:shadow-sm transition-shadow">
          <p className="text-muted-foreground text-sm">{item.label}</p>
          <p className={clsx("font-bold text-lg", item.color)}>{item.value}</p>
        </div>
      ))}
    </div>
  );
}
