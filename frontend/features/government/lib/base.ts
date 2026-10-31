import type { BaseBloc, BaseDeal, CongressBase, VoterGroup } from "@/types";
import { displayDayMonth, displayMoneyLarge } from "@/shared/lib/utils/display";
import { pad, type HemicycleSeat } from "./house";
import { GROUP_INFO } from "./voters";
import { partyColor } from "@/shared/lib/party-colors";

/** Reais por mês na escala do orçamento: "R$ 2,54 bi". */
export const monthlyLabel = (amount: string | number) => displayMoneyLarge(amount);

/** A emenda em % do PIB por ano: "0,11%". */
export function yearShare(ratio: string | number): string {
  return `${(Number(ratio) * 100).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 3 })}%`;
}

/** "Aposentados e servidores": os grupos mais fortes de um partido, por extenso. */
export function groupsLabel(groups: VoterGroup[]): string {
  const names = groups.map((group, index) => {
    const label = GROUP_INFO[group].label;
    return index === 0 ? label : label.toLowerCase();
  });
  return names.join(" e ");
}

/** "6 de folga sobre a maioria" ou "faltam 18 cadeiras para a maioria". */
export function majorityMargin(seats: number, majority: number): { text: string; enough: boolean } {
  const margin = seats - majority;
  if (margin >= 0) return { text: `${margin} de folga sobre a maioria`, enough: true };
  return { text: `faltam ${-margin} ${-margin === 1 ? "cadeira" : "cadeiras"} para a maioria`, enough: false };
}

/** "faltam 77 dias" ou, com mais de dois meses, "faltam 5 meses". */
export function daysLeftLabel(days: number): string {
  if (days >= 60) return `faltam ${Math.round(days / 30)} meses`;
  return days === 1 ? "falta 1 dia" : `faltam ${days} dias`;
}

/** A situação do acordo na tabela da base: "aguardando Lilo · até 29 mar" ou "até 14 set". */
export function pendingLabel(deal: BaseDeal): string {
  const who = deal.leader ?? deal.abbr;
  if (deal.answer_by === null) return `${deal.abbr} responde no próximo pregão`;
  return `aguardando ${who} · até ${displayDayMonth(deal.answer_by)}`;
}

/** Os acordos em vigor, na ordem em que foram propostos. */
export const dealsInForce = (base: CongressBase): BaseDeal[] => base.deals.filter((deal) => deal.status === "ACTIVE");

/** As propostas que esperam resposta. */
export const dealsPending = (base: CongressBase): BaseDeal[] => base.deals.filter((deal) => deal.status === "PENDING");

/** A bancada tem texto de situação: quem governa, quem está na base, quem espera resposta ou quem está fora. */
export function blocStatus(bloc: BaseBloc): "governing" | "in_base" | "pending" | "outside" {
  if (bloc.governing) return "governing";
  if (bloc.in_base) return "in_base";
  return bloc.pending ? "pending" : "outside";
}

const STATUS_TEXT: Record<ReturnType<typeof blocStatus>, string> = {
  governing: "governo",
  in_base: "na base",
  pending: "esperando resposta",
  outside: "fora da base",
};

/** O texto de quem passa o mouse na cadeira: "MRC · 16 cadeiras · Rafa · fora da base". */
function blocTitle(bloc: BaseBloc): string {
  const who = bloc.leader ?? (bloc.is_computer ? "computador" : null);
  return [`${bloc.abbr} · ${bloc.seats} cadeiras`, who, STATUS_TEXT[blocStatus(bloc)]].filter(Boolean).join(" · ");
}

/**
 * O hemiciclo da base: cheia a bancada do governo e as aliadas, clara a de fora. A bancada escolhida para a
 * proposta entra cheia e com anel.
 */
export function baseSeats(blocs: BaseBloc[], selectedKey?: number | null): HemicycleSeat[] {
  const seats = [...blocs]
    .sort((a, b) => b.seats - a.seats || a.key - b.key)
    .flatMap((bloc) => {
      const inside = bloc.governing || bloc.in_base;
      const selected = bloc.key === selectedKey;
      return Array.from({ length: bloc.seats }, (): HemicycleSeat => ({
        color: partyColor(bloc),
        tone: inside || selected ? "solid" : "light",
        ring: selected,
        blocKey: bloc.key,
        title: blocTitle(bloc),
      }));
    });
  return pad(seats);
}

/** Quem está fora da base e tem líder jogador, para a linha "Fora da base: PRL (Lilo, 28)". */
export function outsideLabel(blocs: BaseBloc[]): string {
  return blocs
    .filter((bloc) => !bloc.governing && !bloc.in_base)
    .map((bloc) => `${bloc.abbr} (${bloc.leader ? `${bloc.leader}, ` : ""}${bloc.seats})`)
    .join(" e ");
}

/** O recado de quando a base passa dos dois terços ou da maioria depois da proposta. */
export function baseOutlook(after: number, majority: number, impeachmentVotes: number): string {
  if (after >= impeachmentVotes) return `passa dos dois terços (${impeachmentVotes})`;
  if (after >= majority) return `passa da maioria (${majority})`;
  return `segue abaixo da maioria (${majority})`;
}
