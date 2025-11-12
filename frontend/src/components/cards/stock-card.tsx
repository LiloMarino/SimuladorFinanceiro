import type { Stock } from "@/types";
import BaseCard from "./base-card";

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
        { label: "Preço:", value: `R$ ${stock.price.toFixed(2)}` },
        { label: "Mínimo:", value: `R$ ${stock.low.toFixed(2)}` },
        { label: "Máximo:", value: `R$ ${stock.high.toFixed(2)}` },
      ]}
      footer={{
        linkTo: `/variable-income/${stock.ticker}`,
        label: "Ver",
      }}
    />
  );
}
