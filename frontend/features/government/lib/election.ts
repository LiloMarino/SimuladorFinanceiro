import { addMonths, differenceInCalendarDays, differenceInCalendarMonths } from "date-fns";
import { displayMonthShort, displayShortDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionPhase } from "@/types";

/** Os diálogos da página da eleição que um atalho de fora (as pendências, o diálogo da campanha) abre ao chegar. */
export type ElectionShortcut = "found" | "join" | "contribution" | "vice" | "campaign" | "federation-answer";

/** "out 2020": o mês e o ano de uma data. */
export function monthYear(isoDate: string) {
  return `${displayMonthShort(isoDate)} ${isoDate.slice(0, 4)}`;
}

/** O prazo de filiação de quem quer concorrer nesta eleição; depois dele, a filiação vale para a seguinte. */
export function affiliationNote(panel: ElectionPanel) {
  const { affiliation_deadline: deadline, first_round: firstRound } = panel.dates;
  return panel.today <= deadline
    ? `Para concorrer em ${monthYear(firstRound)}, filie-se até ${displayShortDate(deadline)}.`
    : `Quem se filia agora concorre na eleição seguinte: o prazo para ${monthYear(firstRound)} fechou em ${displayShortDate(deadline)}.`;
}

/** A contribuição se cobra só com a campanha aberta; antes dela, a frase diz quando começa. */
export function collectionNote(panel: ElectionPanel) {
  return panel.phase === "BEFORE_CAMPAIGN"
    ? ` A cobrança começa com a campanha, que abre em ${displayShortDate(panel.dates.campaign_start)}.`
    : "";
}

/** Quantas vezes a raiz do gasto mensal divide em pontos de intenção (a cada 100 eleitores). */
const VOTE_DIVISOR = 64;

/** Pontos de intenção que uma verba mensal rende por mês: raiz do gasto dividida por 64. */
export function monthlyYield(monthlySpend: number) {
  return Math.sqrt(Math.max(monthlySpend, 0)) / VOTE_DIVISOR;
}

/** "6 meses e 23 dias": o tempo de `from` até `to`, em meses cheios e dias. */
export function countdownLabel(from: string, to: string) {
  const start = parseLocalDate(from);
  const end = parseLocalDate(to);
  if (end <= start) return "hoje";
  let months = differenceInCalendarMonths(end, start);
  if (addMonths(start, months) > end) months -= 1;
  const days = differenceInCalendarDays(end, addMonths(start, months));
  const parts = [];
  if (months > 0) parts.push(`${months} ${months === 1 ? "mês" : "meses"}`);
  if (days > 0) parts.push(`${days} ${days === 1 ? "dia" : "dias"}`);
  return parts.join(" e ");
}

/** Quantos dias 1º ainda cobram a verba até o 1º turno: o primeiro dia de cada mês depois de hoje. */
export function remainingCollections(today: string, firstRound: string) {
  const start = parseLocalDate(today);
  const end = parseLocalDate(firstRound);
  let count = 0;
  for (let day = new Date(start.getFullYear(), start.getMonth() + 1, 1); day <= end; day = addMonths(day, 1)) {
    count += 1;
  }
  return count;
}

/** A campanha acaba com a apuração do último turno: da espera pela posse em diante, não há mais pesquisa. */
export function campaignEnded(phase: ElectionPhase) {
  return phase === "AWAITING_TERM" || phase === "TERM";
}

/** O selo da fase no topo da página. */
export function phaseLabel(phase: ElectionPhase) {
  switch (phase) {
    case "BEFORE_CAMPAIGN":
      return "Campanha ainda fechada";
    case "CAMPAIGN":
      return "Campanha aberta";
    case "BETWEEN_ROUNDS":
      return "Entre os turnos";
    case "AWAITING_TERM":
      return "Aguardando a posse";
    case "TERM":
      return "Mandato em curso";
  }
}
