export type RateIndex = "CDI" | "IPCA" | "SELIC" | "Prefixado";

export type InvestmentType = "CDB" | "LCI" | "LCA" | "Tesouro Direto";

export type FixedIncomeAssetApi = {
  asset_uuid: string;
  name: string;
  issuer: string;
  interest_rate: number;
  rate_index: RateIndex;
  investment_type: InvestmentType;
  maturity_date: string;
};
