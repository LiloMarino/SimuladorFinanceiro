import { addDays, differenceInCalendarDays, format } from "date-fns";
import { displayDayMonth, displayMoneyCompact, displayMonthShort, parseLocalDate } from "@/shared/lib/utils/display";
import type {
  GovernmentApproval,
  GovernmentMeasure,
  GovernmentPanel,
  MeasureKind,
  MeasurePreview,
  MeasureStatus,
} from "@/types";

const MINUS = "−";
const PERCENT = new Intl.NumberFormat("pt-BR", { style: "percent", maximumFractionDigits: 1 });

export type GeneralKind = Exclude<MeasureKind, "SECTOR_EXEMPT" | "SECTOR_TAX">;

export const GENERAL_KINDS = [
  "STOCK_PROFIT_RATE",
  "DAY_TRADE_RATE",
  "STOCK_EXEMPTION",
  "FIXED_INCOME_TABLE",
  "LCI_LCA_RATE",
] as const satisfies readonly GeneralKind[];

export const isGeneral = (kind: MeasureKind): kind is GeneralKind => GENERAL_KINDS.includes(kind as GeneralKind);

/** Alíquota como o jogo escreve: 0.225 → "22,5%" e 0.15 → "15%". */
export function percentLabel(fraction: string | number) {
  return PERCENT.format(Number(fraction));
}

/** Pontos com sinal e o menos tipográfico: 4 → "+4", -1 → "−1". */
export function signedPoints(points: number) {
  if (points === 0) return "0";
  return `${points > 0 ? "+" : MINUS}${Math.abs(points)}`;
}

/** Tom do número que muda a aprovação: positivo soma, negativo tira. */
export function pointsTone(points: number) {
  if (points > 0) return "text-success";
  if (points < 0) return "text-destructive";
  return "";
}

/** "Isenção até R$ 20 mil/mês": o teto mensal das vendas de ações sem IR. */
function exemptionLabel(limit: string | number) {
  return `até ${displayMoneyCompact(limit)}/mês`;
}

export function generalLabel(kind: GeneralKind, value: string) {
  switch (kind) {
    case "STOCK_PROFIT_RATE":
      return "Ações · vendas com lucro";
    case "DAY_TRADE_RATE":
      return "Ações · day trade";
    case "STOCK_EXEMPTION":
      return `Isenção de vendas ${exemptionLabel(value)}`;
    case "FIXED_INCOME_TABLE":
      return "Renda fixa · tabela regressiva";
    case "LCI_LCA_RATE":
      return "LCI e LCA";
  }
}

/** O valor em vigor de um imposto geral: a alíquota, o teto da isenção ou a faixa da tabela. */
export function generalToday(kind: GeneralKind, value: string, top: string | null) {
  switch (kind) {
    case "STOCK_EXEMPTION":
      return Number(value) > 0 ? "Vale" : "Não vale";
    case "FIXED_INCOME_TABLE":
      return top !== null && Number(top) !== Number(value)
        ? `${percentLabel(top)} → ${percentLabel(value)}`
        : percentLabel(value);
    case "LCI_LCA_RATE":
      return Number(value) === 0 ? "Isentas" : percentLabel(value);
    default:
      return percentLabel(value);
  }
}

/** Dias que faltam até a medida valer; nunca negativo. */
export function daysUntil(today: string, day: string) {
  return Math.max(0, differenceInCalendarDays(parseLocalDate(day), parseLocalDate(today)));
}

/** O dia em que uma medida votada em `vote` passa a valer, depois da espera. */
export function effectiveDate(vote: string, vigenceDays: number) {
  return format(addDays(parseLocalDate(vote), vigenceDays), "yyyy-MM-dd");
}

/** "nov 2019": o mês de uma data, para "desde nov 2019". */
export function monthYear(day: string) {
  return `${displayMonthShort(day)} ${parseLocalDate(day).getFullYear()}`;
}

export const STAGES: Record<
  MeasureStatus,
  { label: string; variant: "warning" | "info" | "destructive" | "secondary" }
> = {
  QUEUED: { label: "Na fila", variant: "warning" },
  APPROVED: { label: "Aprovada", variant: "info" },
  REJECTED: { label: "Rejeitada", variant: "destructive" },
  WITHDRAWN: { label: "Retirada", variant: "secondary" },
  DROPPED: { label: "Descartada", variant: "secondary" },
};

