import {
  Armchair,
  Banknote,
  Briefcase,
  Building2,
  ChartCandlestick,
  Gem,
  GraduationCap,
  HandCoins,
  Landmark,
  Laptop,
  Ship,
  Store,
  type LucideIcon,
} from "lucide-react";
import type { IncomeDriver, IncomeLoss, LifeStatus, Profession, SimulationSettings } from "@/types";

/** As regras da sala que decidem o que cada profissão sente: o card só mostra o que vale na partida. */
export type RoomRules = Pick<
  SimulationSettings["simulation"],
  "government_enabled" | "inflation_adjusted" | "monthly_salary"
>;

/** Regra da sala de que uma vantagem, desvantagem ou etiqueta depende; todas precisam estar ligadas. */
type RoomRequirement = "government" | "inflationAdjusted";

export type TagKey =
  | "unemployment"
  | "gdp"
  | "dollar"
  | "selic"
  | "stocks"
  | "personalTax"
  | "corporateTax"
  | "consumptionTax"
  | "servantRaise"
  | "retireeRaise"
  | "welfareSpending";

type ProfessionPoint = { text: string; requires?: RoomRequirement[] };
type ProfessionTag = { key: TagKey; requires?: RoomRequirement[] };

export type ProfessionInfo = {
  name: string;
  icon: LucideIcon;
  /** Renda do mês em múltiplos do salário que o host definiu */
  incomeMultiple: number;
  /** Quanto da renda vem do auxílio do governo, nos gastos de referência (o resto é a renda do trabalho) */
  benefitMultiple?: number;
  /** O que a profissão tem de melhor que as outras */
  gains: ProfessionPoint[];
  /** O que a profissão tem de pior que as outras */
  losses: ProfessionPoint[];
  /** O que muda a renda da profissão durante a partida */
  tags: ProfessionTag[];
  /** A regra que a sala precisa ter ligada para a profissão existir; sem ela some da escolha */
  requires?: Extract<RoomRequirement, "inflationAdjusted">;
};

const GOVERNMENT: RoomRequirement[] = ["government"];
const GOVERNMENT_RAISE: RoomRequirement[] = ["government", "inflationAdjusted"];
const INFLATION: RoomRequirement[] = ["inflationAdjusted"];

