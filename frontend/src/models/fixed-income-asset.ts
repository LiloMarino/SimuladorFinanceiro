import type { FixedIncomeAssetApi } from "@/types";
import { differenceInDays, parseISO, format } from "date-fns";
import { ptBR } from "date-fns/locale";

export class FixedIncomeAsset {
  readonly name: string;
  readonly issuer: string;
  readonly interestRate: number;
  readonly rateIndex: string;
  readonly investmentType: string;
  readonly maturityDate: string;
  readonly currentDate: Date;

  constructor(apiData: FixedIncomeAssetApi, currentDate: Date) {
    this.name = apiData.name;
    this.issuer = apiData.issuer;
    this.interestRate = apiData.interest_rate;
    this.rateIndex = apiData.rate_index;
    this.investmentType = apiData.investment_type;
    this.maturityDate = apiData.maturity_date;
    this.currentDate = currentDate;
  }

  /** Retorna taxa formatada */
  get rateLabel(): string {
    if (this.rateIndex === "PREFIXADO") {
      return `${this.interestRate.toFixed(2)}% a.a.`;
    }
    return `${this.interestRate}% ${this.rateIndex}`;
  }

  /** Retorna a data de vencimento formatada */
  get formattedMaturity(): string {
    const maturity = parseISO(this.maturityDate);
    const formatted = format(maturity, "dd/MM/yyyy", { locale: ptBR });
    const days = Math.max(differenceInDays(maturity, this.currentDate), 0);
    return `${formatted} (${days} dias)`;
  }

  /** Retorna a forma de tributação formatada */
  get incomeTax(): string {
    switch (this.investmentType.toUpperCase()) {
      case "LCI":
      case "LCA":
        return "Isento";
      case "CDB":
      case "TESOURO DIRETO":
        return "Regressivo (22,5% a 15%)";
      default:
        return "Indefinido";
    }
  }

  /** Gera o link detalhado */
  get detailsLink(): string {
    return `/fixed-income/${this.name.toLowerCase()}`;
  }
}
