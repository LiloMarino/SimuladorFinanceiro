import {
  Armchair,
  Banknote,
  Briefcase,
  Building2,
  ChartCandlestick,
  Gem,
  Gavel,
  GraduationCap,
  HandCoins,
  Handshake,
  Landmark,
  Laptop,
  Ship,
  Store,
  type LucideIcon,
} from "lucide-react";
import type { IncomeLoss, LifeStatus, Profession, SimulationSettings } from "@/types";

/** As regras da sala que decidem o que cada profissão sente: o card só mostra o que vale na partida. */
export type RoomRules = Pick<
  SimulationSettings["simulation"],
  "funds_enabled" | "government_enabled" | "inflation_adjusted" | "monthly_salary"
>;

/** Regra da sala de que uma vantagem, desvantagem ou etiqueta depende; todas precisam estar ligadas. */
type RoomRequirement = "government" | "funds" | "inflationAdjusted";

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
  /** A frase que abre a página da profissão: o que ela é e o que mexe na renda */
  description: string;
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
  requires?: RoomRequirement;
  /** A profissão exige mais do jogador que as outras: ganha o selo "difícil" no card */
  hard?: boolean;
  /** A renda segue um partido que o jogador escolhe ao entrar; o bot não escolhe, então não a recebe */
  partyBound?: boolean;
};

/** O nome da expansão que a regra exige; as regras que não são expansão ficam de fora. */
export const EXPANSION_NAME: Partial<Record<RoomRequirement, string>> = {
  government: "Governo & Política",
  funds: "Gestoras",
};

const GOVERNMENT: RoomRequirement[] = ["government"];
const GOVERNMENT_RAISE: RoomRequirement[] = ["government", "inflationAdjusted"];
const INFLATION: RoomRequirement[] = ["inflationAdjusted"];

