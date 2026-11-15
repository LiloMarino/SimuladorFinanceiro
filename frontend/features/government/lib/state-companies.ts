import { displayPoints } from "@/shared/lib/budget-metrics";
import { STATE_LEVER_LABEL } from "@/shared/lib/state-lever";
import { displayDayMonth, displayMoney, displayMoneyLarge, displayPercent } from "@/shared/lib/utils/display";
import type {
  DividendPolicy,
  GovernmentMeasure,
  StateCompaniesPanel,
  StateCompany,
  StateCompanySize,
  StateControl,
  StateLever,
  StateMovement,
  StateOffer,
  StateOrderPreview,
  StateRules,
} from "@/types";
import { daysUntil } from "./government";

const MINUS = "−";

/** O peso de cada alavanca vem do backend: o texto lê o que o painel entrega. */
export function leverEffect(rules: StateRules, lever: StateLever) {
  const rule = rules.levers.find((item) => item.lever === lever);
  if (!rule) return "";
  const tenPercent = (weight: string) => pointsLabel(Number(weight) * 10);
  if (lever === "BANK") {
    return `Baixar o juro do crédito sobe o PIB, com um pouco de inflação. 10% de controle tira cerca de ${tenPercent(rule.credit_weight)} do juro.`;
  }
  const subject = lever === "FUEL" ? "a gasolina" : "a conta de luz";
  return `Segurar ${subject} baixa o IPCA: pesa cerca de ${displayPercent(rule.ipca_weight, 0)} do índice. 10% de controle tira cerca de ${tenPercent(rule.ipca_weight)}.`;
}

export const SIZE_LABEL: Record<StateCompanySize, string> = {
  SMALL: "Pequena",
  MEDIUM: "Média",
  LARGE: "Grande",
};

export const sizeLabel = (size: StateCompanySize) => SIZE_LABEL[size].toLowerCase();

const CONTROL_PERCENT: Record<StateControl, number> = { NONE: 0, P5: 5, P10: 10, P15: 15, P20: 20 };

export const controlPercent = (control: StateControl) => CONTROL_PERCENT[control];

/** O degrau como o jogador lê: "Sem controle" ou "10%". */
export const stepLabel = (control: StateControl) =>
  control === "NONE" ? "Sem controle" : `${controlPercent(control)}%`;

/** O controle em vigor na linha: "Sem controle" ou "Segurando 10%". */
export const controlLabel = (control: StateControl) =>
  control === "NONE" ? "Sem controle" : `Segurando ${controlPercent(control)}%`;

export const POLICY_LABEL: Record<DividendPolicy, string> = {
  REINVEST: "Reinvestir",
  NORMAL: "Normal",
  SQUEEZE: "Espremer",
};

/** O que cada política faz com a empresa e a ação. */
export const POLICY_NOTE: Record<DividendPolicy, string> = {
  REINVEST: "A empresa cresce mais: em 4 anos, a ação tende a valer mais",
  NORMAL: "Equilibra o caixa da empresa e o do Tesouro",
  SQUEEZE: "A empresa cresce menos: em 4 anos, a ação tende a valer menos",
};

/** Uma casa decimal quando o número cabe nela (0,5; 1,0) e duas quando não (0,25; 0,75). */
const digitsFor = (points: number) => (Number.isInteger(Math.round(points * 100) / 10) ? 1 : 2);

