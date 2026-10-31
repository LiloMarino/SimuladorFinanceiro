import type { GovernmentPanel } from "@/types";
import { partyColor } from "@/shared/lib/party-colors";
import { GROUP_INFO } from "./voters";

type Congress = GovernmentPanel["congress"];
export type House = Congress["house"];
export type Bloc = House["blocs"][number];
export type Vote = NonNullable<GovernmentPanel["queue"][number]["vote"]>;
export type BlocVote = Vote["blocs"][number];

/** Uma cadeira do hemiciclo: a cor (do partido; nula é a cor do texto), o tom e o anel de quem pode desobedecer. */
export type HemicycleSeat = {
  color: string | null;
  tone: "solid" | "light" | "empty";
  ring?: boolean;
  /** A bancada da cadeira, quando o hemiciclo deixa escolhê-la, e o texto de quem passa o mouse */
  blocKey?: number;
  title?: string;
};

/** "Sim" ou "Não" */
export const orientationLabel = (yes: boolean) => (yes ? "Sim" : "Não");

/** O placar previsto em faixa: "53 a 60", ou "55" quando a faixa fecha em um número. */
export function rangeLabel(low: number | null, high: number | null): string {
  if (low === null || high === null) return "—";
  return low === high ? `${low}` : `${low} a ${high}`;
}

/** Onde a faixa prevista cai em relação ao mínimo para passar. */
export function outlook(vote: Pick<Vote, "low" | "high" | "needed">): "passes" | "falls" | "open" {
  if (vote.low === null || vote.high === null) return "open";
  if (vote.low >= vote.needed) return "passes";
  return vote.high < vote.needed ? "falls" : "open";
}

/** "Passa com 53 a 60", "Cai com 40 a 46", "Decidida por quem desobedecer: 48 a 55" */
export function outlookLabel(vote: Pick<Vote, "low" | "high" | "needed">): string {
  const range = rangeLabel(vote.low, vote.high);
  switch (outlook(vote)) {
    case "passes":
      return `Passa com ${range}`;
    case "falls":
      return `Cai com ${range}`;
    default:
      return `Aberta: ${range}`;
  }
}

/** O resultado de uma votação feita: "Aprovada por 54 a 47". */
export function resultLabel(vote: Pick<Vote, "yes" | "no">, approved: boolean): string {
  return `${approved ? "Aprovada" : "Rejeitada"} por ${approved ? vote.yes : vote.no} a ${approved ? vote.no : vote.yes}`;
}

/** Por que a bancada pode desobedecer: "aposentados, 18% dos eleitores do FDS, perdem com a medida". */
export function causeLabel(bloc: Pick<BlocVote, "abbr" | "cause" | "cause_share" | "orientation">, subject: string) {
  if (!bloc.cause || bloc.cause_share === null) return null;
  const group = GROUP_INFO[bloc.cause].short.toLowerCase();
  const share = Math.round(Number(bloc.cause_share) * 100);
  return `${group}, ${share}% dos eleitores do ${bloc.abbr}, ${bloc.orientation ? "rejeitam" : "querem"} ${subject}`;
}

/** Quanto cada bancada pesa no total de cadeiras que ela tem hoje, em ordem de tamanho. */
export function bySeats(blocs: Bloc[]): Bloc[] {
  return blocs.filter((bloc) => bloc.seats > 0).sort((a, b) => b.seats - a.seats || a.key - b.key);
}

/** A mudança de cadeiras desde a casa anterior: "+6", "-3" ou "0". */
export function seatChange(bloc: Pick<Bloc, "seats" | "previous_seats">): string | null {
  if (bloc.previous_seats === null) return null;
  const change = bloc.seats - bloc.previous_seats;
  return change > 0 ? `+${change}` : `${change}`;
}

const SEAT_TOTAL = 101;

/** O hemiciclo por partido: cada bancada ocupa uma cunha, em ordem de tamanho. */
export function partySeats(blocs: Bloc[]): HemicycleSeat[] {
  const seats = bySeats(blocs).flatMap((bloc) =>
    Array.from({ length: bloc.seats }, (): HemicycleSeat => ({ color: partyColor(bloc), tone: "solid" })),
  );
  return pad(seats);
}

/**
 * O hemiciclo de uma votação. Antes de votar: cheia a bancada orientada a Sim, clara a que vota Não, com anel nos que
 * podem desobedecer. Depois: cheio quem votou Sim, claro quem votou Não, com anel em quem votou contra o líder.
 */
export function voteSeats(vote: Vote): HemicycleSeat[] {
  const seats = [...vote.blocs]
    .sort((a, b) => b.seats - a.seats || a.key - b.key)
    .flatMap((bloc) => {
      const voted = bloc.yes !== null && bloc.defected !== null;
      const yes = voted ? bloc.yes! : bloc.orientation ? bloc.seats : 0;
      const rebels = voted ? bloc.defected! : bloc.may_defect;
      return Array.from({ length: bloc.seats }, (_, index): HemicycleSeat => ({
        color: null,
        tone: index < yes ? "solid" : "light",
        // Quem vota contra: os últimos da bancada orientada a Sim, os primeiros da orientada a Não
        ring: bloc.orientation ? index >= bloc.seats - rebels : index < rebels,
      }));
    });
  return pad(seats);
}

export function pad(seats: HemicycleSeat[]): HemicycleSeat[] {
  const missing = Math.max(0, SEAT_TOTAL - seats.length);
  return [...seats, ...Array.from({ length: missing }, (): HemicycleSeat => ({ color: null, tone: "empty" }))];
}

/** Votações em que o líder de quem vê ainda não orientou: o selo da aba Congresso. */
export function unguidedCount(congress: GovernmentPanel["congress"], queue: GovernmentPanel["queue"]): number {
  const votes = [...queue.map((measure) => measure.vote), congress.impeachment_request?.vote ?? null];
  return votes.filter((vote) => {
    const mine = vote?.guide ? vote.blocs.find((bloc) => bloc.key === vote.guide?.bloc_key) : undefined;
    return mine !== undefined && !mine.guided;
  }).length;
}

/** "75% de 8 votações"; sem votação ainda, "—". */
export function shareOfVotes(share: string | number | null, votes: number): string {
  return share === null || votes === 0 ? "—" : `${Math.round(Number(share))}% de ${votes}`;
}
