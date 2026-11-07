import type { ChallengeDirection, ChallengeMark } from "@/types";

const MONTHS = [
  "janeiro",
  "fevereiro",
  "março",
  "abril",
  "maio",
  "junho",
  "julho",
  "agosto",
  "setembro",
  "outubro",
  "novembro",
  "dezembro",
];

function monthYear(isoDay: string) {
  const [year = "", month = "1"] = isoDay.split("-");
  return { year, month: MONTHS[Number(month) - 1] ?? "" };
}

/** "março de 2015", "fevereiro a março de 2015" ou "dezembro de 2014 a janeiro de 2015". */
export function displayPeriod(start: string, end: string) {
  const from = monthYear(start);
  const to = monthYear(end);
  if (from.year === to.year && from.month === to.month) return `${to.month} de ${to.year}`;
  if (from.year === to.year) return `${from.month} a ${to.month} de ${to.year}`;
  return `${from.month} de ${from.year} a ${to.month} de ${to.year}`;
}

export const sideVerb = (direction: ChallengeDirection) => (direction === "up" ? "sobe" : "desce");

export function ordinal(position: number) {
  return `${position}º`;
}

/** A frase que diz o que o jogador respondeu e como foi. */
export function verdictText(direction: ChallengeDirection | undefined, mark: ChallengeMark | null) {
  if (!direction) return "Você não respondeu a tempo.";
  return `Você disse que ${sideVerb(direction)}: ${mark === "hit" ? "acertou" : "errou"}.`;
}

export function pointsText(hits: number) {
  return `${hits} ${hits === 1 ? "acerto" : "acertos"}`;
}

export type FinalBand = { title: string; celebrate: boolean };

/** O recado do fim da rodada solo pela faixa de acertos: 0 a 3, 4 a 7 e 8 ou mais; só a última comemora. */
export function finalBand(hits: number): FinalBand {
  if (hits <= 3) return { title: "Gráfico é traiçoeiro: veja as respostas", celebrate: false };
  if (hits <= 7) return { title: "Na média", celebrate: false };
  return { title: "Leitura afiada", celebrate: true };
}