function pointsNumber(points: number) {
  const digits = digitsFor(points);
  return points.toLocaleString("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

/** Os pontos de IPCA por extenso: "0,5 ponto", "1,5 ponto", "2,0 pontos". */
export const pointsLabel = (points: number | string) => displayPoints(Number(points), digitsFor(Number(points)));

/** O que um degrau do controle faz: o efeito no índice (ou no juro, no banco) e o corte no dividendo. */
export function stepEffect(step: StateOrderPreview["steps"][number], lever: StateLever | null) {
  if (step.control === "NONE") return null;
  const bank = lever === "BANK";
  const points = Number(bank ? step.credit_points : step.held_points);
  return {
    main: `${bank ? "juro" : "IPCA"} ${MINUS}${pointsNumber(points)}`,
    dividend: `div. ${MINUS}${displayPercent(1 - Number(step.dividend_factor), 0)}`,
  };
}

/** O efeito do controle em vigor na linha da tabela; o juro do banco é o que a linha não traz. */
export function rowControlEffect(company: StateCompany) {
  if (company.in_force.control === "NONE") return null;
  if (company.lever === "BANK") return "Juro do crédito menor";
  return `IPCA ${MINUS}${pointsLabel(company.held_points)}`;
}

/** O primeiro nome da empresa: "Luz Nacional" vira "Luz". */
const shortName = (name: string) => name.split(" ")[0] ?? name;

/** Quanto do teto de pontos de IPCA está em uso, de 0 a 1. */
export function capUsage(summary: StateCompaniesPanel["summary"]) {
  const cap = Number(summary.cap_points);
  return cap > 0 ? Math.min(1, Number(summary.held_points) / cap) : 0;
}

/** Os pontos em uso e o teto: "0,7 de 1,5 ponto". */
export const capLabel = (held: string | number, cap: string | number) =>
  `${pointsNumber(Number(held))} de ${pointsLabel(cap)}`;

/** Quanto cada estatal segura do teto: "Petrobras 0,5 · Luz 0,2". */
export function capBreakdown(companies: StateCompany[]) {
  return companies
    .filter((company) => Number(company.held_points) > 0)
    .map((company) => `${shortName(company.name)} ${pointsNumber(Number(company.held_points))}`)
    .join(" · ");
}

/** As estatais que o governo ainda tem: a vendida só aparece nos movimentos. */
export const heldCompanies = (companies: StateCompany[]) =>
  companies.filter((company) => company.status !== "PRIVATIZED");

/** Os nomes em lista corrida: "A", "A e B", "A, B e C". */
function joinNames(names: string[]) {
  if (names.length <= 1) return names.join("");
  return `${names.slice(0, -1).join(", ")} e ${names[names.length - 1]}`;
}

/** O que o governo já tem na alavanca: "Já tem: Petrobras e Luz Nacional", ou a primeira do setor. */
export function leverOwnedNote(companies: StateCompany[], lever: StateLever) {
  const owned = heldCompanies(companies).filter((company) => company.lever === lever);
  if (owned.length === 0) return `Nenhuma estatal de ${STATE_LEVER_LABEL[lever].toLowerCase()} por enquanto`;
  return `Já tem: ${joinNames(owned.map((company) => company.name))}`;
}

/** O que a faixa diz da fatia: "3 empresas: 1 importada e 2 fundadas". */
export function stakeNote(companies: StateCompany[]) {
  const held = heldCompanies(companies);
  const imported = held.filter((company) => company.origin === "IMPORTED").length;
  const founded = held.length - imported;
  const plural = (count: number, one: string, many: string) => `${count} ${count === 1 ? one : many}`;
  return `${plural(held.length, "empresa", "empresas")}: ${plural(imported, "importada", "importadas")} e ${plural(founded, "fundada", "fundadas")}`;
}

/** O valor da empresa inteira, pela fatia do governo; zero depois da venda. */
export function companyValue(company: StateCompany) {
  const share = Number(company.government_share);
  return share > 0 ? Number(company.government_value) / share : 0;
}

/** O que a fatia ganhou ou perdeu desde a fundação, sobre o que o governo pagou; None na importada. */
export function sinceFounding(company: StateCompany) {
  return company.invested === null ? null : Number(company.government_value) / Number(company.invested) - 1;
}

/** O ganho desde a fundação com sinal: "+12,0%" e "−20,0%". */
export const signedSince = (fraction: number) =>
  `${fraction < 0 ? MINUS : "+"}${displayPercent(Math.abs(fraction), 1)}`;

/** O dia da votação da privatização que ainda espera o plenário; None quando não há venda em votação. */
function privatizationVote(company: StateCompany, queue: GovernmentMeasure[]) {
  if (company.privatization_measure_id === null || company.status !== "ACTIVE") return null;
  const measure = queue.find((candidate) => candidate.id === company.privatization_measure_id);
  return measure?.status === "QUEUED" ? measure.vote_date : null;
}

/** "vota em out": o dia da votação da venda, ou None. */
export function votesOnLabel(company: StateCompany, queue: GovernmentMeasure[]) {
  const day = privatizationVote(company, queue);
  return day === null ? null : `vota em ${displayDayMonth(day)}`;
}

/** O estado do Comandar em Suas ações: quem segura o preço, ou None. */
export function commandChip(companies: StateCompany[]) {
  const holding = companies.filter((company) => company.in_force.control !== "NONE" && company.status === "ACTIVE");
  const [first] = holding;
  if (!first) return undefined;
  if (holding.length === 1) return `${shortName(first.name)} ${controlLabel(first.in_force.control).toLowerCase()}`;
  return `${holding.length} estatais segurando o preço`;
}

/** O estado do Privatizar em Suas ações: a estatal com a venda na fila e o dia da votação, ou None. */
export function privatizeChip(companies: StateCompany[], queue: GovernmentMeasure[]) {
  for (const company of companies) {
    const label = votesOnLabel(company, queue);
    if (label) return `${company.ticker} ${label}`;
  }
  return undefined;
}

/** A frase de um movimento recente, pelo ticker. */
export function movementText(movement: StateMovement) {
  const { ticker } = movement;
  switch (movement.kind) {
    case "FOUNDED":
      return `${ticker} fundada pelo governo`;
    case "PRIVATIZATION_OPENED":
      return `Oferta de privatização da ${ticker} aberta à sala`;
    case "PRIVATIZED":
      return `${ticker} privatizada${movement.amount ? ` · ${displayMoneyLarge(movement.amount)} ao Tesouro` : ""}`;
    case "CONTROL_SET":
      return `${ticker} passou a segurar o preço${
        movement.control && movement.control !== "NONE" ? ` em ${controlPercent(movement.control)}%` : ""
      }`;
    case "CONTROL_RELEASED":
      return `${ticker} saiu do controle de preço`;
    case "DIVIDEND_POLICY_SET":
      return `${ticker} passou a pagar dividendos no modo ${
        movement.dividend_policy ? POLICY_LABEL[movement.dividend_policy] : POLICY_LABEL.NORMAL
      }`;
  }
}

/** A diferença entre o preço da oferta e o da bolsa, em fração; None sem um dos dois preços. */
export function offerPremium(offer: StateOffer) {
  if (offer.price === null || offer.market_price === null || Number(offer.market_price) <= 0) return null;
  return Number(offer.price) / Number(offer.market_price) - 1;
}

/** O ágio ou deságio da oferta: "7% acima da bolsa" ou "5% abaixo da bolsa"; None quando empata. */
export function premiumLabel(premium: number) {
  if (Math.abs(premium) < 0.005) return null;
  return `${displayPercent(Math.abs(premium), 0)} ${premium > 0 ? "acima" : "abaixo"} da bolsa`;
}

/** O que a reserva paga no fechamento: ações vezes o preço da oferta. */
export const reservationCost = (offer: StateOffer, quantity: number) => quantity * Number(offer.price ?? 0);

/** A fatia das ações à venda que a sala já pediu, em fração; acima de 1 o rateio é proporcional. */
export const reservedShare = (offer: StateOffer) => (offer.shares > 0 ? Number(offer.reserved) / offer.shares : 0);

/** Os dias que restam à oferta pelo relógio da partida: "faltam 3 dias", "falta 1 dia" ou "último dia". */
export function offerDaysLabel(offer: StateOffer, today: string) {
  const days = daysUntil(today, offer.ends_on);
  if (days === 0) return "último dia";
  return days === 1 ? "falta 1 dia" : `faltam ${days} dias`;
}

/** Reais por ação com centavos; sem preço, o traço. */
export const unitPrice = (price: string | number | null) => (price === null ? "—" : displayMoney(price));
