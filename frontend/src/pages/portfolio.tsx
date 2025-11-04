import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWallet, faChartLine, faCoins, faMoneyBillWave, faEye } from "@fortawesome/free-solid-svg-icons";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

interface Position {
  ticker: string;
  quantity?: number | string;
  averagePrice?: number;
  investedValue?: number;
  currentValue: number;
  rate?: string;
  portfolioPercent: string;
  returnValue?: number;
  returnPercent: string;
}

interface PortfolioPageProps {
  portfolioValue: number;
  variableIncome: number;
  fixedIncome: number;
  profit: number;
  variableIncomePct: number;
  fixedIncomePct: number;
  profitPct?: string;
  variablePositions: Position[];
  fixedPositions: Position[];
  economicIndicators: { label: string; value: string }[];
}

export default function PortfolioPage({
  portfolioValue = 0,
  variableIncome = 0,
  fixedIncome = 0,
  profit = 0,
  variableIncomePct = 0,
  fixedIncomePct = 0,
  profitPct = "Últimos 12 meses",
  variablePositions = [],
  fixedPositions = [],
  economicIndicators = [
    { label: "CDI", value: "11,65%" },
    { label: "SELIC", value: "11,25%" },
    { label: "IPCA (12m)", value: "4,50%" },
  ],
}: PortfolioPageProps) {
  const summaryCards = [
    {
      title: "Valor Total",
      value: portfolioValue,
      icon: faWallet,
      iconBg: "bg-green-100",
      iconColor: "text-green-600",
      subtitle: "+12,3% desde o início",
      subtitleColor: "text-green-600",
    },
    {
      title: "Renda Variável",
      value: variableIncome,
      icon: faChartLine,
      iconBg: "bg-blue-100",
      iconColor: "text-blue-600",
      subtitle: `${variableIncomePct}% da carteira`,
      subtitleColor: "text-blue-600",
    },
    {
      title: "Renda Fixa",
      value: fixedIncome,
      icon: faCoins,
      iconBg: "bg-yellow-100",
      iconColor: "text-yellow-600",
      subtitle: `${fixedIncomePct}% da carteira`,
      subtitleColor: "text-yellow-600",
    },
    {
      title: "Proventos",
      value: profit,
      icon: faMoneyBillWave,
      iconBg: "bg-purple-100",
      iconColor: "text-purple-600",
      subtitle: profitPct,
      subtitleColor: "text-purple-600",
    },
  ];

  return (
    <section className="p-4 space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {summaryCards.map((card) => (
          <Card key={card.title} className="p-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-gray-600">{card.title}</p>
                <h3 className="text-2xl font-bold">
                  R$ {card.value.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </h3>
                <p className={`${card.subtitleColor} mt-1`}>{card.subtitle}</p>
              </div>
              <div className={`${card.iconBg} w-12 h-12 flex items-center justify-center rounded-full`}>
                <FontAwesomeIcon icon={card.icon} className={card.iconColor} />
              </div>
            </div>
          </Card>
        ))}
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
        <h3 className="font-semibold">Indicadores Econômicos</h3>
        <div className="flex flex-wrap gap-4">
          {economicIndicators.map((ind) => (
            <div key={ind.label} className="flex-1 min-w-[120px] border rounded p-4 text-center">
              <p className="text-gray-600 text-sm">{ind.label}</p>
              <p className="font-bold">{ind.value}</p>
            </div>
          ))}
        </div>
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
                    <TableHead key={h}>{h}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {variablePositions.map((pos) => (
                  <TableRow key={pos.ticker}>
                    <TableCell>{pos.ticker}</TableCell>
                    <TableCell>
                      {pos.averagePrice?.toLocaleString("pt-BR", { minimumFractionDigits: 2 }) ?? "-"}
                    </TableCell>
                    <TableCell>{pos.quantity}</TableCell>
                    <TableCell>R$ {pos.currentValue.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</TableCell>
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