export const PROFESSIONS: Record<Profession, ProfessionInfo> = {
  CLT: {
    name: "CLT",
    icon: Briefcase,
    description:
      "Carteira assinada: salário estável, reajuste que acompanha o PIB e risco de demissão quando o desemprego sobe.",
    incomeMultiple: 1,
    gains: [{ text: "Renda cheia" }, { text: "Aumento acima da inflação quando o PIB cresce", requires: INFLATION }],
    losses: [{ text: "Pode ser demitido e ficar um mês sem salário, mais quando o desemprego sobe" }],
    tags: [{ key: "unemployment" }, { key: "gdp" }, { key: "personalTax", requires: GOVERNMENT }],
  },
  PUBLIC_SERVANT: {
    name: "Servidor",
    icon: Landmark,
    description:
      "Cargo público: nunca é demitido, o salário é um pouco menor e o reajuste acima da inflação depende do governo da sala.",
    incomeMultiple: 0.95,
    gains: [
      { text: "Nunca é demitido" },
      { text: "Aumento acima da inflação quando o governo dá aos servidores", requires: GOVERNMENT_RAISE },
    ],
    losses: [{ text: "Ganha 5% menos que o CLT" }],
    tags: [
      { key: "servantRaise", requires: GOVERNMENT_RAISE },
      { key: "personalTax", requires: GOVERNMENT },
    ],
  },
  ENTREPRENEUR: {
    name: "Empreendedor",
    icon: Store,
    description:
      "Negócio próprio: o lucro é maior que o salário do CLT e segue o PIB. Parte dele pode voltar para a empresa e virar capital, que rende com o PIB.",
    incomeMultiple: 1.1,
    gains: [
      { text: "Ganha 10% mais que o CLT" },
      { text: "Não é demitido" },
      { text: "A renda sobe quando o PIB passa de 2% ao ano" },
      { text: "Reinveste parte do lucro e o capital da empresa rende com o PIB" },
    ],
    losses: [
      { text: "A renda cai quando o PIB fica abaixo de 2%, até a metade" },
      { text: "O capital encolhe com o PIB negativo e só vira caixa vendendo, com 20% de desconto" },
    ],
    tags: [{ key: "gdp" }, { key: "corporateTax", requires: GOVERNMENT }],
  },
  RETIREE: {
    name: "Aposentado",
    icon: Armchair,
    description:
      "Aposentadoria: nunca é demitido, o reajuste acima da inflação depende do governo da sala e a saúde custa o dobro. A previdência rende o CDI menos 1% e vira renda vitalícia ou é resgatada com IR regressivo.",
    incomeMultiple: 0.95,
    gains: [
      { text: "Nunca é demitido" },
      { text: "Aumento acima da inflação quando o governo dá aos aposentados", requires: GOVERNMENT_RAISE },
      { text: "Previdência que rende o CDI menos 1% e vira renda para sempre" },
    ],
    losses: [
      { text: "Ganha 5% menos que o CLT" },
      { text: "Despesa de saúde custa o dobro" },
      { text: "Resgatar a previdência paga IR de 35% a 10%, pelo tempo no plano" },
    ],
    tags: [
      { key: "retireeRaise", requires: GOVERNMENT_RAISE },
      { key: "personalTax", requires: GOVERNMENT },
    ],
  },
  WELFARE: {
    name: "Auxílio",
    icon: HandCoins,
    description:
      "Auxílio do governo: parte da renda nunca some, mas o resto é bico, que o sorteio de demissão tira por um mês. A despesa tem tarifa social, o governo deposita no Pé-de-Meia e o curso técnico leva a um emprego de CLT.",
    incomeMultiple: 0.5,
    benefitMultiple: 0.45,
    gains: [
      { text: "O auxílio nunca some, nem no sorteio de demissão" },
      { text: "Tarifa social: a despesa que você paga é 15% menor" },
      { text: "Pé-de-Meia: o governo deposita parte da sobra do mês, e o saldo libera a cada 2 anos" },
      { text: "Curso técnico de 12 meses que leva a um emprego de CLT" },
    ],
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
    description: "Aluguéis: renda maior que a do CLT, mas o imóvel pode ficar vago quando o desemprego sobe.",
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
    description:
      "Vende para fora: a renda acompanha o dólar, sobe quando ele sobe e cai quando ele cai, e o sorteio de demissão não pega.",
    incomeMultiple: 1.05,
    gains: [{ text: "Não é demitido" }, { text: "A renda sobe com o dólar, até o dobro" }],
    losses: [{ text: "A renda cai quando o dólar cai, até a metade" }],
    tags: [{ key: "dollar" }, { key: "corporateTax", requires: GOVERNMENT }],
  },
  BANKER: {
    name: "Bancário",
    icon: Banknote,
    description:
      "Banco: renda maior que a do CLT, que acompanha a SELIC, com risco de demissão quando o desemprego sobe.",
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
    description:
      "Trabalho por conta própria: a maior renda entre as profissões. Você define o preço por atendimento: acima da referência do mercado rende mais por cliente e perde clientes, parado perde para a inflação, e o mês sem cliente tira a renda.",
    incomeMultiple: 1.4,
    gains: [{ text: "Ganha 40% mais que o CLT" }],
    losses: [
      { text: "O sorteio de demissão vira um mês sem cliente: um mês sem renda" },
      {
        text: "A renda só acompanha a inflação se você reajustar o preço: parado, a despesa sobe e a renda fica para trás",
      },
    ],
    tags: [{ key: "unemployment" }, { key: "personalTax", requires: GOVERNMENT }],
    requires: "inflationAdjusted",
  },
  BROKER: {
    name: "Corretor",
    icon: ChartCandlestick,
    description:
      "Mercado de ações: a renda acompanha o retorno do Ibovespa em 12 meses, e o sorteio de demissão não pega.",
    incomeMultiple: 1.05,
    gains: [{ text: "Não é demitido" }, { text: "A renda sobe quando o Ibovespa rende mais de 12% em 12 meses" }],
    losses: [{ text: "A renda cai quando o Ibovespa rende menos, até 60% a menos" }],
    tags: [{ key: "stocks" }, { key: "personalTax", requires: GOVERNMENT }],
  },
  HEIR: {
    name: "Herdeiro",
    icon: Gem,
    description:
      "Herança: começa com capital, nunca é demitido e não tem renda de trabalho, então a despesa sai do patrimônio.",
    incomeMultiple: 0,
    gains: [
      { text: "Começa com o capital da sala mais uma herança que cobre os salários da partida" },
      { text: "Nunca é demitido" },
    ],
    losses: [{ text: "Não tem renda de trabalho: a despesa sai do patrimônio" }],
    tags: [],
    hard: true,
  },
  NEW_GRADUATE: {
    name: "Recém-formado",
    icon: GraduationCap,
    description:
      "Começo de carreira: salário menor que o do CLT que sobe em linha reta em 10 anos, com demissão mais provável no início.",
    incomeMultiple: 0.85,
    gains: [
      { text: "A renda sobe em linha reta até 1,3× o salário em 10 anos" },
      { text: "Aumento acima da inflação quando o PIB cresce", requires: INFLATION },
    ],
    losses: [
      { text: "Começa ganhando 15% menos que o CLT, sem capital" },
      { text: "Chance de demissão dobrada no começo, caindo até a do CLT em 10 anos" },
    ],
    tags: [{ key: "unemployment" }, { key: "gdp" }, { key: "personalTax", requires: GOVERNMENT }],
  },
  COMMISSIONED: {
    name: "Comissionado",
    icon: Handshake,
    description: "Cargo de confiança: renda maior enquanto o seu partido está no governo, menor quando ele sai.",
    incomeMultiple: 1.5,
    gains: [{ text: "Ganha 50% mais que o CLT enquanto o seu partido está na presidência ou na base" }],
    losses: [
      { text: "Ganha 50% menos que o CLT quando o partido sai do governo" },
      { text: "A renda só muda no mês seguinte à troca de governo" },
    ],
    tags: [{ key: "personalTax", requires: GOVERNMENT }],
    requires: "government",
    partyBound: true,
  },
  OFFERS_BANKER: {
    name: "Banqueiro de ofertas",
    icon: Gavel,
    description:
      "Coordena as ofertas de ações da sala: ganha comissão sobre cada oferta que fecha, e o salário fixo é baixo.",
    incomeMultiple: 0.7,
    gains: [{ text: "Recebe 1% de toda oferta pública e emissão de cotas da sala, dividido com os outros banqueiros" }],
    losses: [
      { text: "Ganha 30% menos que o CLT de salário fixo" },
      { text: "Pode ser demitido e ficar um mês sem salário, mais quando o desemprego sobe" },
    ],
    tags: [{ key: "unemployment" }, { key: "personalTax", requires: GOVERNMENT }],
    requires: "funds",
  },
};

