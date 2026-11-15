import type { FundDetails } from "@/types";

export type Comanager = FundDetails["comanagers"][number];

// Co-gestores por gestora, contando os convites pendentes
export const MAX_COMANAGERS = 3;

// Dias que o convidado tem para responder ao convite
export const INVITE_DAYS = 7;

const CENT = 100;

/** A parte que vale daqui em diante: a agendada, se houver, senão a de hoje (fração do servidor). */
export const futureShareOf = (comanager: Pick<Comanager, "share" | "pending_share">) =>
  Number(comanager.pending_share ?? comanager.share);

/** O que os outros co-gestores já reservam, em pontos percentuais. */
export const othersPoints = (comanagers: Comanager[], exceptUserId: number | null) =>
  comanagers
    .filter((comanager) => comanager.user_id !== exceptUserId)
    .reduce((sum, comanager) => sum + futureShareOf(comanager) * 100, 0);

/** O teto da régua de um co-gestor: sobra ao menos 1 ponto para o gestor principal. */
export const maxSharePoints = (others: number) => Math.max(0, Math.round(100 - others) - 1);

/** A parte do principal depois da mudança: o que sobra das partes dos co-gestores. */
export const managerPointsAfter = (others: number, points: number) => 100 - others - points;

/** A taxa dividida entre o co-gestor e o principal, o co-gestor arredondado para baixo ao centavo. */
export function splitMonthly(monthly: number, points: number) {
  // monthly × points / 100 reais, que são monthly × points centavos
  const comanager = Math.floor(monthly * points) / CENT;
  return { comanager, manager: Math.round((monthly - comanager) * CENT) / CENT };
}

/** O convite pendente: ainda não opera e já reserva a parte. */
export const isInvited = (comanager: Pick<Comanager, "status">) => comanager.status === "INVITED";

/** Há parte nova agendada para um co-gestor que já opera. */
export const hasScheduledChange = (comanager: Pick<Comanager, "status" | "pending_share" | "pending_from">) =>
  comanager.status === "ACTIVE" && comanager.pending_share !== null && comanager.pending_from !== null;

/** O convite do jogador que consulta a gestora, se houver. */
export const myInviteOf = (fund: Pick<FundDetails, "comanagers">, userId: number) =>
  fund.comanagers.find((comanager) => comanager.user_id === userId && isInvited(comanager));
