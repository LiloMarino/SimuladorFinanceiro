import { useEffect, useState } from "react";
import StockCard from "@/components/stock-card";
// import socket from "@/services/socket"; // placeholder para socket futuro

interface Stock {
  ticker: string;
  name: string;
  price: number;
  low: number;
  high: number;
  change_pct: string;
}

interface VariableIncomePageProps {
  initialStocks?: Stock[];
}

export default function VariableIncomePage({ initialStocks = [] }: VariableIncomePageProps) {
  initialStocks.push({
    change_pct: "0.00%",
    high: 0,
    low: 0,
    name: "Apple Inc.",
    price: 0,
    ticker: "AAPL",
  })
  const [stocks, setStocks] = useState<Stock[]>(initialStocks);

  useEffect(() => {
    // Aqui você poderia fazer:
    // socket.on("stocks_update", (data) => setStocks(data.stocks));

    // Simulação de atualização periódica
    const interval = setInterval(() => {
      setStocks((prev) =>
        prev.map((s) => ({
          ...s,
          price: s.price + (Math.random() - 0.5), // preço flutuando aleatório
          low: s.low + (Math.random() - 0.5),
          high: s.high + (Math.random() - 0.5),
          change_pct: `${((Math.random() - 0.5) * 2).toFixed(2)}%`,
        }))
      );
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <section id="variable-income" className="section-content p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {stocks.map((stock) => (
          <StockCard key={stock.ticker} stock={stock} />
        ))}
      </div>
    </section>
  );
}
