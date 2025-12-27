import type { PortfolioState, Stock } from "@/types";

export function calculatePortfolioView(portfolioData: PortfolioState, stocks: Stock[] | null) {
  function getCurrentPrice(ticker: string): number | undefined {
    return stocks?.find((s) => s.ticker === ticker)?.close;
  }

  const { variable_income, fixed_income } = portfolioData;

  const variablePositions = variable_income.map((pos) => {
    const currentPrice = getCurrentPrice(pos.ticker) ?? pos.avg_price;
    const investedValue = pos.avg_price * pos.size;
    const currentValue = currentPrice * pos.size;
    const returnValue = currentValue - investedValue;
    const returnPercent = investedValue > 0 ? returnValue / investedValue : 0;

    return {
      ticker: pos.ticker,
      averagePrice: pos.avg_price,
      quantity: pos.size,
      currentPrice,
      investedValue,
      currentValue,
      portfolioPercent: 0, // ratio
      returnValue,
      returnPercent, // ratio
    };
  });

  const fixedPositions = fixed_income.map((pos) => {
    const investedValue = pos.total_applied;
    const currentValue = pos.current_value;
    const returnValue = currentValue - investedValue;
    const returnPercent = investedValue > 0 ? returnValue / investedValue : 0;

    return {
      uuid: pos.asset.asset_uuid,
      name: pos.asset.name,
      issuer: pos.asset.issuer,
      rateIndex: pos.asset.rate_index,
      interestRate: pos.asset.interest_rate,
      investedValue,
      currentValue,
      returnValue,
      returnPercent, // ratio
      portfolioPercent: 0, // ratio
    };
  });

  const variableIncomeValue = variablePositions.reduce((sum, p) => sum + p.currentValue, 0);
  const fixedIncomeValue = fixedPositions.reduce((sum, p) => sum + p.currentValue, 0);

  const portfolioValue = variableIncomeValue + fixedIncomeValue;

  variablePositions.forEach((pos) => {
    pos.portfolioPercent = portfolioValue > 0 ? pos.currentValue / portfolioValue : 0;
  });

  fixedPositions.forEach((pos) => {
    pos.portfolioPercent = portfolioValue > 0 ? pos.currentValue / portfolioValue : 0;
  });

  const variableIncomePct = portfolioValue > 0 ? variableIncomeValue / portfolioValue : 0;

  const fixedIncomePct = portfolioValue > 0 ? fixedIncomeValue / portfolioValue : 0;

  const dividend = 0;
  const portfolioPct = 0;

  return {
    variablePositions,
    fixedPositions,
    variableIncomeValue,
    fixedIncomeValue,
    portfolioValue,
    variableIncomePct,
    fixedIncomePct,
    dividend,
    portfolioPct,
  };
}
