import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWallet, faChartLine, faCoins, faMoneyBillWave, faEye } from "@fortawesome/free-solid-svg-icons";

interface PortfolioProps {
  portfolioValue: number;
  variableIncome: number;
  fixedIncome: number;
  profit: number;
  variableIncomePct: number;
  fixedIncomePct: number;
  profitPct?: string;
  positions: {
    ticker: string;
    quantity: number | string;
    currentValue: number;
    portfolioPercent: string;
    returnPercent: string;
  }[];
}

export default function PortfolioPage({
  portfolioValue = 125430.65,
  variableIncome = 78450.25,
  fixedIncome = 46980.4,
  profit = 3450.8,
  variableIncomePct = 62.5,
  fixedIncomePct = 37.5,
  profitPct = "Últimos 12 meses",
  positions = [],
}: PortfolioProps) {
  const summaryCards = [
    {
      title: "Valor Total",
      value: portfolioValue,
      icon: faWallet,
      iconBg: "bg-green-100",
      iconColor: "text-green-600",
      subtitle: "+12.3% desde o início",
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

  const economicIndicators = [
    { label: "CDI", value: "11,65%" },
    { label: "SELIC", value: "11,25%" },
    { label: "IPCA (12m)", value: "4,50%" },
    { label: "IBOVESPA", value: "+8,32%" },
  ];

  positions = [
    {
      ticker: "PETR4",
      quantity: "1.000",
      currentValue: 32450.00,
      portfolioPercent: "25,8%",
      returnPercent: "+12,5%",
    },
    {
      ticker: "VALE3",
      quantity: "500",
      currentValue: 33945.00,
      portfolioPercent: "27,0%",
      returnPercent: "-4,2%",
    },
    {
      ticker: "Tesouro IPCA+ 2035",
      quantity: "-",
      currentValue: 25670.00,
      portfolioPercent: "20,4%",
      returnPercent: "+6,8%",
    },
    {
      ticker: "CDB 110% CDI",
      quantity: "-",
      currentValue: 21310.40,
      portfolioPercent: "17,0%",
      returnPercent: "+9,5%",
    },
  ];

  return (
    <section id="portfolio" className="section-content p-4 space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {summaryCards.map((card) => (
          <div key={card.title} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">{card.title}</p>
                <h3 className="text-2xl font-bold">
                  R$ {card.value.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </h3>
              </div>
              <div className={`${card.iconBg} p-3 rounded-full`}>
                <FontAwesomeIcon icon={card.icon} className={card.iconColor} />
              </div>
            </div>
            <p className={`${card.subtitleColor} mt-2`}>{card.subtitle}</p>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-4">Evolução do Patrimônio</h3>
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            <p className="text-gray-500">Gráfico de evolução do patrimônio</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-4">Distribuição da Carteira</h3>
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            <p className="text-gray-500">Gráfico de distribuição por setor/ativo</p>
          </div>
        </div>
      </div>

      {/* Economic Indicators */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold mb-4">Indicadores Econômicos</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {economicIndicators.map((ind) => (
            <div key={ind.label} className="border rounded p-4 text-center">
              <p className="text-gray-600 text-sm">{ind.label}</p>
              <p className="font-bold">{ind.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Positions Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <h3 className="font-semibold p-6">Posições Atuais</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {["Ativo", "Quantidade", "Valor Atual", "% Carteira", "Retorno", "Ações"].map((h) => (
                  <th
                    key={h}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {positions.map((pos) => (
                <tr key={pos.ticker}>
                  <td className="px-6 py-4 whitespace-nowrap">{pos.ticker}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{pos.quantity}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    R$ {pos.currentValue.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">{pos.portfolioPercent}</td>
                  <td
                    className={`px-6 py-4 whitespace-nowrap ${
                      pos.returnPercent.startsWith("-") ? "text-red-600" : "text-green-600"
                    }`}
                  >
                    {pos.returnPercent}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      className="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1"
                      onClick={() => alert(`Detalhes do ativo ${pos.ticker}`)}
                    >
                      <FontAwesomeIcon icon={faEye} /> Detalhes
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
