import { addYears, format } from "date-fns";
import { displayPremiumPoints } from "@/shared/lib/budget-metrics";
import { displayMoneyLarge, displayPercent, parseLocalDate } from "@/shared/lib/utils/display";
import { isIsoDate } from "@/shared/lib/utils/date-field";
import type { ComputerDifficulty, InitialAccount, InitialAccountPreview } from "@/types";

/** A campanha dura um ano e o mandato, quatro: menos que isso a partida não fecha um ciclo. */
export const GOVERNMENT_MIN_YEARS = 5;

/** Quanto o computador gasta por mês, em múltiplos da média dos partidos de jogadores. */
export const COMPUTER_DIFFICULTIES: { value: ComputerDifficulty; label: string; factor: number }[] = [
  { value: "EASY", label: "Fácil", factor: 0.5 },
  { value: "NORMAL", label: "Médio", factor: 1 },
  { value: "HARD", label: "Difícil", factor: 1.5 },
];

/** As duas contas iniciais do governo: de onde a partida parte na dívida e no resultado primário. */
export const INITIAL_ACCOUNTS: { value: InitialAccount; label: string }[] = [
  { value: "PLAYABLE", label: "Jogável" },
  { value: "REALISTIC", label: "Realista" },
];

const MEAN_BUDGET_EXAMPLE = 10_000;

/** "0,5 vez" / "1 vez" / "1,5 vez" */
function factorLabel(factor: number) {
  return `${factor.toLocaleString("pt-BR")} vez`;
}

/** O exemplo da dificuldade: com média de R$ 10.000 por mês, quanto cada partido do computador gasta. */
export function difficultyExample(difficulty: ComputerDifficulty) {
  const factor = COMPUTER_DIFFICULTIES.find((d) => d.value === difficulty)?.factor ?? 1;
  const spend = (MEAN_BUDGET_EXAMPLE * factor).toLocaleString("pt-BR");
  return `A verba mensal de cada partido do computador é ${factorLabel(factor)} a média dos partidos de jogadores: se a média for R$ 10.000, cada um deles gasta R$ ${spend} por mês.`;
}

/** Anos completos da partida, contados como o servidor: o fim alcança o início mais N anos. */
export function spansYears(start: string, end: string, years: number) {
  if (!isIsoDate(start) || !isIsoDate(end)) return false;
  return end >= format(addYears(parseLocalDate(start), years), "yyyy-MM-dd");
}

/** Quantos anos a partida tem, em anos cheios. */
export function wholeYears(start: string, end: string) {
  if (!isIsoDate(start) || !isIsoDate(end)) return 0;
  let years = 0;
  while (spansYears(start, end, years + 1)) years += 1;
  return years;
}

/** 7 de outubro do ano seguinte ao início; se a partida acaba antes, o último dia dela. */
export function defaultFirstElection(start: string, end: string) {
  if (!isIsoDate(start)) return "";
  const year = Number(start.slice(0, 4)) + 1;
  const election = `${year}-10-07`;
  return isIsoDate(end) && election > end ? end : election;
}

/** A candidatura abre um ano antes da eleição (ou no início da partida, se for depois). */
export function campaignOpening(start: string, firstElection: string) {
  if (!isIsoDate(firstElection)) return null;
  const opening = format(addYears(parseLocalDate(firstElection), -1), "yyyy-MM-dd");
  return isIsoDate(start) && opening < start ? start : opening;
}

type GovernmentRuleInput = { start: string; end: string; firstElection: string };

/** A mensagem de erro da expansão, ou nulo quando as datas servem. Os campos de data incompletos ficam para a máscara. */
export function governmentRuleError({ start, end, firstElection }: GovernmentRuleInput) {
  if (!isIsoDate(start) || !isIsoDate(end)) return null;
  if (!spansYears(start, end, GOVERNMENT_MIN_YEARS)) {
    return {
      path: "endDate" as const,
      message: `O Governo & Política pede uma partida de ${GOVERNMENT_MIN_YEARS} anos ou mais.`,
    };
  }
  if (!firstElection) return { path: "firstElection" as const, message: "Escolha a data da primeira eleição." };
  if (!isIsoDate(firstElection)) return null;
  if (!(firstElection > start && firstElection <= end)) {
    return { path: "firstElection" as const, message: "A primeira eleição precisa cair dentro da partida." };
  }
  return null;
}

/** "déficit primário de 1,7% do PIB por ano" / "superávit primário de ..." / "resultado primário zero" */
function primaryPhrase(primary: string) {
  const value = Number(primary);
  if (value === 0) return "resultado primário zero";
  return `${value < 0 ? "déficit" : "superávit"} primário de ${displayPercent(Math.abs(value), 1)} do PIB por ano`;
}

/** O prêmio chega em fração (0.0097) e sai em pontos percentuais. */
function premiumPhrase(premium: string) {
  if (Number(premium) === 0)
    return "A dívida está abaixo de 50% do PIB: os títulos do Tesouro ainda não cobram prêmio de risco.";
  return `O prêmio de risco já vale desde o início: ${displayPremiumPoints(premium)} a mais nos títulos do Tesouro.`;
}

/** O que a conta escolhida faz com o resultado primário, em uma frase. */
export function initialAccountDescription(account: InitialAccount, preview: InitialAccountPreview | undefined) {
  if (account === "PLAYABLE") {
    return "Começa com a dívida real do ano anterior e a receita igual ao gasto: a dívida só cresce com os juros, e o déficit nasce das medidas do governo.";
  }
  if (!preview) return "Começa com a dívida e o déficit reais do ano anterior ao início da partida.";
  return `O primeiro governo herda a conta real de ${preview.year}: dívida de ${displayPercent(preview.realistic.debt, 1)} do PIB e ${primaryPhrase(preview.realistic.primary)}.`;
}

export type InitialAccountExample = {
  year: number;
  /** Os números que a conta escolhida herda, na ordem em que aparecem */
  figures: string[];
  premium: string;
};

/** O exemplo da conta escolhida: a dívida, o resultado primário (com o valor em reais) e o prêmio que a dívida já cobra. */
export function initialAccountExample(account: InitialAccount, preview: InitialAccountPreview): InitialAccountExample {
  const option = account === "PLAYABLE" ? preview.playable : preview.realistic;
  const amount = Number(option.primary) === 0 ? "" : ` (${displayMoneyLarge(Math.abs(Number(option.primary_amount)))})`;
  return {
    year: preview.year,
    figures: [`dívida ${displayPercent(option.debt, 1)} do PIB`, `${primaryPhrase(option.primary)}${amount}`],
    premium: premiumPhrase(option.premium),
  };
}
