import type { FixedIncomeAssetApi } from "@/types";
import { differenceInDays, parseISO, format } from "date-fns";
import { ptBR } from "date-fns/locale";

export class FixedIncomeAsset {
  readonly name: string;
  readonly issuer: string;
  readonly interestRate: number | null;
  readonly rateIndex: string;
  readonly investmentType: string;
  readonly maturityDate: string | null;
  readonly daysToMaturity: number;
  readonly incomeTax: string | null;

  constructor(apiData: FixedIncomeAssetApi) {
    this.name = apiData.name;
    this.issuer = apiData.issuer;
    this.interestRate = apiData.interest_rate ?? null;
    this.rateIndex = apiData.rate_index?.toUpperCase?.() ?? "—";
    this.investmentType = apiData.investment_type ?? "—";
    this.maturityDate = apiData.maturity_date ?? null;
    this.daysToMaturity = this.calculateDaysToMaturity();
    this.incomeTax = this.calculateIncomeTax();
  }

  /** Calcula dias até o vencimento */
  private calculateDaysToMaturity(): number {
    if (!this.maturityDate) return 0;
    try {
      const maturity = parseISO(this.maturityDate);
      return Math.max(differenceInDays(maturity, new Date()), 0);
    } catch {
      return 0;
    }
  }

  /** Define a regra de IR com base no tipo de investimento */
  private calculateIncomeTax(): string | null {
    switch (this.investmentType.toUpperCase()) {
      case "LCI":
      case "LCA":
        return "Isento";
      case "CDB":
      case "TESOURO DIRETO":
        return "Regressivo (22,5% a 15%)";
      default:
        return null;
    }
  }

  /** Retorna taxa formatada */
  get rateLabel(): string {
    if (!this.interestRate) return this.rateIndex;
    if (this.rateIndex === "PREFIXADO") {
      return `${this.interestRate.toFixed(2)}% a.a.`;
    }
    return `${this.interestRate}% ${this.rateIndex}`;
  }

  /** Retorna data de vencimento formatada */
  get formattedMaturity(): string {
    if (!this.maturityDate) return "—";
    try {
      const date = parseISO(this.maturityDate);
      const formatted = format(date, "dd/MM/yyyy", { locale: ptBR });
      const days = this.daysToMaturity > 0 ? ` (${this.daysToMaturity} dias)` : "";
      return formatted + days;
    } catch {
      return "—";
    }
  }

  /** Retorna a forma de tributação formatada */
  get formattedIncomeTax(): string {
    return this.incomeTax ?? "—";
  }

  /** Gera o link detalhado */
  get detailsLink(): string {
    return `/fixed-income/${this.name.toLowerCase()}`;
  }
}
