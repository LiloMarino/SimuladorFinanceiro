import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWallet, faChartLine, faCoins, faMoneyBillWave, faEye } from "@fortawesome/free-solid-svg-icons";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/shared/components/ui/table";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { Spinner } from "@/shared/components/ui/spinner";
import usePageLabel from "@/shared/hooks/usePageLabel";
import type { EconomicIndicators, PortfolioState, Stock } from "@/types";
import { formatMoney, formatPercent } from "@/shared/lib/utils/formatting";
import { Link } from "react-router-dom";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { SummaryCard } from "@/features/portfolio/components/summary-card";
import { PortfolioCharts } from "../components/portfolio-charts";
import { useMemo } from "react";
import { calculatePortfolioView } from "../lib/portfolio-calculator";
export default function PortfolioPage() {
  usePageLabel("Carteira");
  // Busca dados da carteira
  const {
    data: portfolioData,
    setData: setPortfolioData,
    loading: portfolioLoading,
  } = useQueryApi<PortfolioState>("/api/portfolio");

  // Busca dados econômicos
  const { data: economicIndicatorsData, loading: economicIndicatorsLoading } =
    useQueryApi<EconomicIndicators>("/api/economic-indicators");

  // Atualiza o histórico patrimonial em tempo real
  useRealtime("snapshot_update", ({ snapshot }) => {
    setPortfolioData((prev) => {
      if (!prev) return prev;

      const map = new Map(prev.patrimonial_history.map((h) => [h.snapshot_date, h]));

      map.set(snapshot.snapshot_date, {
        snapshot_date: snapshot.snapshot_date,
        total_networth: snapshot.total_networth,
        total_equity: snapshot.total_equity,
        total_fixed: snapshot.total_fixed,
        total_cash: snapshot.total_cash,
      });

      return {
        ...prev,
        patrimonial_history: Array.from(map.values()).sort((a, b) => a.snapshot_date.localeCompare(b.snapshot_date)),
      };
    });
  });

  // Busca os valores das ações e os atualiza em tempo real
  const { data: stocks, setData: setStocks } = useQueryApi<Stock[]>("/api/variable-income");
  useRealtime("stocks_update", (data) => {
    setStocks(data.stocks);
  });

  // Atualiza os valores da renda fixa em tempo real
  useRealtime("fixed_income_position_update", (data) => {
    setPortfolioData((prev) => {
      if (!prev) return prev;

      return {
        ...prev,
        fixed_income: data.positions,
      };
    });
  });

  const view = useMemo(() => {
    if (!portfolioData) return null;
    return calculatePortfolioView(portfolioData, stocks);
  }, [portfolioData, stocks]);

  if (portfolioLoading) {
    return (
      <section className="flex min-h-[80vh] items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </section>
    );
  } else if (!portfolioData) {
    return <div>Falha ao carregar carteira</div>;
  }

  if (!view) return null;
  const { patrimonial_history } = portfolioData;
  const {
    variablePositions,
    fixedPositions,
    variableIncomeValue,
    fixedIncomeValue,
    variableIncomePct,
    totalNetWorth,
    investedValue,
    investedPct,
    fixedIncomePct,
    totalReturnPct,
  } = view;

  return (
    <section className="p-4 space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SummaryCard
          title="Patrimônio Total"
          value={totalNetWorth}
          subtitle={`${formatPercent(totalReturnPct)} desde o início`}
          icon={faWallet}
          iconBg="bg-green-100"
          color="text-green-600"
        />

        <SummaryCard
          title="Total Investido"
          value={investedValue}
          subtitle={`${formatPercent(investedPct)} do patrimônio`}
          icon={faMoneyBillWave}
          iconBg="bg-purple-100"
          color="text-purple-600"
        />

        <SummaryCard
          title="Renda Variável"
          value={variableIncomeValue}
          subtitle={`${formatPercent(variableIncomePct)} da carteira`}
          icon={faChartLine}
          iconBg="bg-blue-100"
          color="text-blue-600"
        />

        <SummaryCard
          title="Renda Fixa"
          value={fixedIncomeValue}
          subtitle={`${formatPercent(fixedIncomePct)} da carteira`}
          icon={faCoins}
          iconBg="bg-yellow-100"
          color="text-yellow-600"
        />
      </div>

      {/* Charts */}
      <PortfolioCharts
        variablePositions={variablePositions}
        fixedPositions={fixedPositions}
        patrimonialHistory={patrimonial_history}
      />

      {/* Economic Indicators */}
      <Card className="p-6">
        <h3 className="font-semibold mb-4">Indicadores Econômicos</h3>
        {economicIndicatorsLoading || !economicIndicatorsData ? (
          <div className="flex items-center justify-center h-32">
            <Spinner className="h-8 w-8 text-muted-foreground" />
          </div>
        ) : (
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[120px] border rounded p-4 text-center">
              <p className="text-gray-600 text-sm">CDI</p>
              <p className="font-bold">{formatPercent(economicIndicatorsData.cdi / 100)}</p>
            </div>
            <div className="flex-1 min-w-[120px] border rounded p-4 text-center">
              <p className="text-gray-600 text-sm">SELIC</p>
              <p className="font-bold">{formatPercent(economicIndicatorsData.selic / 100)}</p>
            </div>
            <div className="flex-1 min-w-[120px] border rounded p-4 text-center">
              <p className="text-gray-600 text-sm">IPCA (12m)</p>
              <p className="font-bold">{formatPercent(economicIndicatorsData.ipca / 100)}</p>
            </div>
          </div>
        )}
      </Card>

      {/* Positions Tables */}
      <div className="space-y-6">
        {/* Renda Variável */}
        <Card>
          <CardHeader>
            <CardTitle>Renda Variável</CardTitle>
          </CardHeader>
          <CardContent className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  {[
                    "Ativo",
                    "Preço Médio",
                    "Preço Atual",
                    "Quantidade",
                    "Valor Total",
                    "% Carteira",
                    "Retorno (R$)",
                    "Retorno (%)",
                    "Ações",
                  ].map((h) => (
                    <TableHead className="text-center" key={h}>
                      {h}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {variablePositions.map((pos) => (
                  <TableRow className="text-center [&>td]:py-4" key={pos.ticker}>
                    <TableCell>{pos.ticker}</TableCell>
                    <TableCell>{formatMoney(pos.averagePrice)}</TableCell>
                    <TableCell>{formatMoney(pos.currentPrice)}</TableCell>
                    <TableCell>{pos.quantity}</TableCell>
                    <TableCell>{formatMoney(pos.currentValue)}</TableCell>
                    <TableCell>{formatPercent(pos.portfolioPercent)}</TableCell>
                    <TableCell className={pos.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                      {formatMoney(pos.returnValue)}
                    </TableCell>
                    <TableCell className={pos.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                      {formatPercent(pos.returnPercent)}
                    </TableCell>
                    <TableCell>
                      <Link
                        to={`/variable-income/${pos.ticker}`}
                        className="text-blue-600 hover:text-blue-800 text-sm flex items-center justify-center"
                      >
                        <FontAwesomeIcon icon={faEye} className="mr-1" />
                        Detalhes
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Renda Fixa */}
        <Card>
          <CardHeader>
            <CardTitle>Renda Fixa</CardTitle>
          </CardHeader>
          <CardContent className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  {[
                    "Ativo",
                    "Valor Investido",
                    "Valor Atual",
                    "Taxa",
                    "% Carteira",
                    "Retorno (R$)",
                    "Retorno (%)",
                    "Ações",
                  ].map((h) => (
                    <TableHead className="text-center" key={h}>
                      {h}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {fixedPositions.map((pos) => (
                  <TableRow className="text-center [&>td]:py-4" key={pos.name}>
                    <TableCell>{pos.name}</TableCell>
                    <TableCell>{formatMoney(pos.investedValue)}</TableCell>
                    <TableCell>{formatMoney(pos.currentValue)}</TableCell>
                    <TableCell>
                      {pos.interestRate ? `${pos.interestRate.toFixed(2)}% ${pos.rateIndex}` : pos.rateIndex}
                    </TableCell>
                    <TableCell>{formatPercent(pos.portfolioPercent)}</TableCell>
                    <TableCell className={pos.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                      {formatMoney(pos.returnValue)}
                    </TableCell>
                    <TableCell className={pos.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                      {formatPercent(pos.returnPercent)}
                    </TableCell>
                    <TableCell>
                      <Link
                        to={`/fixed-income/${pos.uuid}`}
                        className="text-blue-600 hover:text-blue-800 text-sm flex items-center justify-center"
                      >
                        <FontAwesomeIcon icon={faEye} className="mr-1" />
                        Detalhes
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
