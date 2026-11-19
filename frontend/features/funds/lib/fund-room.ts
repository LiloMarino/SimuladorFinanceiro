import { displayDayMonth } from "@/shared/lib/utils/display";
import type { FundRoomItem, Pending } from "@/types";

/** A gestora é do jogador (conta para fundar outra): ele a gere ou a tem em licença pela presidência. */
export const isHeldBy = (fund: Pick<FundRoomItem, "manager_user_id" | "leave_manager_user_id">, userId: number) =>
  fund.manager_user_id === userId || fund.leave_manager_user_id === userId;

/** O jogador opera a gestora: ela é dele, ou ele é co-gestor ativo dela. */
export const operates = (fund: FundRoomItem, userId: number) => isHeldBy(fund, userId) || fund.i_comanage;

export type RoomBlocks = {
  /** As que o jogador gere */
  managed: FundRoomItem[];
  /** As que ele não gere, mas em que tem cotas */
  quotas: FundRoomItem[];
  /** As demais da sala */
  others: FundRoomItem[];
};

/** Separa a sala nos três blocos da lista; cada gestora cai em um só, na ordem de gerir, ter cotas e o resto. */
export function roomBlocks(funds: FundRoomItem[], userId: number): RoomBlocks {
  const managed = funds.filter((fund) => operates(fund, userId));
  const rest = funds.filter((fund) => !operates(fund, userId));
  return {
    managed,
    quotas: rest.filter((fund) => Number(fund.my_quotas) > 0),
    others: rest.filter((fund) => Number(fund.my_quotas) <= 0),
  };
}

/** O patrimônio da gestora: o patrimônio por cota vezes as cotas; nulo enquanto não há patrimônio por cota. */
export const roomNetWorth = (fund: Pick<FundRoomItem, "nav" | "quotas">) =>
  fund.nav === null ? null : Number(fund.nav) * Number(fund.quotas);

/** A soma do patrimônio das gestoras da sala. */
export const roomTotalNetWorth = (funds: FundRoomItem[]) =>
  funds.reduce((sum, fund) => sum + (roomNetWorth(fund) ?? 0), 0);

/** A fração das cotas em circulação que o jogador tem (0 a 1). */
export const roomShareOf = (fund: Pick<FundRoomItem, "my_quotas" | "quotas">) =>
  Number(fund.quotas) > 0 ? Number(fund.my_quotas) / Number(fund.quotas) : 0;

/** A gestora que o jogador fundou e perdeu para a assembleia; só existe enquanto ele não tem outra. */
export function roomLostFund(funds: FundRoomItem[], userId: number): FundRoomItem | undefined {
  if (funds.some((fund) => isHeldBy(fund, userId))) return undefined;
  return funds.find((fund) => fund.founder_user_id === userId);
}

/** A frase sob o título do bloco "Você gere": a situação das gestoras dele, ou o que o botão Abrir faz. */
export function managedHint(managed: FundRoomItem[], userId: number): string {
  const sentences: string[] = [];
  if (managed.some((fund) => fund.manager_user_id === userId && fund.frozen_until !== null)) {
    sentences.push("A gestora congela enquanto você é presidente.");
  }
  if (managed.some((fund) => fund.leave_manager_user_id === userId && fund.manager_user_id !== userId)) {
    sentences.push("A gestora está com o co-gestor até o fim do mandato.");
  }
  // A gestora ganha na assembleia é a que ele gere sem ter fundado nem ter recebido da presidência
  for (const fund of managed) {
    const won =
      fund.manager_user_id === userId && fund.founder_user_id !== userId && fund.leave_manager_user_id === null;
    if (won && fund.manager_since) {
      sentences.push(`Ganhou a assembleia da ${fund.name} em ${displayDayMonth(fund.manager_since)}.`);
    }
  }
  return sentences.length > 0 ? sentences.join(" ") : "Abrir leva à tela de gestão, com as abas da gestora.";
}

// As pendências que pedem decisão do jogador numa gestora
const FUND_DECISIONS: Pending["type"][] = [
  "FUND_ASSEMBLY_INVITE",
  "FUND_ASSEMBLY_VOTE",
  "COMANAGER_INVITE",
  "DIRECTED_ISSUANCE_OFFER",
];

/** Quantas decisões pendentes o jogador tem na gestora: convites, votação aberta e oferta dirigida. */
export const roomPendingCount = (pending: Pending[], fundId: number) =>
  pending.filter((item) => item.fund_id === fundId && FUND_DECISIONS.includes(item.type)).length;
