import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWallet, faChartLine, faCoins, faMoneyBillWave, faEye } from "@fortawesome/free-solid-svg-icons";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { useQueryApi } from "@/hooks/useQueryApi";
import { Spinner } from "@/components/ui/spinner";
import { SummaryCard } from "@/components/summary-card";
import usePageLabel from "@/hooks/usePageLabel";
import type { PortfolioState } from "@/types";
import { formatPrice } from "@/lib/utils/formatting";
import { Link } from "react-router-dom";

type EconomicIndicators = {
  cdi: number;
  selic: number;
  ipca: number;
};

export default function PortfolioPage() {
  usePageLabel("Carteira");

  const { data: portfolioData, loading: portfolioLoading } = useQueryApi<PortfolioState>("/api/portfolio", {
    initialFetch: true,
  });

  const { data: economicIndicatorsData, loading: economicIndicatorsLoading } = useQueryApi<EconomicIndicators>(
    "/api/economic-indicators",
    { initialFetch: true }
  );

  if (portfolioLoading) {
    return (
      <section className="flex min-h-[80vh] items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </section>
    );
  } else if (!portfolioData) {
    return <div>Falha ao carregar carteira</div>;
  }

  const { cash, variable_income, fixed_income } = portfolioData;

  const variableIncomeValue = variable_income.reduce(
    (total, position) => total + position.avg_price * position.size,
    0
  );
  const fixedIncomeValue = 0; // ❌ Não é possível inferir com os dados atuais
  const portfolioValue = variableIncomeValue + fixedIncomeValue;
  const variableIncomePct = ((variableIncomeValue / portfolioValue) * 100).toFixed(1);
  const fixedIncomePct = ((fixedIncomeValue / portfolioValue) * 100).toFixed(1);
  const dividend = 0; // ❌ Não é possível inferir com os dados atuais
  const portfolioPct = 0; // ❌ Não é possível inferir com os dados atuais

  const variablePositions = variable_income.map((pos) => ({
    ticker: pos.ticker,
    averagePrice: pos.avg_price,
    quantity: pos.size,
    currentValue: pos.avg_price * pos.size, // usando preço médio
    portfolioPercent: (((pos.avg_price * pos.size) / portfolioValue) * 100).toFixed(2) + "%",
    returnValue: "N/D", // ❌ requer preço atual
    returnPercent: "N/D", // ❌ requer preço atual
  }));

  const fixedPositions: unknown[] = []; // ❌ fixed_income é unknown[]

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
                    <TableCell>{formatPrice(pos.averagePrice)}</TableCell>
                    <TableCell>{pos.quantity}</TableCell>
                    <TableCell>{formatPrice(pos.currentValue)}</TableCell>
                    <TableCell>{pos.portfolioPercent}</TableCell>
                    <TableCell>{pos.returnValue}</TableCell>
                    <TableCell>{pos.returnPercent}</TableCell>
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
