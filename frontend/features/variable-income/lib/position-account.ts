import { isSovereignAccount } from "@/shared/lib/active-account";
import type { FundAccount } from "@/types";

type PositionAccount = Pick<FundAccount, "fund_id" | "name" | "role">;

/** O título do card de posição de uma conta que opera: a gestora é "da", o Fundo Soberano é "do". */
export function positionTitle(account: PositionAccount) {
  return `Posição ${isSovereignAccount(account) ? "do" : "da"} ${account.name}`;
}

/** O texto do card de posição quando a conta que opera não tem o ativo: a gestora é "A", o Fundo Soberano é "O". */
export function positionEmptyText(account: PositionAccount, ticker: string) {
  return `${isSovereignAccount(account) ? "O" : "A"} ${account.name} não tem ${ticker}.`;
}
