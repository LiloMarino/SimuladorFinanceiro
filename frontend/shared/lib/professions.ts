import { Armchair, Briefcase, Building2, HandCoins, Landmark, Store, type LucideIcon } from "lucide-react";
import type { IncomeLoss, LifeStatus, Profession, SimulationSettings } from "@/types";

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
};

export const PROFESSION_ORDER = Object.keys(PROFESSIONS) as Profession[];

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
};

/** O imposto cujo desvio contra a lei corta (ou soma à) a renda da profissão. */
export const TAX_NAMES: Record<NonNullable<LifeStatus["tax"]>, string> = {
  PERSONAL: "Imposto de renda das pessoas",
  CORPORATE: "Imposto de renda das empresas",
  CONSUMPTION: "Imposto sobre consumo",
};
