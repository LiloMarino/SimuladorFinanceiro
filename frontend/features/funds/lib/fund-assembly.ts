import { displayIsoDate, displayQuantity } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";

type Panel = FundDetails["assembly"];

/** A assembleia em andamento, como o cotista a vê. */
export type AssemblyCurrent = NonNullable<Panel["current"]>;

/** O placar em cotas: a favor, contra e abstenção. */
export type AssemblyTally = NonNullable<AssemblyCurrent["tally"]>;

/** O que cada trecho da barra pesa no total de cotas (frações de 0 a 1). */
export function tallyFractions(tally: AssemblyTally) {
  const total = Number(tally.total);
  const part = (value: string) => (total > 0 ? Number(value) / total : 0);
  return { favor: part(tally.in_favor), abstention: part(tally.abstention), against: part(tally.against) };
}

/** "Faltam N cotas a favor para trocar" ou o aviso de que a troca já vence. */
export function missingText(tally: AssemblyTally): string {
  const missing = Number(tally.missing_to_replace);
  if (missing <= 0) return "A favor já supera o gestor: se nada mudar, a gestão troca.";
  return `Faltam ${displayQuantity(tally.missing_to_replace)} ${missing === 1 ? "cota" : "cotas"} a favor para a gestão trocar. Empate mantém o gestor.`;
}

/** O motivo escrito de quem não pode convocar; nulo quando pode. */
export function blockReason(panel: Panel): string | null {
  switch (panel.block) {
    case null:
      return null;
    case "share":
      return `Convocar exige ${displayQuantity(panel.convene_quotas)} cotas (10% da gestora) e você tem ${displayQuantity(panel.my_quotas)}.`;
    case "interval":
      return panel.next_allowed_on === null
        ? "Há uma assembleia por gestora a cada 3 meses."
        : `Há uma assembleia por gestora a cada 3 meses: a próxima pode ser convocada em ${displayIsoDate(panel.next_allowed_on)}.`;
    case "pending":
      return "Já existe uma assembleia em andamento.";
    case "manager":
      return "O gestor não convoca assembleia contra si mesmo.";
    case "unlisted":
      return "A assembleia só existe depois da oferta pública.";
    case "grace":
      return panel.next_allowed_on === null
        ? "A assembleia só abre depois da carência."
        : `A assembleia só abre depois da carência, em ${displayIsoDate(panel.next_allowed_on)}.`;
  }
}

/** O que o resultado de uma assembleia concluída diz, em uma frase. */
export function resultText(result: NonNullable<Panel["last_result"]>): string {
  const closed = displayIsoDate(result.closed_on);
  return result.status === "REPLACED"
    ? `${result.candidate_nickname} assumiu a gestão no lugar de ${result.previous_manager_nickname} em ${closed}.`
    : `${result.previous_manager_nickname} segue na gestão: a votação fechou em ${closed} sem maioria para trocar.`;
}
