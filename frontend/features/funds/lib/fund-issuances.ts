import type { FundDetails } from "@/types";

export type IssuanceRow = {
  key: string;
  day: string;
  how: "Oferta pública" | "Emissão pública" | "Emissão dirigida";
  quotas: string | null;
  /** O preço por cota; nulo quando ainda não houve venda */
  price: string | null;
  /** O dinheiro que entrou na gestora */
  amount: string | null;
  /** Quem comprou, já em texto */
  buyers: string;
  /** A oferta ou a emissão ainda vende */
  inProgress: boolean;
  /** O motivo de a emissão ter encerrado sem vender cota; nulo nas demais linhas */
  unsoldReason: string | null;
};

/** Bots e Mercado compram no último pregão da sobra: o bot quando o preço cabe no valor que dá à cota, o Mercado quando há desempenho acima do CDI ou ágio. */
const UNSOLD_REASON =
  "Encerrada sem venda: ninguém comprou, nenhum bot achou o preço dentro do valor que dá à cota e o Mercado não viu desempenho acima do CDI nem ágio.";

const investors = (count: number) => `${count} ${count === 1 ? "investidor" : "investidores"}`;

/** A oferta pública da gestora como uma linha: aberta ou encerrada. */
function offerRow(fund: FundDetails): IssuanceRow | null {
  if (fund.listed_on === null) return null;
  const sold = Number(fund.offer_sold ?? 0);
  const raised = Number(fund.offer_raised ?? 0);
  const count = fund.offer_buyers_count ?? fund.offer_buyers?.length ?? 0;

  return {
    key: "offer",
    day: fund.offer_closed_on ?? fund.listed_on,
    how: "Oferta pública",
    quotas: fund.offer_sold,
    price: sold > 0 ? String(raised / sold) : null,
    amount: fund.offer_raised,
    buyers: investors(count),
    inProgress: fund.offer_closed_on === null,
    unsoldReason: null,
  };
}

/** As emissões da gestora, da mais nova à mais antiga: a oferta pública, as emissões abertas a cotistas e as dirigidas. */
export function issuanceRows(fund: FundDetails): IssuanceRow[] {
  const rows: IssuanceRow[] = [];
  const offer = offerRow(fund);
  if (offer) rows.push(offer);

  const open = fund.issuance;
  if (open && open.closed_on === null) {
    rows.push({
      key: `issuance-${open.id}`,
      day: open.announced_on,
      how: "Emissão pública",
      quotas: open.sold,
      price: open.price,
      amount: open.raised,
      buyers: "Cotistas e mercado",
      inProgress: true,
      unsoldReason: null,
    });
  }

  fund.movements.forEach((movement, index) => {
    if (movement.type === "issuance_closed") {
      rows.push({
        key: `issuance-closed-${movement.day}-${index}`,
        day: movement.day,
        how: "Emissão pública",
        quotas: movement.quotas,
        price: movement.price,
        amount: movement.amount,
        buyers: "Cotistas e mercado",
        inProgress: false,
        unsoldReason: Number(movement.quotas ?? 0) === 0 ? UNSOLD_REASON : null,
      });
    } else if (movement.type === "directed_issuance") {
      rows.push({
        key: `directed-${movement.day}-${index}`,
        day: movement.day,
        how: "Emissão dirigida",
        quotas: movement.quotas,
        price: movement.price,
        amount: movement.amount,
        buyers: movement.nickname ?? "—",
        inProgress: false,
        unsoldReason: null,
      });
    }
  });

  return [...rows].sort((a, b) => b.day.localeCompare(a.day));
}
