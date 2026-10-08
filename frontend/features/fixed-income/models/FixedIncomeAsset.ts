import { differenceInCalendarDays, parseISO } from "date-fns";
import type { FixedIncomeAssetApi, RateIndex, InvestmentType } from "@/types";
import { displayDate, displayRateLabel } from "@/shared/lib/utils/display";

/** Legenda da tabela regressiva; a faixa aplicável vem calculada da API. */
export const TAX_TABLE = [
  { label: "Até 180 dias", rate: "0.225" },
  { label: "De 181 a 360 dias", rate: "0.20" },
  { label: "De 361 a 720 dias", rate: "0.175" },
  { label: "Acima de 720 dias", rate: "0.15" },
] as const;

export class FixedIncomeAsset {
  readonly uuid: string;
  readonly name: string;
  readonly issuer: string;
  readonly interestRate: string;
  readonly rateIndex: RateIndex;
  readonly investmentType: InvestmentType;
  readonly maturityDate: Date;
  readonly currentDate: Date;

  constructor(apiData: FixedIncomeAssetApi, currentDate: Date) {
    this.uuid = apiData.asset_uuid ?? "";
    this.name = apiData.name;
    this.issuer = apiData.issuer;
    this.interestRate = apiData.interest_rate;
    this.rateIndex = apiData.rate_index;
    this.investmentType = apiData.investment_type;
    this.maturityDate = parseISO(apiData.maturity_date);
    this.currentDate = currentDate;
  }

  get daysToMaturity(): number {
    return Math.max(differenceInCalendarDays(this.maturityDate, this.currentDate), 0);
  }

  get formattedMaturity(): string {
    const formatted = displayDate(this.maturityDate);
    return `${formatted} (${this.daysToMaturity} dias)`;
  }

  get indexTypeLabel(): string {
    return this.rateIndex === "Prefixado" ? "Pré-fixado" : "Pós-fixado";
  }

  get rateLabel(): string {
    return displayRateLabel(this.rateIndex, this.interestRate);
  }

  get incomeTaxLabel(): string {
    return ["LCI", "LCA"].includes(this.investmentType) ? "Isento" : "Regressivo (22,5% a 15%)";
  }

  get detailsLink(): string {
    return `/fixed-income/${this.uuid}`;
  }
}
