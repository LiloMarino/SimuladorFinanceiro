import { Link, useParams } from "react-router-dom";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { Button } from "@/shared/components/ui/button";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ErrorPage } from "@/pages/error";
import { ErrorState } from "@/shared/components/error-state";
import { StockAnalysis } from "../components/stock-analysis";
import { StockHeader } from "../components/stock-header";
import { OrderBookCard } from "../components/order-book-card";
import { OrderTicket } from "../components/order-ticket";
import { PositionCard } from "../components/position-card";
import { usePendingOrders } from "../hooks/queries/usePendingOrders";
import { useVariableIncomeStock } from "../hooks/queries/useVariableIncomeStock";
import { useIndicatorSettings } from "../hooks/queries/useIndicatorSettings";
import { usePortfolioPosition } from "../hooks/queries/usePortfolioPosition";

export default function VariableIncomeDetailPage() {
  usePageLabel("Renda variável");
  const { ticker } = useParams<{ ticker: string }>();
  const { data: stock, isLoading, error, refetch } = useVariableIncomeStock(ticker);
  const orders = usePendingOrders(ticker);
  const { data: position } = usePortfolioPosition(ticker);
  const { data: indicatorSettings } = useIndicatorSettings();

  if (error && error.status !== 404) {
    return (
      <ErrorState
        title="Não deu para carregar esse ativo"
        description="Confira a conexão e tente novamente."
        error={error}
        onRetry={() => void refetch()}
      />
    );
  }

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
          {indicatorSettings ? (
            <StockAnalysis ticker={stock.ticker} history={stock.history} settings={indicatorSettings} />
          ) : (
            <Skeleton className="h-96" />
          )}
          <OrderBookCard ticker={stock.ticker} orders={orders} />
        </div>
        <div className="grid gap-5">
          <OrderTicket
            key={stock.ticker}
            ticker={stock.ticker}
            assetClass={stock.asset_class}
            todayPrice={stock.close}
          />
          <PositionCard ticker={stock.ticker} position={position ?? null} />
          <Button variant="link" size="sm" nativeButton={false} render={<Link to="/portfolio" />}>
            Ver carteira
          </Button>
        </div>
      </div>
    </>
  );
}
