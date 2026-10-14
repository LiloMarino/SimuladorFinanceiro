import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { displayCompactNumber, displayMoney, displaySignedPercent } from "@/shared/lib/utils/display";
import type { StockDetails } from "@/types";

const CLASS_LABELS: Record<StockDetails["asset_class"], string> = {
  STOCK: "Ação",
  FII: "FII",
  ETF: "ETF",
  BDR: "BDR",
};

/** Cabeçalho do ativo: código, nome, o pregão do dia e o preço. */
export function StockHeader({ stock }: { stock: StockDetails }) {
  const up = stock.change >= 0;
  const ohlc = [
    { label: "Abertura", value: displayMoney(stock.open) },
    { label: "Mínima", value: displayMoney(stock.low) },
    { label: "Máxima", value: displayMoney(stock.high) },
    { label: "Volume", value: displayCompactNumber(stock.volume) },
  ];

  return (
    <header className="flex flex-wrap items-end justify-between gap-4">
      <div className="grid gap-1.5">
        <Button
          variant="link"
          size="sm"
          nativeButton={false}
          render={<Link to="/variable-income" />}
          className="self-start"
        >
          <ArrowLeft />
          Renda variável
        </Button>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="font-mono text-[28px] font-semibold">{stock.ticker}</h1>
          <span className="text-muted-foreground">{stock.name}</span>
          <Badge variant="secondary">{CLASS_LABELS[stock.asset_class]}</Badge>
        </div>
      </div>

      <div className="flex flex-wrap items-end gap-6">
        {ohlc.map((item) => (
          <div key={item.label} className="grid">
            <span className="text-xs font-medium text-muted-foreground">{item.label}</span>
            <span className="font-mono">{item.value}</span>
          </div>
        ))}
        <div className="grid justify-items-end">
          <span className="font-mono text-[28px] leading-none font-semibold">{displayMoney(stock.close)}</span>
          <span className={up ? "text-[13px] text-success" : "text-[13px] text-destructive"}>
            {up ? "▲" : "▼"} {displaySignedPercent(stock.change_pct)} · {up ? "+" : ""}
            {displayMoney(stock.change)} hoje
          </span>
        </div>
      </div>
    </header>
  );
}
