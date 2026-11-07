import { describeSplit } from "@/shared/lib/split-ratio";
import { displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import type { SimulationEvents } from "@/types";

type CorporateActions = SimulationEvents["corporate_actions"];

/** Quantos ativos aparecem no aviso de proventos; o resto vira "e mais N". */
const LISTED_PAYERS = 3;

export interface ToastText {
  title: string;
  description?: string;
}

/** Um aviso por pregão somando os proventos: o total no caixa e os ativos que mais pagaram. */
export function dividendsToast({ dividends, dividends_total }: CorporateActions): ToastText | null {
  if (dividends.length === 0) return null;
  const ranked = [...dividends].sort((a, b) => Number(b.amount) - Number(a.amount));
  const listed = ranked.slice(0, LISTED_PAYERS).map((line) => `${line.ticker} ${displayMoney(line.amount)}`);
  const rest = ranked.length - LISTED_PAYERS;

  return {
    title: `Proventos de ${displayMoney(dividends_total)} no caixa`,
    description: `${listed.join(" · ")}${rest > 0 ? ` e mais ${rest}` : ""}`,
  };
}

/** Um aviso por desdobramento ou grupamento: a razão, a nova quantidade e a fração paga em dinheiro. */
export function splitToast(split: CorporateActions["splits"][number]): ToastText {
  const { name, label } = describeSplit(split.ratio);
  const quantity = `Suas ações foram de ${displayQuantity(split.shares_before)} para ${displayQuantity(split.shares_after)}.`;
  const fraction =
    Number(split.fraction_amount) > 0
      ? ` A fração que sobrou foi paga em dinheiro: ${displayMoney(split.fraction_amount)}.`
      : "";

  return { title: `${name} ${label} em ${split.ticker}`, description: `${quantity}${fraction}` };
}
