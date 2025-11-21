import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWallet, faChartLine, faCoins, faMoneyBillWave, faEye } from "@fortawesome/free-solid-svg-icons";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/shared/components/ui/table";
import { Button } from "@/shared/components/ui/button";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { Spinner } from "@/shared/components/ui/spinner";
import usePageLabel from "@/shared/hooks/usePageLabel";
import type { EconomicIndicators, PortfolioState, Stock } from "@/types";
import { formatMoney } from "@/shared/lib/utils/formatting";
import { Link } from "react-router-dom";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { SummaryCard } from "@/features/portfolio/components/summary-card";

export default function PortfolioPage() {
  usePageLabel("Carteira");
  // Busca dados da carteira
  const { data: portfolioData, loading: portfolioLoading } = useQueryApi<PortfolioState>("/api/portfolio");

  // Busca dados econômicos
  const { data: economicIndicatorsData, loading: economicIndicatorsLoading } =
    useQueryApi<EconomicIndicators>("/api/economic-indicators");

  // Busca os valores das ações e os atualiza em tempo real
  const { data: stocks, setData: setStocks } = useQueryApi<Stock[]>("/api/variable-income");
  useRealtime("stocks_update", (data) => {
    setStocks(data.stocks);
  });

  if (portfolioLoading) {
    return (
      <section className="flex min-h-[80vh] items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </section>
    );
  } else if (!portfolioData) {
    return <div>Falha ao carregar carteira</div>;
  }

  function getCurrentPrice(ticker: string): number | undefined {
    return stocks?.find((s) => s.ticker === ticker)?.price;
  }

  const { cash, variable_income, fixed_income } = portfolioData;

  const variablePositions = variable_income.map((pos) => {
    const currentPrice = getCurrentPrice(pos.ticker) ?? pos.avg_price;
    const investedValue = pos.avg_price * pos.size;
    const currentValue = currentPrice * pos.size;
    const returnValue = currentValue - investedValue;
    const returnPercent = ((returnValue / investedValue) * 100).toFixed(2) + "%";

    return {
      ticker: pos.ticker,
      averagePrice: pos.avg_price,
      quantity: pos.size,
      currentPrice,
      investedValue,
      currentValue,
      portfolioPercent: "0%", // definido depois
      returnValue,
      returnPercent,
    };
  });
  const fixedPositions: unknown[] = []; // ❌ fixed_income é unknown[]

  const variableIncomeValue = variablePositions.reduce((sum, p) => sum + p.currentValue, 0);
  const fixedIncomeValue = 0; // ❌ Não é possível inferir com os dados atuais
  const portfolioValue = variableIncomeValue + fixedIncomeValue;
  variablePositions.forEach((pos) => {
    pos.portfolioPercent = ((pos.currentValue / portfolioValue) * 100).toFixed(2) + "%";
  });

  const variableIncomePct = ((variableIncomeValue / portfolioValue) * 100).toFixed(1);
  const fixedIncomePct = ((fixedIncomeValue / portfolioValue) * 100).toFixed(1);
  const dividend = 0; // ❌ Não é possível inferir com os dados atuais
  const portfolioPct = 0; // ❌ Não é possível inferir com os dados atuais

  console.log(portfolioData);

  return (
    <section className="p-4 space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SummaryCard
          title="Valor Total"
          value={portfolioValue}
          subtitle={`${portfolioPct}% desde o início`}
          icon={faWallet}
          iconBg="bg-green-100"
          color="text-green-600"
        />
        <SummaryCard
          title="Renda Variável"
          value={variableIncomeValue}
          subtitle={`${variableIncomePct}% da carteira`}
          icon={faChartLine}
          iconBg="bg-blue-100"
          color="text-blue-600"
        />
        <SummaryCard
          title="Renda Fixa"
          value={fixedIncomeValue}
          subtitle={`${fixedIncomePct}% da carteira`}
          icon={faCoins}
          iconBg="bg-yellow-100"
          color="text-yellow-600"
        />
        <SummaryCard
          title="Proventos"
          value={dividend}
          subtitle="Últimos 12 meses"
          icon={faMoneyBillWave}
          iconBg="bg-purple-100"
          color="text-purple-600"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="font-semibold">Evolução do Patrimônio</h3>
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            <p className="text-gray-500">Gráfico de evolução do patrimônio</p>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="font-semibold">Distribuição da Carteira</h3>
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            <p className="text-gray-500">Gráfico de distribuição por setor/ativo</p>
          </div>
        </Card>
      </div>

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
              <p className="font-bold">{economicIndicatorsData.cdi.toFixed(2)}%</p>
            </div>
            <div className="flex-1 min-w-[120px] border rounded p-4 text-center">
              <p className="text-gray-600 text-sm">SELIC</p>
              <p className="font-bold">{economicIndicatorsData.selic.toFixed(2)}%</p>
            </div>
            <div className="flex-1 min-w-[120px] border rounded p-4 text-center">
              <p className="text-gray-600 text-sm">IPCA (12m)</p>
              <p className="font-bold">{economicIndicatorsData.ipca.toFixed(2)}%</p>
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
                    <TableCell>{pos.portfolioPercent}</TableCell>
                    <TableCell className={pos.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                      {formatMoney(pos.returnValue)}
                    </TableCell>
                    <TableCell className={pos.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                      {pos.returnPercent}
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
                    <TableHead key={h}>{h}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {fixedPositions.map((pos) => (
                  <TableRow key={pos.ticker}>
                    <TableCell>{pos.ticker}</TableCell>
                    <TableCell>
                      R$ {pos.investedValue?.toLocaleString("pt-BR", { minimumFractionDigits: 2 }) ?? "-"}
                    </TableCell>
                    <TableCell>R$ {pos.currentValue.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</TableCell>
                    <TableCell>{pos.rate ?? "-"}</TableCell>
                    <TableCell>{pos.portfolioPercent}</TableCell>
                    <TableCell>
                      {pos.returnValue?.toLocaleString("pt-BR", { minimumFractionDigits: 2 }) ?? "-"}
                    </TableCell>
                    <TableCell className={pos.returnPercent.startsWith("-") ? "text-red-600" : "text-green-600"}>
                      {pos.returnPercent}
                    </TableCell>
                    <TableCell>
                      <Button variant="link" onClick={() => alert(`Detalhes do ativo ${pos.ticker}`)}>
                        <FontAwesomeIcon icon={faEye} /> Detalhes
                      </Button>
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
