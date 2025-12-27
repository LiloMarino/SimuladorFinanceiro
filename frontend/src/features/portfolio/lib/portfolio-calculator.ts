import type { PortfolioState, Stock } from "@/types";

type ReturnMetrics = {
  investedValue: number;
  currentValue: number;
  returnValue: number;
  returnPercent: number;
};

function calculateReturnMetrics(investedValue: number, currentValue: number): ReturnMetrics {
  const returnValue = currentValue - investedValue;
  const returnPercent = investedValue > 0 ? returnValue / investedValue : 0;

  return {
    investedValue,
    currentValue,
    returnValue,
    returnPercent,
  };
}

function calculateVariablePositions(variableIncome: PortfolioState["variable_income"], stocks: Stock[] | null) {
  const getCurrentPrice = (ticker: string) => stocks?.find((s) => s.ticker === ticker)?.close;

  return variableIncome.map((pos) => {
    const currentPrice = getCurrentPrice(pos.ticker) ?? pos.avg_price;

    const metrics = calculateReturnMetrics(pos.avg_price * pos.size, currentPrice * pos.size);

    return {
      ticker: pos.ticker,
      averagePrice: pos.avg_price,
      quantity: pos.size,
      currentPrice,
      ...metrics,
      portfolioPercent: 0,
    };
  });
}

function calculateFixedPositions(fixedIncome: PortfolioState["fixed_income"]) {
  return fixedIncome.map((pos) => {
    const metrics = calculateReturnMetrics(pos.total_applied, pos.current_value);

    return {
      uuid: pos.asset.asset_uuid,
      name: pos.asset.name,
      issuer: pos.asset.issuer,
      rateIndex: pos.asset.rate_index,
      interestRate: pos.asset.interest_rate,
      ...metrics,
      portfolioPercent: 0,
    };
  });
}

function applyPortfolioPercent<T extends { currentValue: number; portfolioPercent: number }>(
  positions: T[],
  total: number
) {
  positions.forEach((pos) => {
    pos.portfolioPercent = total > 0 ? pos.currentValue / total : 0;
  });
}

export function calculatePortfolioView(portfolioData: PortfolioState, stocks: Stock[] | null) {
  // Obtém as posições com suas métricas
  const variablePositions = calculateVariablePositions(portfolioData.variable_income, stocks);
  const fixedPositions = calculateFixedPositions(portfolioData.fixed_income);

  // Obtém os valores totais
  const variableIncomeValue = variablePositions.reduce((sum, p) => sum + p.currentValue, 0);
  const fixedIncomeValue = fixedPositions.reduce((sum, p) => sum + p.currentValue, 0);
  const investedValue = variableIncomeValue + fixedIncomeValue;
  const cashValue = portfolioData.cash;
  const totalNetWorth = investedValue + cashValue;

  applyPortfolioPercent(variablePositions, investedValue);
  applyPortfolioPercent(fixedPositions, investedValue);

  // Calcula os percentuais
  const variableIncomePct = investedValue > 0 ? variableIncomeValue / investedValue : 0;
  const fixedIncomePct = investedValue > 0 ? fixedIncomeValue / investedValue : 0;
  const investedPct = totalNetWorth > 0 ? investedValue / totalNetWorth : 0;
  const initialCapital = portfolioData.starting_cash;
  const totalReturnPct = initialCapital > 0 ? (totalNetWorth - initialCapital) / initialCapital : 0;

  return {
    variablePositions,
    fixedPositions,
    variableIncomeValue,
    fixedIncomeValue,
    investedValue,
    cashValue,
    totalNetWorth,
    variableIncomePct,
    fixedIncomePct,
    investedPct,
    totalReturnPct,
  };
}
