import type { FixedIncomePosition, PortfolioState, Position, RateIndex, Stock } from "@/types";
import { displayPercent } from "@/shared/lib/utils/display";

type ReturnMetrics = {
  investedValue: number;
  currentValue: number;
  returnValue: number;
  returnPercent: number;
};

export type VariablePosition = {
  portfolioPercent: number;
  investedValue: number;
  currentValue: number;
  returnValue: number;
  returnPercent: number;
  ticker: string;
  averagePrice: number;
  quantity: number;
  currentPrice: number;
};

export type FixedPosition = {
  portfolioPercent: number;
  investedValue: number;
  currentValue: number;
  returnValue: number;
  returnPercent: number;
  uuid: string;
  name: string;
  issuer: string;
  rateIndex: RateIndex;
  interestRate: number;
  rateLabel: string;
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

function calculateVariablePositions(variableIncome: Position[], stocks: Stock[] | null): VariablePosition[] {
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

function calculateFixedPositions(fixedIncome: FixedIncomePosition[]): FixedPosition[] {
  return fixedIncome.map((pos) => {
    const metrics = calculateReturnMetrics(pos.total_applied, pos.current_value);

    const r = pos.asset.interest_rate;
    const idx = pos.asset.rate_index;

    const rateLabel = (() => {
      switch (idx) {
        case "CDI":
          return `${displayPercent(r)} do CDI`;
        case "IPCA":
          return `IPCA + ${displayPercent(r)}`;
        case "SELIC":
          return `SELIC + ${displayPercent(r)}`;
        case "Prefixado":
          return `${displayPercent(r)} a.a.`;
        default:
          return "N/A";
      }
    })();

    return {
      uuid: pos.asset.asset_uuid,
      name: pos.asset.name,
      issuer: pos.asset.issuer,
      rateIndex: pos.asset.rate_index,
      interestRate: pos.asset.interest_rate,
      rateLabel,
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
