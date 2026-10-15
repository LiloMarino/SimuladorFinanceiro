import { Link, useParams } from "react-router-dom";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { Button } from "@/shared/components/ui/button";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ErrorPage } from "@/pages/error";
import { StockChart } from "../components/stock-chart";
import { StockHeader } from "../components/stock-header";
import { OrderBookCard } from "../components/order-book-card";
import { OrderTicket } from "../components/order-ticket";
import { PositionCard } from "../components/position-card";
import { usePendingOrders } from "../hooks/usePendingOrders";
import { useVariableIncomeStock } from "../hooks/queries/useVariableIncomeStock";
import { usePortfolioPosition } from "../hooks/queries/usePortfolioPosition";

export default function VariableIncomeDetailPage() {
  usePageLabel("Renda variável");
  const { ticker } = useParams<{ ticker: string }>();
  const { data: stock, isLoading } = useVariableIncomeStock(ticker);
  const orders = usePendingOrders(ticker);
  const { data: position } = usePortfolioPosition(ticker);

  if (isLoading) {
    return (
      <div className="grid gap-5">
        <Skeleton className="h-16" />
        <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_380px]">
          <Skeleton className="h-96" />
          <Skeleton className="h-96" />
        </div>
      </div>
    );
  }

  if (!stock || !ticker) {
    return (
      <ErrorPage
        title={`${ticker} não está na base`}
        message="Confira o código ou escolha um ativo na lista."
        actionLabel="Ver ativos"
        actionHref="/variable-income"
      />
    );
  }

  return (
    <>
      <StockHeader stock={stock} />
      <div className="grid items-start gap-5 lg:grid-cols-[minmax(0,1fr)_380px]">
        <div className="grid gap-5">
          <StockChart ticker={stock.ticker} initialData={stock.history} />
          <OrderBookCard ticker={stock.ticker} orders={orders} />
        </div>
        <div className="grid gap-5">
          <OrderTicket ticker={stock.ticker} assetClass={stock.asset_class} todayPrice={stock.close} />
          <PositionCard ticker={stock.ticker} position={position ?? null} />
          <Button variant="link" size="sm" nativeButton={false} render={<Link to="/portfolio" />}>
            Ver carteira
          </Button>
        </div>
      </div>
    </>
  );
}
