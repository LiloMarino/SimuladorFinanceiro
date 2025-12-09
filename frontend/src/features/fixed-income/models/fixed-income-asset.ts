import { differenceInDays, parseISO } from "date-fns";
import type { FixedIncomeAssetApi, RateIndex, InvestmentType, EconomicIndicators } from "@/types";
import { formatDate } from "@/shared/lib/utils/formatting";

export const TAX_TABLE = [
  { label: "Até 180 dias", min: 0, max: 180, rate: 0.225 },
  { label: "De 181 a 360 dias", min: 181, max: 360, rate: 0.2 },
  { label: "De 361 a 720 dias", min: 361, max: 720, rate: 0.175 },
  { label: "Acima de 720 dias", min: 721, max: Infinity, rate: 0.15 },
] as const;

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

  get grossReturn(): number {
    const t = this.daysToMaturity / 365;
    return Math.pow(1 + this.annualRate, t) - 1;
  }

  get netReturn(): number {
    return this.grossReturn * (1 - this.incomeTaxRate);
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
        annualPercent = this.rates.selic + this.interestRate * 100;
        break;
    }

    // Converte % para decimal
    return annualPercent / 100;
  }

  get incomeTaxRate(): number {
    // LCI/LCA -> isento
    if (["LCI", "LCA"].includes(this.investmentType)) return 0;

    const d = this.daysToMaturity;

    // Encontra o primeiro item cuja regra de dias é satisfeita
    const entry = TAX_TABLE.find((row) => d >= row.min && d <= row.max);

    return entry?.rate ?? 0;
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

  getSimulation(amount: number) {
    const invested = amount || 0;

    const grossRate = this.grossReturn; // percentual decimal
    const netRate = this.netReturn; // percentual decimal
    const taxRate = this.incomeTaxRate;

    const grossIncome = invested * grossRate;
    const netIncome = invested * netRate;
    const taxAmount = grossIncome - netIncome;
    const finalAmount = invested + netIncome;

    return {
      invested,
      grossIncome,
      taxAmount,
      finalAmount,
      maturityLabel: this.formattedMaturity,
      grossRate,
      netRate,
      taxRate,
    };
  }

  get currentRateLabel(): string {
    switch (this.rateIndex) {
      case "CDI":
        return `${this.rates.cdi.toFixed(2)}% a.a.`;

      case "IPCA":
        return `${this.rates.ipca.toFixed(2)}% a.a.`;

      case "SELIC":
        return `${this.rates.selic.toFixed(2)}% a.a.`;

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
