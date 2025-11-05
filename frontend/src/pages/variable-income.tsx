import StockCard from "@/components/stock-card";
import { Spinner } from "@/components/ui/spinner";
import { useQueryApi } from "@/hooks/useQueryApi";
import { useRealtime } from "@/hooks/useRealtime";
import type { Stock } from "@/types";

export default function VariableIncomePage() {
  const { data: stocks, setData: setStocks, loading } = useQueryApi<Stock[]>("/api/variable-income");

  useRealtime("stocks_update", (data) => {
    setStocks(data.stocks);
  });

  if (loading) {
    return (
      <section className="flex min-h-[80vh] items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </section>
    );
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
