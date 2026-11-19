import { POLICY_LABEL, sizeLabel } from "@/shared/lib/state-company";
import { displayMonthName, displayPercent, parseLocalDate } from "@/shared/lib/utils/display";
import type { DividendPolicy, StateCompanyDetail, StateCompanyHolders, StateCompanyMonth } from "@/types";

/** O que cada política faz com o lucro que sobra e com o porte da empresa. */
const POLICY_EFFECT: Record<DividendPolicy, string> = {
  REINVEST: "O resto vira investimento e o porte cresce 1% ao mês.",
  NORMAL: "",
  SQUEEZE: "Sobra pouco para investir e o porte encolhe.",
};

/** O payout da política em vigor, da tabela de políticas que a API manda. */
export function currentPayout(company: StateCompanyDetail) {
  return company.policies.find((option) => option.dividend_policy === company.dividend_policy)?.payout ?? null;
}

/** "Paga 50% do lucro." mais o que a política faz com o resto. */
export function policyDescription({ dividend_policy, payout }: StateCompanyDetail["policies"][number]) {
  const paid = `Paga ${displayPercent(payout, 0)} do lucro.`;
  return POLICY_EFFECT[dividend_policy] ? `${paid} ${POLICY_EFFECT[dividend_policy]}` : paid;
}

/** "03/2026": o mês da fundação em algarismos, como a linha de origem o lê. */
function monthNumbers(isoDate: string) {
  const date = parseLocalDate(isoDate);
  return `${String(date.getMonth() + 1).padStart(2, "0")}/${date.getFullYear()}`;
}

/** A linha de origem sob o nome da ação: de onde a estatal veio e quanto dela o governo tem. */
export function originLine(company: StateCompanyDetail) {
  const share = Number(company.government_share);
  const stake =
    share > 0 ? `o governo tem ${displayPercent(share, 0, { trim: true })} das ações` : "já foi privatizada";
  if (company.origin === "IMPORTED" || company.founded_on === null || company.size === null) {
    return `Importada · já existia na bolsa · ${stake}`;
  }
  return `Fundada pelo governo em ${monthNumbers(company.founded_on)} · porte ${sizeLabel(company.size)} · ${stake}`;
}

/** Os meses fechados com lucro apurado: os que contam no "em N meses" dos dividendos. */
export function settledMonths(months: StateCompanyMonth[]) {
  return months.filter((month) => month.reason === "PAID" || month.reason === "LOSS");
}

/** O texto da coluna "Por quê": a regra que fez o mês pagar o que pagou. */
export function reasonText(month: StateCompanyMonth) {
  switch (month.reason) {
    case "PAID":
      return month.payout !== null && month.dividend_policy !== null
        ? `${displayPercent(month.payout, 0)} do lucro, pela política ${POLICY_LABEL[month.dividend_policy]}`
        : "Dividendo pago sobre o lucro do mês";
    case "LOSS":
      return "Prejuízo no mês: com lucro negativo, não há o que dividir.";
    case "FOUNDING":
      return "Mês da fundação: o primeiro dividendo sai sobre o lucro do primeiro mês inteiro.";
    case "PRIVATIZED":
      return "Privatizada neste mês: deixou de seguir a política do governo.";
  }
}

/** "O de novembro sai em 01/12.": o mês que ainda está aberto e o dia em que ele fecha; nulo depois da venda. */
export function nextCloseNote(months: StateCompanyMonth[]) {
  const last = months.at(-1);
  if (!last || last.reason === "PRIVATIZED") return null;
  const closing = parseLocalDate(last.month);
  closing.setMonth(closing.getMonth() + 2, 1);
  const closingMonth = String(closing.getMonth() + 1).padStart(2, "0");
  return `O de ${displayMonthName(last.month, 1)} sai em 01/${closingMonth}.`;
}

/** O rendimento dos dividendos sobre o preço; nulo sem preço. */
export function dividendYield(company: StateCompanyDetail) {
  const price = company.price === null ? 0 : Number(company.price);
  return price > 0 ? Number(company.dividends) / price : null;
}

/** Cada fatia de quem tem as ações, como fração do total de ações; "players" soma os outros jogadores e você. */
export function holderShares(holders: StateCompanyHolders) {
  const total =
    Number(holders.government) +
    Number(holders.maker) +
    Number(holders.players) +
    Number(holders.bots) +
    Number(holders.funds) +
    Number(holders.you);
  const part = (...values: string[]) => (total > 0 ? values.reduce((sum, value) => sum + Number(value), 0) / total : 0);
  return {
    government: part(holders.government),
    maker: part(holders.maker),
    players: part(holders.players, holders.you),
    bots: part(holders.bots),
    funds: part(holders.funds),
    you: part(holders.you),
  };
}
