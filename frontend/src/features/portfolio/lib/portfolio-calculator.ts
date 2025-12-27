import type { PortfolioState, Stock } from "@/types";

function calculateReturnMetrics(
  investedValue: number,
  currentValue: number
): {
  investedValue: number;
  currentValue: number;
  returnValue: number;
  returnPercent: number;
} {
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
  portfolioValue: number
) {
  positions.forEach((pos) => {
    pos.portfolioPercent = portfolioValue > 0 ? pos.currentValue / portfolioValue : 0;
  });
}

export function calculatePortfolioView(portfolioData: PortfolioState, stocks: Stock[] | null) {
  const variablePositions = calculateVariablePositions(portfolioData.variable_income, stocks);

  const fixedPositions = calculateFixedPositions(portfolioData.fixed_income);

  const variableIncomeValue = variablePositions.reduce((sum, p) => sum + p.currentValue, 0);

  const fixedIncomeValue = fixedPositions.reduce((sum, p) => sum + p.currentValue, 0);

  const portfolioValue = variableIncomeValue + fixedIncomeValue;

  applyPortfolioPercent(variablePositions, portfolioValue);
  applyPortfolioPercent(fixedPositions, portfolioValue);

  return {
    variablePositions,
    fixedPositions,
    variableIncomeValue,
    fixedIncomeValue,
    portfolioValue,
    variableIncomePct: portfolioValue > 0 ? variableIncomeValue / portfolioValue : 0,
    fixedIncomePct: portfolioValue > 0 ? fixedIncomeValue / portfolioValue : 0,
    dividend: 0,
    portfolioPct: 0,
  };
}
