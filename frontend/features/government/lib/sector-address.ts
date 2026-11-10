import { displayPercent } from "@/shared/lib/utils/display";
import type { BaseDeal } from "@/types";

/** O valor da lista de setores que diz "sem endereço": a obra ou a emenda não aponta para setor nenhum. */
export const NO_SECTOR = "none";

/** O valor da lista de segmentos que diz "o setor inteiro". */
export const WHOLE_SECTOR = "all";

type Address = { sector: string | null; segment: string | null };

/** O endereço que a escolha das listas forma: sem setor, ou o setor com o segmento (nulo quando é o setor inteiro). */
export function addressOf(sector: string, segment: string): Address {
  if (sector === NO_SECTOR || sector === "") return { sector: null, segment: null };
  return { sector, segment: segment === WHOLE_SECTOR ? null : segment };
}

/** O alvo por extenso: "Energia" ou "Energia · Geração". */
export function addressLabel({ sector, segment }: Address): string {
  if (!sector) return "";
  return segment ? `${sector} · ${segment}` : sector;
}

/** A alta de uma fração do preço, com sinal: 0.03 → "+3%", 0.0175 → "+1,75%". */
export function boostLabel(fraction: string | number): string {
  return `+${displayPercent(Number(fraction), 2, { trim: true })}`;
}

/** A linha da prévia da obra: "Ações de Energia: +3% em 6 meses". */
export function worksBoostSentence(address: Address, boost: string | number): string {
  return `Ações de ${addressLabel(address)}: ${boostLabel(boost)} em 6 meses`;
}

/** A linha do favorecimento: os pontos de aprovação que cada grupo perde por ter o presidente no setor. */
export function favoritismSentence(points: string | number): string {
  const value = Math.abs(Number(points));
  const text = value.toLocaleString("pt-BR", { maximumFractionDigits: 1 });
  return `Favorecimento: −${text} ${value < 2 ? "ponto" : "pontos"} de aprovação enquanto a obra valer`;
}

/** A frase do acordo ao líder, com a alta cheia que o setor escolhido pode alcançar. */
export function amendmentSentence(boost: string | number): string {
  return `as ações do setor sobem até ${boostLabel(boost)} enquanto o acordo valer`;
}

type DealAddress = Pick<BaseDeal, "status" | "is_computer" | "sector" | "segment" | "sector_boost">;

/**
 * Onde a emenda do acordo vai, para a linha da tabela da base: "Energia: +3%" no acordo em vigor e "leva a emenda
 * para Energia: +3%" na proposta que o computador vai responder; vazio quando não há endereço.
 */
export function amendmentNote(deal: DealAddress): string {
  if (!deal.sector) return "";
  if (deal.status === "PENDING" && deal.is_computer) return computerAmendmentSentence(deal.sector, deal.sector_boost);
  return `${addressLabel(deal)}: ${boostLabel(deal.sector_boost)}`;
}

/** A leitura do partido do computador, que escolhe o setor sozinho: "leva a emenda para Energia: +3%". */
export function computerAmendmentSentence(sector: string, boost: string | number): string {
  return `leva a emenda para ${sector}: ${boostLabel(boost)}`;
}
