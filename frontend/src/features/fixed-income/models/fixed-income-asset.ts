import { differenceInDays, parseISO, format } from "date-fns";
import { ptBR } from "date-fns/locale";
import type { FixedIncomeAssetApi, RateIndex, InvestmentType } from "@/types";

const TAX_TABLE = [
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
  readonly maturityDate: string;
  readonly currentDate: Date;
  readonly rates: Record<string, number>;

  constructor(apiData: FixedIncomeAssetApi, currentDate: Date);
  constructor(apiData: FixedIncomeAssetApi, currentDate: Date, rates: Record<string, number>);
  constructor(apiData: FixedIncomeAssetApi, currentDate: Date, rates?: Record<string, number>) {
    this.uuid = apiData.uuid;
    this.name = apiData.name;
    this.issuer = apiData.issuer;
    this.interestRate = apiData.interest_rate;
    this.rateIndex = apiData.rate_index;
    this.investmentType = apiData.investment_type;
    this.maturityDate = apiData.maturity_date;
    this.currentDate = currentDate;
    this.rates = rates ?? { CDI: 0, IPCA: 0, SELIC: 0 };
  }

  get rateLabel(): string {
    switch (this.rateIndex) {
      case "CDI":
        return `${(this.interestRate * 100).toFixed(2)}% CDI`;
      case "IPCA":
        return `IPCA + ${this.interestRate.toFixed(2)}%`;
      case "SELIC":
        return `SELIC + ${(this.interestRate * 100).toFixed(2)}%`;
      case "Prefixado":
        return `${this.interestRate.toFixed(2)}% a.a.`;
      default:
        return "Invalid";
    }
  }

  get currentRateLabel(): string {
    const value = this.rates[this.rateIndex];
    return `${(value * 100).toFixed(2)}% a.a.`;
  }

  get formattedMaturity(): string {
    const maturity = parseISO(this.maturityDate);
    const formatted = format(maturity, "dd/MM/yyyy", { locale: ptBR });
    const days = Math.max(differenceInDays(maturity, this.currentDate), 0);
    return `${formatted} (${days} dias)`;
  }

  get investmentTypeLabel(): string {
    const labels: Record<string, string> = { CDB: "CDB", LCI: "LCI", LCA: "LCA", "Tesouro Direto": "Tesouro Direto" };
    return labels[this.investmentType] || this.investmentType;
  }

  get returnType(): string {
    return this.rateIndex === "Prefixado" ? "Pré-fixado" : "Pós-fixado";
  }

  get incomeTax(): string {
    return ["LCI", "LCA"].includes(this.investmentType) ? "Isento" : "Regressivo (22,5% a 15%)";
  }

  get annualRate(): number {
    switch (this.rateIndex) {
      case "CDI":
        return this.rates.CDI * this.interestRate;
      case "IPCA":
        return this.rates.IPCA + this.interestRate;
      case "SELIC":
        return this.rates.SELIC + this.interestRate;
      default:
        return this.interestRate;
    }
  }

  get annualRateLabel(): string {
    return `${(this.annualRate * 100).toFixed(2)}%`;
  }

  get daysToMaturity(): number {
    return Math.max(differenceInDays(parseISO(this.maturityDate), this.currentDate), 0);
  }

  private getTaxRate(days: number): number {
    for (let i = TAX_TABLE.length - 1; i >= 0; i--) {
      if (days >= TAX_TABLE[i].days) return TAX_TABLE[i].rate;
    }
    return TAX_TABLE[0].rate;
  }

  get detailsLink(): string {
    return `/fixed-income/${this.uuid}`;
  }

  calculateInvestment(amount: number) {
    if (amount <= 0) {
      return {
        amount: 0,
        grossAmount: 0,
        grossReturn: 0,
        grossReturnPct: 0,
        tax: 0,
        netAmount: 0,
        netReturn: 0,
        netReturnPct: 0,
        taxRate: 0,
      };
    }

    const days = this.daysToMaturity;
    const periodRate = this.annualRate * (days / 252);
    const grossReturn = amount * periodRate;
    const grossAmount = amount + grossReturn;
    const grossReturnPct = periodRate * 100;

    const taxRate = ["LCI", "LCA"].includes(this.investmentType) ? 0 : this.getTaxRate(days);
    const tax = grossReturn * taxRate;
    const netReturn = grossReturn - tax;
    const netAmount = amount + netReturn;
    const netReturnPct = (netReturn / amount) * 100;

    return { amount, grossAmount, grossReturn, grossReturnPct, tax, netAmount, netReturn, netReturnPct, days, taxRate };
  }
}
