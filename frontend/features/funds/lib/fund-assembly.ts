import { displayIsoDate, displayNumericDayMonth, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { FundAssemblyAgenda, FundDetails } from "@/types";

type Panel = FundDetails["assembly"];

/** Uma votação em andamento, como o cotista a vê. */
export type AssemblyCurrent = Panel["current"][number];

/** O placar em cotas: a favor, contra e abstenção. */
export type AssemblyTally = NonNullable<AssemblyCurrent["tally"]>;

/** As taxas de uma pauta de aumento: as de quando foi proposta e as propostas. */
export type AssemblyFee = NonNullable<AssemblyCurrent["fee"]>;

/** Uma votação concluída do histórico. */
export type AssemblyResult = Panel["history"][number];

/** Uma pauta que a assembleia aceita e o motivo de quem não pode convocá-la. */
export type AssemblyOption = Panel["options"][number];

/** As pautas, na ordem em que a convocação as lista. */
export const AGENDAS = ["REPLACE_MANAGER", "MERGE", "FEE_INCREASE"] as const satisfies readonly FundAssemblyAgenda[];

export const AGENDA_LABEL: Record<FundAssemblyAgenda, string> = {
  REPLACE_MANAGER: "Trocar o gestor",
  MERGE: "Fusão",
  FEE_INCREASE: "Aumento de taxa",
};

export const AGENDA_SUMMARY: Record<FundAssemblyAgenda, string> = {
  REPLACE_MANAGER: "Os cotistas escolhem quem assume a gestão; quem for escolhido aceita o convite em até 5 pregões.",
  MERGE: "Junta esta gestora com outra que o mesmo gestor gere.",
  FEE_INCREASE:
    "Sobe a taxa de administração ou de performance; aprovada, vale no mês seguinte ao resultado. Baixar não precisa de votação.",
};

/** A votação em andamento de uma pauta, se houver. */
export const currentOf = (panel: Panel, agenda: FundAssemblyAgenda) =>
  panel.current.find((assembly) => assembly.agenda === agenda);

/** A pauta como a convocação a oferece a quem consulta. */
export const optionOf = (panel: Panel, agenda: FundAssemblyAgenda) =>
  panel.options.find((option) => option.agenda === agenda);

/** As votações abertas que esperam o voto de quem consulta. */
export const votesToCastOf = (panel: Panel) =>
  panel.current.filter((assembly) => assembly.status === "VOTING" && assembly.can_vote && assembly.my_vote === null);

const FEE_LABEL = { management: "taxa de administração", performance: "taxa de performance" } as const;

const feePercent = (fraction: string) => displayPercent(fraction, 1, { trim: true });

/** As taxas que a proposta muda, cada uma com o valor de hoje e o proposto. */
function feeChanges(fee: AssemblyFee) {
  const changes = [
    { key: "management", label: FEE_LABEL.management, from: fee.management_from, to: fee.management_to },
    { key: "performance", label: FEE_LABEL.performance, from: fee.performance_from, to: fee.performance_to },
  ] as const;
  return changes
    .filter((change) => Number(change.from) !== Number(change.to))
    .map((change) => ({ ...change, from: feePercent(change.from), to: feePercent(change.to) }));
}

/** O nome do aumento: "Aumento da taxa de administração (1,5% para 2%)". */
export function feeTitle(fee: AssemblyFee): string {
  const changes = feeChanges(fee);
  const [only] = changes;
  if (changes.length === 1 && only) return `Aumento da ${only.label} (${only.from} para ${only.to})`;
  return `Aumento das taxas (${changes.map((change) => `${change.key === "management" ? "administração" : "performance"} ${change.from} para ${change.to}`).join("; ")})`;
}

/** O nome da fusão pelo lado de quem lê: "Incorporar a Boreal Renda" ou "Ser incorporada pela Aurora Gestão". */
const mergeTitle = (partnerName: string, absorbed: boolean) =>
  absorbed ? `Ser incorporada pela ${partnerName}` : `Incorporar a ${partnerName}`;

/** O título da votação em andamento. */
export function currentTitle(assembly: AssemblyCurrent): string {
  if (assembly.agenda === "FEE_INCREASE" && assembly.fee !== null) return feeTitle(assembly.fee);
  if (assembly.agenda === "MERGE" && assembly.merge !== null) {
    const { merge } = assembly;
    return merge.is_mother ? mergeTitle(merge.daughter.name, false) : mergeTitle(merge.mother.name, true);
  }
  return `Trocar o gestor por ${assembly.candidate_nickname ?? "um candidato"}`;
}

/** O título da votação concluída. */
export function resultTitle(result: AssemblyResult): string {
  if (result.agenda === "FEE_INCREASE" && result.fee !== null) return feeTitle(result.fee);
  if (result.agenda === "MERGE" && result.partner_name !== null)
    return mergeTitle(result.partner_name, result.absorbed);
  return `Trocar o gestor (${result.previous_manager_nickname} por ${result.candidate_nickname ?? "—"})`;
}

/** O peso de cada lado entre as cotas que votaram (frações de 0 a 1). */
export function voteShares(tally: AssemblyTally) {
  const voted = Number(tally.in_favor) + Number(tally.against);
  return voted > 0
    ? { favor: Number(tally.in_favor) / voted, against: Number(tally.against) / voted }
    : { favor: 0, against: 0 };
}

/** As cotas que votaram e as que podem votar (o total menos bots, Mercado e quem opera a gestora). */
export function participation(tally: AssemblyTally, nonVoting: string) {
  const voted = Number(tally.in_favor) + Number(tally.against);
  const eligible = Number(tally.total) - Number(nonVoting);
  return { voted, eligible, share: eligible > 0 ? voted / eligible : 0 };
}

const MISSING_OUTCOME: Record<FundAssemblyAgenda, string> = {
  REPLACE_MANAGER: "a gestão trocar",
  MERGE: "a fusão sair",
  FEE_INCREASE: "a taxa subir",
};

const MISSING_TIE: Record<FundAssemblyAgenda, string> = {
  REPLACE_MANAGER: "Empate mantém o gestor.",
  MERGE: "Empate, ou sem votos, mantém as duas separadas.",
  FEE_INCREASE: "Empate, ou sem votos, mantém a taxa.",
};

/** "Faltam N cotas a favor" ou o aviso de que a pauta já vence. */
export function missingText(tally: AssemblyTally, agenda: FundAssemblyAgenda): string {
  const missing = Number(tally.missing_to_win);
  const outcome = MISSING_OUTCOME[agenda];
  const tie = MISSING_TIE[agenda];
  if (missing <= 0) return `A favor já supera os contra: se nada mudar, ${outcome}.`;
  return `Faltam ${displayQuantity(tally.missing_to_win)} ${missing === 1 ? "cota" : "cotas"} a favor para ${outcome}. ${tie}`;
}

/** O motivo escrito de quem não pode convocar a pauta; nulo quando pode. */
export function blockReason(option: AssemblyOption | undefined, panel: Panel): string | null {
  if (option === undefined) return null;
  switch (option.block) {
    case null:
      return null;
    case "share":
      return `Convocar exige ${displayQuantity(panel.convene_quotas)} cotas (10% da gestora) e você tem ${displayQuantity(panel.my_quotas)}.`;
    case "interval":
      return option.next_allowed_on === null
        ? "Há uma troca de gestor por gestora a cada 3 meses."
        : `Há uma troca de gestor a cada 3 meses: a próxima pode ser convocada em ${displayIsoDate(option.next_allowed_on)}.`;
    case "pending":
      return option.agenda === "MERGE" && option.next_allowed_on !== null
        ? `Já há uma fusão em votação até ${displayNumericDayMonth(option.next_allowed_on)}.`
        : "A gestora já tem uma votação aberta desta pauta.";
    case "manager":
      return "O gestor não convoca assembleia contra si mesmo.";
    case "manager_only":
      return option.agenda === "MERGE" ? "Só o gestor propõe a fusão." : "Só o gestor propõe aumento de taxa.";
    case "no_partner":
      return "A fusão precisa de outra gestora sua, listada e livre de votação ou oferta em aberto.";
    case "busy":
      return "Feche antes a emissão, a oferta ou a recompra em aberto.";
    case "frozen":
      return option.next_allowed_on === null
        ? "O gestor governa o país e a gestora fica congelada."
        : `O gestor governa o país e a gestora fica congelada até ${displayIsoDate(option.next_allowed_on)}.`;
    case "swap_open":
      return "Há uma troca de gestor em andamento: a fusão espera o resultado dela.";
    case "merge_open":
      return option.next_allowed_on === null
        ? "Há uma fusão em votação: a troca de gestor espera o resultado dela."
        : `Há uma fusão em votação até ${displayNumericDayMonth(option.next_allowed_on)}: a troca de gestor espera o resultado dela.`;
    case "unlisted":
      return "A assembleia só existe depois da oferta pública.";
    case "grace":
      return option.next_allowed_on === null
        ? "A assembleia só abre depois da carência."
        : `A assembleia só abre depois da carência, em ${displayIsoDate(option.next_allowed_on)}.`;
  }
}

/** O placar de uma votação concluída em uma frase: "18,2% a favor · vale a partir de 01/12/2026". */
export function resultScore(result: AssemblyResult): string {
  const { favor } = voteShares(result.tally);
  const voted = Number(result.tally.in_favor) + Number(result.tally.against);
  const score = voted > 0 ? `${displayPercent(favor, 1)} a favor` : "sem votos";
  return result.effective_on === null ? score : `${score} · vale a partir de ${displayIsoDate(result.effective_on)}`;
}

/** A votação aprovada, qualquer que seja a pauta: a troca feita ou o aumento aprovado. */
export const isApproved = (result: Pick<AssemblyResult, "status">) =>
  result.status === "REPLACED" || result.status === "APPROVED";
