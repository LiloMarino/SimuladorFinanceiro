import { isManagedFundAccount, isSovereignAccount } from "@/shared/lib/active-account";
import type { FundAccount } from "@/types";

/**
 * Por onde o automático de uma conta é lido e gravado: a conta pessoal e cada gestora têm rota própria;
 * o Fundo Soberano não tem automático.
 * `pending` é a conta do topo ainda desconhecida: há escolha de conta e a lista não chegou.
 */
export type StrategyRoute =
  | { kind: "personal" }
  | { kind: "fund"; fundId: number }
  | { kind: "sovereign" }
  | { kind: "pending" };

const PERSONAL_ROUTE: StrategyRoute = { kind: "personal" };

const PENDING_ROUTE: StrategyRoute = { kind: "pending" };

/** A rota da conta em uso; sem conta, vale a pessoal (expansões desligadas) ou a rota pendente (lista de contas a caminho). */
export function strategyRoute(account: FundAccount | undefined, accountsPending = false): StrategyRoute {
  if (account === undefined) return accountsPending ? PENDING_ROUTE : PERSONAL_ROUTE;
  if (account.fund_id === null) return PERSONAL_ROUTE;
  if (isSovereignAccount(account)) return { kind: "sovereign" };
  return isManagedFundAccount(account) ? { kind: "fund", fundId: account.fund_id } : PERSONAL_ROUTE;
}

/** A gestora cuja rota serve a conta; nula na pessoal e no Fundo Soberano. */
export const strategyFundId = (route: StrategyRoute) => (route.kind === "fund" ? route.fundId : null);

/** Os endereços do automático da conta: o modo, o registro e a prévia de uma estratégia. */
export function strategyPaths(fundId: number | null) {
  const mine = fundId === null ? "/api/strategies/me" : `/api/funds/${fundId}/strategy`;
  return {
    mine,
    log: `${mine}/log`,
    view: (key: string) => (fundId === null ? `/api/strategies/${key}/view` : `${mine}/${key}/view`),
  };
}
