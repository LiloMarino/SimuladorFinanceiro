import type { FundDetails } from "@/types";

type Distribution = FundDetails["distributions"][number];

const MONTHS = 12;

export type FundYield = {
  /** O que cada cota recebeu nos últimos 12 meses pagos, em reais */
  perQuota: number;
  /** O preço sobre o qual o yield é medido: o do mercado, ou o patrimônio por cota sem negócio */
  base: number;
  /** A fração ao ano; nulo sem rendimento pago ou sem preço */
  rate: number | null;
  /** Quanto cada cota recebeu no último pagamento */
  lastPerQuota: number | null;
  /** A data do último pagamento */
  lastPaidOn: string | null;
};

/** Os rendimentos já pagos, do mais novo ao mais antigo. */
const paidRows = (distributions: Distribution[]) =>
  [...distributions]
    .filter((row) => row.paid_on !== null && row.paid_per_quota !== null)
    .sort((a, b) => (b.paid_on ?? "").localeCompare(a.paid_on ?? ""));

/** O dividend yield: o que a cota pagou nos últimos 12 meses sobre o preço dela hoje. */
export function fundYield(fund: Pick<FundDetails, "distributions" | "price" | "nav">): FundYield {
  const paid = paidRows(fund.distributions);
  const perQuota = paid.slice(0, MONTHS).reduce((sum, row) => sum + Number(row.paid_per_quota), 0);
  const base = Number(fund.price ?? fund.nav ?? 0);
  const last = paid[0];

  return {
    perQuota,
    base,
    rate: paid.length > 0 && base > 0 ? perQuota / base : null,
    lastPerQuota: last ? Number(last.paid_per_quota) : null,
    lastPaidOn: last?.paid_on ?? null,
  };
}
