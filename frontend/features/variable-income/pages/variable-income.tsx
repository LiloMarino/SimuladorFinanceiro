import StockCard from "@/features/variable-income/components/stock-card";
import { LoadingPage } from "@/pages/loading";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { Stock } from "@/types";

export default function VariableIncomePage() {
  const { data: stocks, setData: setStocks, loading } = useQueryApi<Stock[]>("/api/variable-income");

  useRealtime("stocks_update", (data) => {
    setStocks(data.stocks);
  });

  if (loading) {
    return <LoadingPage />;
  }

  return (
    <section className="section-content p-4 ">
      {stocks && stocks.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {stocks.map((stock) => (
            <StockCard key={stock.ticker} stock={stock} />
          ))}
        </div>
      ) : (
        <div className="flex justify-center items-center h-full text-muted-foreground">Nenhum ativo encontrado.</div>
      )}
    </section>
  );
}
