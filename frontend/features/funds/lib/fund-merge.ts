import { displayMoney, displayNumericDayMonth, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { FundMergePreview } from "@/types";
import { blockReason, type AssemblyCurrent, type AssemblyOption, type AssemblyResult } from "./fund-assembly";

/** A fusão de uma votação, vista da gestora que consulta. */
export type AssemblyMerge = NonNullable<AssemblyCurrent["merge"]>;

/** Uma das duas gestoras da fusão. */
export type MergeSide = FundMergePreview["mother"];

/** A razão sem zeros à direita e com no máximo 4 casas: "0,5", "1,8182". */
const ratioText = (value: number) => displayQuantity(String(Number(value.toFixed(4))));

/** A troca em cotas: "2 BORE11 = 1 AURO11" quando a incorporada vale menos por cota, "1 BORE11 = 2 AURO11" quando vale mais. */
export function exchangeText(daughterTicker: string, motherTicker: string, ratio: string): string {
  const value = Number(ratio);
  if (value <= 0) return "—";
  return value <= 1
    ? `${ratioText(1 / value)} ${daughterTicker} = 1 ${motherTicker}`
    : `1 ${daughterTicker} = ${ratioText(value)} ${motherTicker}`;
}

/** A conta da razão: "hoje R$ 55,22 ÷ R$ 110,44 = 0,5". */
export function ratioFormula(daughter: MergeSide, mother: MergeSide, ratio: string | null): string | null {
  if (daughter.nav === null || mother.nav === null || ratio === null) return null;
  return `hoje ${displayMoney(daughter.nav)} ÷ ${displayMoney(mother.nav)} = ${ratioText(Number(ratio))}`;
}

/** Quem paga a saída de quem vota contra na incorporada, como o diálogo da proposta conta. */
export const exitPaymentNote = (daughter: MergeSide, mother: MergeSide) =>
  `Pago pelo caixa da ${daughter.name} (hoje ${displayMoney(daughter.cash)}); o que faltar, a ${mother.name} paga do próprio caixa logo após a incorporação`;

/** Quem paga a saída de quem vota contra, como a votação conta. */
export const exitVoteNote = (daughter: Pick<MergeSide, "name">) => `Pago pela ${daughter.name} antes da incorporação`;

/** A participação na votação da outra gestora: "Sai se as duas aprovarem; lá votaram 52% das cotas". */
export const partnerNote = (merge: Pick<AssemblyMerge, "partner_voted_share">) =>
  `Sai se as duas aprovarem; lá votaram ${displayPercent(merge.partner_voted_share, 0)} das cotas`;

/** O lado que vence na votação da outra gestora: "71,0% a favor". */
export const partnerFavor = (merge: Pick<AssemblyMerge, "partner_in_favor_share">) =>
  merge.partner_in_favor_share === null ? "sem votos" : `${displayPercent(merge.partner_in_favor_share, 1)} a favor`;

/** O que cada lado do voto significa na fusão; quem vota contra na incorporada sai pelo patrimônio por cota. */
export function mergeChoices(merge: AssemblyMerge): Record<"favor" | "against", string> {
  const favor = merge.is_mother
    ? `A ${merge.mother.name} incorpora a ${merge.daughter.name}`
    : `A ${merge.mother.name} incorpora esta gestora`;
  return {
    favor,
    against: merge.is_mother
      ? "As duas seguem separadas"
      : "As duas seguem separadas; se as duas aprovarem, você sai pelo patrimônio por cota",
  };
}

/** O aviso de que a fusão não fecha com os caixas de hoje; nulo quando cobrem a saída. */
export function shortfallText(shortfall: string): string | null {
  return Number(shortfall) > 0
    ? `Os dois caixas somados não cobrem a saída de quem votou contra: faltam ${displayMoney(shortfall)}. Se ainda faltar no fechamento, a fusão é rejeitada.`
    : null;
}

/** O motivo da fusão que ganhou no voto e foi rejeitada no fechamento por falta de caixa; nulo nas demais votações. */
export function rejectionNote(result: Pick<AssemblyResult, "merge_shortfall">): string | null {
  return result.merge_shortfall === null
    ? null
    : `Rejeitada: os dois caixas somados não cobriam a saída de quem votou contra (faltavam ${displayMoney(result.merge_shortfall)}).`;
}

/** O que a linha "Propor fusão" diz de quem não pode propor; a fusão em votação é das duas gestoras. */
export function mergeBlockReason(
  option: AssemblyOption | undefined,
  panel: Parameters<typeof blockReason>[1],
): string | null {
  if (option?.block === "pending" && option.next_allowed_on !== null)
    return `Já há uma fusão das duas em votação, até ${displayNumericDayMonth(option.next_allowed_on)}.`;
  return blockReason(option, panel);
}

/** O que a linha "Propor fusão" diz da outra gestora que o mesmo gestor gere. */
export const mergeDescription = (partners: MergeSide[]) => {
  const [first] = partners;
  const tail = "a fusão junta as duas numa só e vai à assembleia de cada uma";
  if (first === undefined) return "Junta duas gestoras que você gere numa só, e as duas assembleias votam";
  if (partners.length === 1) return `Você gere também a ${first.name} (${first.ticker}): ${tail}`;
  return `Você gere outras ${partners.length} gestoras: a fusão junta duas delas numa só e vai à assembleia de cada uma`;
};
