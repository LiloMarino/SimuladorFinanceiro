import type ApiError from "@/shared/lib/models/ApiError";
import type { FundAccount } from "@/types";

/** Por que o crédito da conta ativa está travado: o Fundo Soberano não toma crédito, e o co-gestor não contrata pela gestora. */
export type CreditLock = "sovereign" | "comanager";

// Os motivos tipados que o servidor devolve no 403 do crédito
const LOCK_CODES: Record<string, CreditLock> = {
  credit_sovereign_fund: "sovereign",
  credit_comanager: "comanager",
};

/** O travamento pela conta ativa: o papel dela na gestora decide, sem esperar a resposta do servidor. */
export function creditLockOfAccount(active: Pick<FundAccount, "role"> | undefined): CreditLock | null {
  if (active?.role === "president") return "sovereign";
  if (active?.role === "comanager") return "comanager";
  return null;
}

/** O travamento pelo motivo do 403; o servidor é a garantia quando a conta ativa ainda não carregou. */
export function creditLockOfError(error: ApiError | null): CreditLock | null {
  return (error?.code && LOCK_CODES[error.code]) || null;
}