/** A coluna "Próximo passo" da fila, conforme a etapa da medida. */
export function nextStep(measure: GovernmentMeasure, today: string) {
  switch (measure.status) {
    case "QUEUED":
      return measure.vote_date ? `Congresso vota em ${displayDayMonth(measure.vote_date)}` : "Aguarda a votação";
    case "APPROVED":
      return measure.effective
        ? `Vale em ${displayDayMonth(measure.effective)} · faltam ${daysUntil(today, measure.effective)} dias`
        : "Vale após a espera";
    case "REJECTED":
      return measure.chance !== null ? `Tinha ${measure.chance}% de chance` : "Rejeitada pelo Congresso";
    default:
      return "";
  }
}

/** A frase da linha de uma medida de setor: a alíquota nova e quando vale. */
export function sectorEffect(measure: GovernmentMeasure, baseRate: string, today: string) {
  if (measure.kind === "SECTOR_EXEMPT") return "IR 0% (isento)";
  const raised = Number(baseRate) + Number(measure.value ?? 0);
  const waiting = measure.effective !== null && measure.effective > today;
  if (waiting && measure.effective) {
    return `${percentLabel(baseRate)} → ${percentLabel(raised)} em ${displayDayMonth(measure.effective)}`;
  }
  return `IR ${percentLabel(raised)}`;
}

/** O setor ou o segmento que a medida atinge. */
export const measureTarget = (measure: GovernmentMeasure) => measure.segment ?? measure.sector ?? "";

/** Tom da aprovação: abaixo do piso é crítica, abaixo de 50 pede atenção. */
export function approvalTone(approval: Pick<GovernmentApproval, "value" | "floor">) {
  if (approval.value < approval.floor) return "destructive";
  if (approval.value < 50) return "warning";
  return "success";
}

/** Seta da variação da aprovação desde o mês anterior. */
export function approvalArrow(approval: Pick<GovernmentApproval, "value" | "previous">) {
  if (approval.previous === null || approval.previous === approval.value) return "";
  return approval.value > approval.previous ? "▲" : "▼";
}

/** Meses abaixo do piso, no plural certo: "2 meses seguidos abaixo de 25%". */
export function lowStreakLabel(approval: Pick<GovernmentApproval, "low_streak" | "floor">) {
  const months = approval.low_streak;
  return months === 1 ? `1 mês abaixo de ${approval.floor}%` : `${months} meses seguidos abaixo de ${approval.floor}%`;
}

/** Quem assume se o impeachment vier: o vice, ou um governo neutro do computador. */
export function successionLabel(panel: Pick<GovernmentPanel, "term">) {
  const vice = panel.term?.vice;
  return vice ? `${vice.name} assume` : "o governo passa a um computador neutro";
}

/** A carteira como fração do total: 0.34 → "34%". */
export function shareLabel(share: string | number) {
  return `${Math.round(Number(share) * 100)}%`;
}

/** Quem tem os ativos da medida: o próprio jogador em %, os outros em reais. */
export function holdingLabel(holding: { nickname: string; share: string; value: string }, me: string | undefined) {
  return holding.nickname === me
    ? `você ${shareLabel(holding.share)}`
    : `${holding.nickname} ${displayMoneyCompact(holding.value)}`;
}

/** O valor que o jogador digitou em %, como a fração que a API recebe: "22,5" → "0.225". */
export function rateToFraction(text: string) {
  const value = Number(text.replace(",", "."));
  return Number.isFinite(value) && text.trim() !== "" ? String(Math.round(value * 100) / 10000) : null;
}

/** O que a medida rascunhada faz na aprovação, em uma frase. */
export function impactSentence(preview: Pick<MeasurePreview, "impact">) {
  const points = Math.abs(preview.impact);
  const unit = points === 1 ? "ponto" : "pontos";
  if (preview.impact > 0) {
    return `Como corte de imposto, soma ${points} ${unit} à aprovação quando passa a valer.`;
  }
  return `Como imposto novo, tira ${points} ${unit} da aprovação quando passa a valer, efeito que some em 6 meses.`;
}
