import { isSovereignAccount } from "@/shared/lib/active-account";
import type { FundAccount } from "@/types";

type TicketAccount = Pick<FundAccount, "fund_id" | "name" | "role">;

/** O cabeçalho da boleta de uma conta que opera: a gestora ou o Fundo Soberano, com o papel de co-gestor quando é o caso. */
export function ticketAccountHeading(account: TicketAccount) {
  const owner = isSovereignAccount(account) ? `pelo ${account.name}` : `pela ${account.name}`;
  return `Operando ${owner}${account.role === "comanager" ? " · você é co-gestor" : ""}`;
}

/** O texto do botão da boleta de uma conta que opera; comprar e vender dizem a conta, e o lado da ordem se lê no seletor. */
export function ticketAccountSubmitLabel(account: TicketAccount, action: "buy" | "sell", ticker: string) {
  const verb = action === "sell" ? "Vender" : "Comprar";
  return isSovereignAccount(account) ? `${verb} pelo ${account.name}` : `${verb} ${ticker} pela gestora`;
}
