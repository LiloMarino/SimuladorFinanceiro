import type { PortfolioState } from "@/types";

type LockedKind = PortfolioState["locked_assets"][number]["kind"];

/** Nome e saída curta de cada tipo de patrimônio travado, numa definição só: toda tela que nomeia o tipo lê daqui. */
const LOCKED_KINDS: Record<LockedKind, { label: string; exit: string }> = {
  FGTS: { label: "FGTS", exit: "só sai na demissão" },
  COMPANY_CAPITAL: { label: "Capital da empresa", exit: "só sai vendendo" },
};

/** O nome e a saída do patrimônio travado quando nenhum tipo está em mãos (o histórico guarda só o saldo somado). */
const GENERIC = { label: "Patrimônio travado", exit: "só sai pela regra da profissão" };

export const GENERIC_LOCKED_LABEL = GENERIC.label;

export const lockedLabel = (kind: LockedKind) => LOCKED_KINDS[kind].label;

/** Os tipos que o jogador tem agora, juntos num nome só ("FGTS", "Capital da empresa"). */
export function lockedLabels(portfolio: PortfolioState) {
  return joined(portfolio, "label");
}

/** A saída curta dos tipos que o jogador tem agora ("só sai na demissão"). */
export function lockedExits(portfolio: PortfolioState) {
  return joined(portfolio, "exit");
}

function joined(portfolio: PortfolioState, field: "label" | "exit") {
  const kinds = portfolio.locked_assets.map((asset) => LOCKED_KINDS[asset.kind][field]);
  return kinds.length > 0 ? kinds.join(" + ") : GENERIC[field];
}