/** As profissões que a sala oferece, na ordem das cartas: as que exigem uma regra ou expansão somem sem ela. */
export function availableProfessions(
  room: Pick<RoomRules, "funds_enabled" | "government_enabled" | "inflation_adjusted">,
) {
  return (Object.keys(PROFESSIONS) as Profession[]).filter((profession) => {
    const { requires } = PROFESSIONS[profession];
    return !requires || isActive([requires], room);
  });
}

/** As profissões que o bot pode ter: as da sala, sem as que seguem um partido escolhido pelo jogador. */
export function availableBotProfessions(
  room: Pick<RoomRules, "funds_enabled" | "government_enabled" | "inflation_adjusted">,
) {
  return availableProfessions(room).filter((profession) => !PROFESSIONS[profession].partyBound);
}

/** Renda de partida da profissão sobre o salário do host; o auxílio conta no gasto de referência. */
export function professionIncome(profession: Profession, salary: number) {
  const { incomeMultiple, benefitMultiple = 0 } = PROFESSIONS[profession];
  return salary * (incomeMultiple + benefitMultiple);
}

const ROOM_RULE: Record<
  RoomRequirement,
  keyof Pick<RoomRules, "funds_enabled" | "government_enabled" | "inflation_adjusted">
> = {
  government: "government_enabled",
  funds: "funds_enabled",
  inflationAdjusted: "inflation_adjusted",
};

function isActive(
  requires: RoomRequirement[] | undefined,
  room: Pick<RoomRules, "funds_enabled" | "government_enabled" | "inflation_adjusted">,
) {
  return (requires ?? []).every((rule) => room[ROOM_RULE[rule]]);
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

/** O imposto cujo desvio contra a lei corta (ou soma à) a renda da profissão. */
export const TAX_NAMES: Record<NonNullable<LifeStatus["tax"]>, string> = {
  PERSONAL: "Imposto de renda das pessoas",
  CORPORATE: "Imposto de renda das empresas",
  CONSUMPTION: "Imposto sobre consumo",
};