export const PROFESSIONS: Record<Profession, ProfessionInfo> = {
  CLT: {
    name: "CLT",
    icon: Briefcase,
    incomeMultiple: 1,
    gains: [{ text: "Renda cheia" }, { text: "Aumento acima da inflação quando o PIB cresce", requires: INFLATION }],
    losses: [{ text: "Pode ser demitido e ficar um mês sem salário, mais quando o desemprego sobe" }],
    tags: [{ key: "unemployment" }, { key: "gdp" }, { key: "personalTax", requires: GOVERNMENT }],
  },
  PUBLIC_SERVANT: {
    name: "Servidor",
    icon: Landmark,
    incomeMultiple: 0.9,
    gains: [
      { text: "Nunca é demitido" },
      { text: "Aumento acima da inflação quando o governo dá aos servidores", requires: GOVERNMENT_RAISE },
    ],
    losses: [{ text: "Ganha 10% menos que o CLT" }],
    tags: [
      { key: "servantRaise", requires: GOVERNMENT_RAISE },
      { key: "personalTax", requires: GOVERNMENT },
    ],
  },
  ENTREPRENEUR: {
    name: "Empreendedor",
    icon: Store,
    incomeMultiple: 1.2,
    gains: [
      { text: "Ganha 20% mais que o CLT" },
      { text: "Não é demitido" },
      { text: "A renda sobe quando o PIB passa de 2% ao ano" },
    ],
    losses: [{ text: "A renda cai quando o PIB fica abaixo de 2%, até a metade" }],
    tags: [{ key: "gdp" }, { key: "corporateTax", requires: GOVERNMENT }],
  },
  RETIREE: {
    name: "Aposentado",
    icon: Armchair,
    incomeMultiple: 0.85,
    gains: [
      { text: "Nunca é demitido" },
      { text: "Aumento acima da inflação quando o governo dá aos aposentados", requires: GOVERNMENT_RAISE },
    ],
    losses: [{ text: "Ganha 15% menos que o CLT" }, { text: "Despesa de saúde custa o dobro" }],
    tags: [
      { key: "retireeRaise", requires: GOVERNMENT_RAISE },
      { key: "personalTax", requires: GOVERNMENT },
    ],
  },
  WELFARE: {
    name: "Auxílio",
    icon: HandCoins,
    incomeMultiple: 0.5,
    benefitMultiple: 0.4,
    gains: [{ text: "O auxílio nunca some, nem no sorteio de demissão" }],
    losses: [{ text: "Mais da metade da renda é bico, e o sorteio de demissão tira o bico por um mês" }],
    tags: [
      { key: "unemployment" },
      { key: "welfareSpending", requires: GOVERNMENT },
      { key: "consumptionTax", requires: GOVERNMENT },
    ],
  },
  LANDLORD: {
    name: "Locador",
    icon: Building2,
    incomeMultiple: 1.1,
    gains: [{ text: "Ganha 10% mais que o CLT" }],
    losses: [
      { text: "O sorteio de demissão deixa o imóvel vago: um mês sem aluguel" },
      { text: "O aluguel só sobe com a inflação", requires: INFLATION },
    ],
    tags: [{ key: "unemployment" }, { key: "personalTax", requires: GOVERNMENT }],
  },
  EXPORTER: {
    name: "Exportador",
    icon: Ship,
    incomeMultiple: 1.05,
    gains: [{ text: "Não é demitido" }, { text: "A renda sobe com o dólar, até o dobro" }],
    losses: [{ text: "A renda cai quando o dólar cai, até a metade" }],
    tags: [{ key: "dollar" }, { key: "corporateTax", requires: GOVERNMENT }],
  },
  BANKER: {
    name: "Bancário",
    icon: Banknote,
    incomeMultiple: 1.1,
    gains: [{ text: "Ganha 10% mais que o CLT" }, { text: "A renda sobe quando a SELIC passa de 12% ao ano" }],
    losses: [
      { text: "Pode ser demitido e ficar um mês sem salário, mais quando o desemprego sobe" },
      { text: "A renda cai quando a SELIC fica abaixo de 12% ao ano" },
    ],
    tags: [{ key: "unemployment" }, { key: "selic" }, { key: "personalTax", requires: GOVERNMENT }],
  },
  FREELANCER: {
    name: "Autônomo",
    icon: Laptop,
    incomeMultiple: 1.4,
    gains: [{ text: "Ganha 40% mais que o CLT" }],
    losses: [
      { text: "O sorteio de demissão vira um mês sem cliente: um mês sem renda" },
      { text: "A renda não sobe com a inflação: a despesa sobe e a renda fica parada" },
    ],
    tags: [{ key: "unemployment" }, { key: "personalTax", requires: GOVERNMENT }],
    requires: "inflationAdjusted",
  },
  BROKER: {
    name: "Corretor",
    icon: ChartCandlestick,
    incomeMultiple: 1.05,
    gains: [{ text: "Não é demitido" }, { text: "A renda sobe quando o Ibovespa rende mais de 12% em 12 meses" }],
    losses: [{ text: "A renda cai quando o Ibovespa rende menos, até 60% a menos" }],
    tags: [{ key: "stocks" }, { key: "personalTax", requires: GOVERNMENT }],
  },
  HEIR: {
    name: "Herdeiro",
    icon: Gem,
    incomeMultiple: 0,
    gains: [
      { text: "Começa com o capital da sala mais uma herança que cobre os salários da partida" },
      { text: "Nunca é demitido" },
    ],
    losses: [{ text: "Não tem renda de trabalho: a despesa sai do patrimônio" }],
    tags: [],
  },
  NEW_GRADUATE: {
    name: "Recém-formado",
    icon: GraduationCap,
    incomeMultiple: 0.6,
    gains: [
      { text: "A renda sobe em linha reta até 1,5× o salário em 10 anos" },
      { text: "Aumento acima da inflação quando o PIB cresce", requires: INFLATION },
    ],
    losses: [
      { text: "Começa ganhando 40% menos que o CLT, sem capital" },
      { text: "Chance de demissão dobrada no começo, caindo até a do CLT em 10 anos" },
    ],
    tags: [{ key: "unemployment" }, { key: "gdp" }, { key: "personalTax", requires: GOVERNMENT }],
  },
};

