import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { isSovereignAccount } from "@/shared/lib/active-account";
import { Button } from "@/shared/components/ui/button";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ErrorPage } from "@/pages/error";
import { ErrorState } from "@/shared/components/error-state";
import { FundDistributionsCard } from "@/shared/components/fund-distributions-card";
import { FundMetricsRow } from "@/shared/components/fund-metrics-row";
import { useFund } from "@/shared/hooks/queries/useFund";
import { FundAboutCard } from "../components/fund-about-card";
import { FundSaleCard } from "../components/fund-sale-card";
import { StockAnalysis } from "../components/stock-analysis";
import { StockHeader } from "../components/stock-header";
import { CorporateEventsCard } from "../components/corporate-events-card";
import { OrderBookCard } from "../components/order-book-card";
import { OrderTicket, type OrderPrefill } from "../components/order-ticket";
import { PositionCard } from "../components/position-card";
import { SovereignAccountNotice } from "../components/sovereign-account-notice";
import { StateCompanyChartCard } from "../components/state-company/state-company-chart-card";
import { StateCompanyHoldersCard } from "../components/state-company/state-company-holders-card";
import { StateCompanyMetricsRow } from "../components/state-company/state-company-metrics-row";
import { StateCompanyMonthsCard } from "../components/state-company/state-company-months-card";
import { StateCompanyPolicyCard } from "../components/state-company/state-company-policy-card";
import { usePendingOrders } from "../hooks/queries/usePendingOrders";
import { useVariableIncomeStock } from "../hooks/queries/useVariableIncomeStock";
import { useHousePicks } from "../hooks/queries/useHousePicks";
import { useIndicatorSettings } from "../hooks/queries/useIndicatorSettings";
import { usePortfolioPosition } from "../hooks/queries/usePortfolioPosition";
import { useStateCompanyDetail } from "../hooks/queries/useStateCompanyDetail";
import { describeOffer, typicalPrice } from "../lib/order-book";
import { displayMoney } from "@/shared/lib/utils/display";
import type { FundDetails, Order, StateCompanyDetail, StockDetails } from "@/types";

/** Carrega a gestora dona da cota e só então monta o corpo, que recebe a gestora pronta. */
function FundStockLoader({ stock, fundId }: { stock: StockDetails; fundId: number }) {
  const { data: fund, error, refetch } = useFund(fundId);

  if (error) {
    return (
      <ErrorState
        title="Não deu para carregar a gestora dessa cota"
        description="Confira a conexão e tente novamente."
        error={error}
        onRetry={() => void refetch()}
      />
    );
  }

  if (!fund) return <DetailSkeleton />;

  return <StockDetailsBody stock={stock} fund={fund} stateCompany={null} />;
}

/** Carrega a estatal da ação (nula para as demais) e só então monta o corpo, que recebe o dado resolvido. */
function StockLoader({ stock }: { stock: StockDetails }) {
  const { data: stateCompany, error, refetch } = useStateCompanyDetail(stock.ticker);

  if (error) {
    return (
      <ErrorState
        title="Não deu para carregar os dados da estatal"
        description="Confira a conexão e tente novamente."
        error={error}
        onRetry={() => void refetch()}
      />
    );
  }

  if (stateCompany === undefined) return <DetailSkeleton />;

  return <StockDetailsBody stock={stock} fund={null} stateCompany={stateCompany} />;
}

function DetailSkeleton() {
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

type StockDetailsBodyProps = {
  stock: StockDetails;
  /** A gestora dona da cota; `null` para os demais ativos */
  fund: FundDetails | null;
  /** A estatal dona da ação; `null` para os demais ativos */
  stateCompany: StateCompanyDetail | null;
};

function StockDetailsBody({ stock, fund, stateCompany }: StockDetailsBodyProps) {
  const {
    orders,
    isLoading: ordersLoading,
    error: ordersError,
    refetch: refetchOrders,
  } = usePendingOrders(stock.ticker);
  const [prefill, setPrefill] = useState<OrderPrefill>();
  const { data: position } = usePortfolioPosition(stock.ticker);
  const { data: indicatorSettings } = useIndicatorSettings();
  const { fund: activeAccount } = useActiveAccount();
  const { data: housePicks } = useHousePicks();

  // Clicar numa venda prepara a compra limitada ao preço dela; numa compra, a venda
  const pickOffer = (order: Order) => {
    const limitPrice = order.limit_price;
    if (limitPrice === null) return;
    setPrefill((previous) => ({
      id: (previous?.id ?? 0) + 1,
      action: order.action === "sell" ? "buy" : "sell",
      limitPrice,
      source: describeOffer(order, displayMoney(limitPrice)),
    }));
  };

  return (
    <>
      <StockHeader stock={stock} stateCompany={stateCompany} housePick={housePicks?.get(stock.ticker)} />
      {fund && (
        <>
          {/* Cards da gestora */}
          <FundSaleCard fund={fund} />
          <FundMetricsRow fund={fund} viewer={fund.my_role !== "manager"} />
        </>
      )}
      {stateCompany && <StateCompanyMetricsRow company={stateCompany} />}
      <div className="grid items-start gap-5 lg:grid-cols-[minmax(0,1fr)_380px]">
        <div className="grid gap-5">
          {indicatorSettings ? (
            <StockAnalysis ticker={stock.ticker} history={stock.history} settings={indicatorSettings} />
          ) : (
            <Skeleton className="h-96" />
          )}
          {isSovereignAccount(activeAccount) && <SovereignAccountNotice />}
          {fund && (
            <>
              <FundAboutCard fund={fund} />
              <FundDistributionsCard fund={fund} />
            </>
          )}
          {stateCompany && stateCompany.months.length > 0 && (
            <>
              {/* Cards da estatal */}
              <StateCompanyChartCard months={stateCompany.months} />
              <StateCompanyMonthsCard months={stateCompany.months} />
            </>
          )}
          {stateCompany?.holders && (
            <div className="grid items-start gap-5 md:grid-cols-2">
              <StateCompanyHoldersCard holders={stateCompany.holders} />
              <StateCompanyPolicyCard policies={stateCompany.policies} dividend_policy={stateCompany.dividend_policy} />
            </div>
          )}
          <CorporateEventsCard ticker={stock.ticker} />
          <OrderBookCard
            ticker={stock.ticker}
            orders={orders}
            typicalPrice={typicalPrice(stock)}
            isLoading={ordersLoading}
            error={ordersError}
            onRetry={() => void refetchOrders()}
            onPick={pickOffer}
          />
        </div>
        <div className="grid gap-5 lg:sticky lg:top-[89px] lg:max-h-[calc(100vh-105px)] lg:overflow-auto">
          <OrderTicket
            key={stock.ticker}
            ticker={stock.ticker}
            assetClass={stock.asset_class}
            todayPrice={stock.close}
            prefill={prefill}
            fund={fund ?? undefined}
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

export default function VariableIncomeDetailPage() {
  usePageLabel("Renda variável");
  const { ticker } = useParams<{ ticker: string }>();
  const { data: stock, isLoading, error, refetch } = useVariableIncomeStock(ticker);

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

  if (isLoading) return <DetailSkeleton />;

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

  // A gestora e a estatal chegam resolvidas: cada uma passa pelo seu carregador antes do corpo
  return stock.fund_id === null ? (
    <StockLoader stock={stock} />
  ) : (
    <FundStockLoader stock={stock} fundId={stock.fund_id} />
  );
}
