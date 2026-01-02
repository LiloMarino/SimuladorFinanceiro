import BaseCard from "@/shared/components/base-card";
import { displayMoney } from "@/shared/lib/utils/display";
import type { Stock } from "@/types";

interface StockCardProps {
  stock: Stock;
}

export default function StockCard({ stock }: StockCardProps) {
  const changeColor = stock.change_pct.includes("-") ? "text-red-500" : "text-green-500";

  return (
    <BaseCard
      header={{
        title: stock.ticker,
        subtitle: stock.name,
        badge: <span className={`${changeColor} text-sm font-medium`}>{stock.change_pct}</span>,
      }}
      fields={[
        { label: "Preço:", value: displayMoney(stock.close) },
        { label: "Mínimo:", value: displayMoney(stock.low) },
        { label: "Máximo:", value: displayMoney(stock.high) },
      ]}
      footer={{
        linkTo: `/variable-income/${stock.ticker}`,
        label: "Ver",
      }}
    />
  );
}