/** As profissões que a sala oferece, na ordem das cartas: as que exigem a correção pela inflação somem sem ela. */
export function availableProfessions(room: Pick<RoomRules, "inflation_adjusted">) {
  return (Object.keys(PROFESSIONS) as Profession[]).filter(
    (profession) => !PROFESSIONS[profession].requires || room.inflation_adjusted,
  );
}

/** Renda de partida da profissão sobre o salário do host; o auxílio conta no gasto de referência. */
export function professionIncome(profession: Profession, salary: number) {
  const { incomeMultiple, benefitMultiple = 0 } = PROFESSIONS[profession];
  return salary * (incomeMultiple + benefitMultiple);
}

function isActive(requires: RoomRequirement[] | undefined, room: RoomRules) {
  return (requires ?? []).every((rule) => (rule === "government" ? room.government_enabled : room.inflation_adjusted));
}

/** O que a profissão tem de vantagem, desvantagem e etiqueta nas regras desta sala. */
export function visibleProfession(profession: Profession, room: RoomRules) {
  const { gains, losses, tags } = PROFESSIONS[profession];
  return {
    gains: gains.filter((point) => isActive(point.requires, room)),
    losses: losses.filter((point) => isActive(point.requires, room)),
    tags: tags.filter((tag) => isActive(tag.requires, room)).map((tag) => tag.key),
  };
}

/** O nome de cada etiqueta "Afetado por". */
export const TAG_NAMES: Record<TagKey, string> = {
  unemployment: "Desemprego",
  gdp: "PIB",
  dollar: "Dólar",
  selic: "SELIC",
  stocks: "Ibovespa",
  personalTax: "IR das pessoas",
  corporateTax: "IR das empresas",
  consumptionTax: "Imposto sobre consumo",
  servantRaise: "Aumento dos servidores",
  retireeRaise: "Aumento dos aposentados",
  welfareSpending: "Gasto com auxílio",
};

/** O que a demissão sorteada tira de cada profissão que a sente. */
export const INCOME_LOSS_NAMES: Record<IncomeLoss, { event: string; missing: string }> = {
  LAYOFF: { event: "Demitido", missing: "o salário" },
  GIG_LOSS: { event: "Bico perdido", missing: "a renda do bico" },
  VACANCY: { event: "Imóvel vago", missing: "o aluguel" },
  NO_CLIENTS: { event: "Mês sem cliente", missing: "a renda" },
};

/** A variável que move a renda da profissão, como a linha do card da vida financeira a nomeia. */
export const DRIVER_NAMES: Record<IncomeDriver, string> = {
  GDP: "PIB em 12 meses",
  DOLLAR: "Variação do dólar em 12 meses",
  SELIC: "SELIC ao ano",
  STOCKS: "Retorno do Ibovespa em 12 meses",
};

/** O imposto cujo desvio contra a lei corta (ou soma à) a renda da profissão. */
export const TAX_NAMES: Record<NonNullable<LifeStatus["tax"]>, string> = {
  PERSONAL: "Imposto de renda das pessoas",
  CORPORATE: "Imposto de renda das empresas",
  CONSUMPTION: "Imposto sobre consumo",
};
