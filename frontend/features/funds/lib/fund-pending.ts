import type { FundDetails } from "@/types";
import { myInviteOf, type Comanager } from "./fund-comanagers";
import type { DirectedOffer } from "./fund-directed";

type Issuance = NonNullable<FundDetails["issuance"]>;

/** O que ainda resta do direito de preferência do jogador na emissão; 0 sem direito ou com tudo usado. */
export const rightsLeftOf = (issuance: Pick<Issuance, "my_rights" | "my_bought">) =>
  issuance.my_rights === null ? 0 : Math.max(Number(issuance.my_rights) - Number(issuance.my_bought ?? 0), 0);

export type FundPending = {
  /** O convite de co-gestão feito ao jogador */
  invite: Comanager | undefined;
  /** A oferta de cotas dirigida ao jogador, a quem ele responde */
  directed: DirectedOffer | undefined;
  /** O direito de preferência que ainda resta na emissão aberta, em cotas */
  preferenceLeft: number;
};

/** O que espera decisão do jogador nesta gestora: convite, oferta dirigida e preferência da emissão. */
export function fundPending(fund: FundDetails, userId: number): FundPending {
  const issuance = fund.issuance;
  const preferenceOpen = issuance !== null && issuance.closed_on === null && issuance.phase === "preference";
  const directed = fund.directed_issuance;

  return {
    invite: myInviteOf(fund, userId),
    directed: directed !== null && directed.buyer_user_id === userId ? directed : undefined,
    preferenceLeft: preferenceOpen ? rightsLeftOf(issuance) : 0,
  };
}

export const fundPendingCount = (pending: FundPending) =>
  (pending.invite ? 1 : 0) + (pending.directed ? 1 : 0) + (pending.preferenceLeft > 0 ? 1 : 0);
