import { differenceInDays, parseISO } from "date-fns";
import type { FixedIncomeAssetApi, RateIndex, InvestmentType, EconomicIndicators } from "@/types";
import { formatDate } from "@/shared/lib/utils/formatting";

export const TAX_TABLE: readonly { days: number; rate: number }[] = [
  { days: 0, rate: 0.225 },
  { days: 181, rate: 0.2 },
  { days: 361, rate: 0.175 },
  { days: 721, rate: 0.15 },
];

export class FixedIncomeAsset {
  readonly uuid: string;
  readonly name: string;
  readonly issuer: string;
  readonly interestRate: number;
  readonly rateIndex: RateIndex;
  readonly investmentType: InvestmentType;
  readonly maturityDate: Date;
  readonly currentDate: Date;
  readonly rates: EconomicIndicators;

  constructor(apiData: FixedIncomeAssetApi, currentDate: Date);
  constructor(apiData: FixedIncomeAssetApi, currentDate: Date, rates: EconomicIndicators);
  constructor(apiData: FixedIncomeAssetApi, currentDate: Date, rates?: EconomicIndicators) {
    this.uuid = apiData.uuid;
    this.name = apiData.name;
    this.issuer = apiData.issuer;
    this.interestRate = apiData.interest_rate;
    this.rateIndex = apiData.rate_index;
    this.investmentType = apiData.investment_type;
    this.maturityDate = parseISO(apiData.maturity_date);
    this.currentDate = currentDate;
    this.rates = rates ?? { cdi: 0, ipca: 0, selic: 0 };
  }

  get expectedReturn(): number {
    const t = this.daysToMaturity / 365;
    // Juros compostos
    return Math.pow(1 + this.annualRate, t) - 1;
  }

  get annualRate(): number {
    let annualPercent = 0;

    switch (this.rateIndex) {
      case "Prefixado":
        annualPercent = this.interestRate;
        break;

      case "CDI":
        annualPercent = this.rates.cdi * this.interestRate;
        break;

      case "IPCA":
        annualPercent = this.rates.ipca + this.interestRate;
        break;

      case "SELIC":
        annualPercent = this.rates.selic + (this.interestRate * 100);
        break;
    }

    // Converte % para decimal
    return annualPercent / 100;
  }

  get daysToMaturity(): number {
    const days = Math.max(differenceInDays(this.maturityDate, this.currentDate), 0);
    return days;
  }

  get formattedMaturity(): string {
    const formatted = formatDate(this.maturityDate);
    return `${formatted} (${this.daysToMaturity} dias)`;
  }

  get indexTypeLabel(): string {
    return this.rateIndex === "Prefixado" ? "Pré-fixado" : "Pós-fixado";
  }

  get currentRateLabel(): string {
    switch (this.rateIndex) {
      case "CDI":
        return `${(this.rates.cdi).toFixed(2)}% a.a.`;

      case "IPCA":
        return `${(this.rates.ipca).toFixed(2)}% a.a.`;

      case "SELIC":
        return `${(this.rates.selic).toFixed(2)}% a.a.`;

      default:
        return "";
    }
  }

  get rateLabel(): string {
    switch (this.rateIndex) {
      case "CDI":
        return `${(this.interestRate * 100).toFixed(2)}% do CDI`;
      case "IPCA":
        return `IPCA + ${this.interestRate.toFixed(2)}%`;
      case "SELIC":
        return `SELIC + ${(this.interestRate * 100).toFixed(2)}%`;
      case "Prefixado":
        return `${this.interestRate.toFixed(2)}% a.a.`;
      default:
        return "N/A";
    }
  }

  get incomeTaxLabel(): string {
    return ["LCI", "LCA"].includes(this.investmentType) ? "Isento" : "Regressivo (22,5% a 15%)";
  }

  get detailsLink(): string {
    return `/fixed-income/${this.uuid}`;
  }

}
