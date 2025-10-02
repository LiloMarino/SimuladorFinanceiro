import type { Stock } from "@/types";
import { Link } from "react-router-dom";


interface StockCardProps {
  stock: Stock;
}

export default function StockCard({ stock }: StockCardProps) {
  // Determina a cor do percentual
  const changeColor = stock.change_pct.includes("-") ? "text-red-500" : "text-green-500";

  return (
    <div
      className="bg-white rounded-lg shadow-md overflow-hidden transition-transform transform hover:-translate-y-0.5 hover:shadow-lg transition-all duration-200"
      data-ticker={stock.ticker}
    >
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex justify-between items-center">
          <h3 className="ticker font-bold text-lg">{stock.ticker}</h3>
          <span className={`${changeColor} text-sm font-medium`}>{stock.change_pct}</span>
        </div>
        <p className="name text-gray-500 text-sm">{stock.name}</p>
      </div>

      {/* Dados de preço */}
      <div className="p-4">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-500">Preço:</span>
          <span className="price font-medium">R$ {stock.price.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-500">Mínimo:</span>
          <span className="low font-medium">R$ {stock.low.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Máximo:</span>
          <span className="high font-medium">R$ {stock.high.toFixed(2)}</span>
        </div>
      </div>

      {/* Link de detalhes */}
      <div className="bg-gray-50 px-4 py-2 flex justify-end">
        <Link
          to={`/variable-income/${stock.ticker}`}
          className="details-link text-blue-600 text-sm font-medium hover:text-blue-800"
        >
          Ver
        </Link>
      </div>
    </div>
  );
}
