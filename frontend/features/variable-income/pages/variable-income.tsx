import StockCard from "@/features/variable-income/components/stock-card";
import { ErrorPage } from "@/pages/error";
import { LoadingPage } from "@/pages/loading";
import { useVariableIncomeStocks } from "@/features/variable-income/hooks/queries/useVariableIncomeStocks";

export default function VariableIncomePage() {
  const { data: stocks, isLoading: loading, error } = useVariableIncomeStocks();

  if (loading) {
    return <LoadingPage />;
  }

  if (!stocks) {
    return (
      <ErrorPage
        code={String(error?.status) || "500"}
        title="Erro ao carregar ativos"
        message={String(error?.message)}
      />
    );
  }

  return (
    <section className="section-content p-4 ">
      {stocks.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {stocks.map((stock) => (
            <StockCard key={stock.ticker} stock={stock} />
          ))}
        </div>
      ) : (
        <div className="flex justify-center items-center h-full text-muted-foreground">Nenhum ativo disponível.</div>
      )}
    </section>
  );
}
