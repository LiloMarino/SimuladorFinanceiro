import { StackedBar } from "@/shared/components/stacked-bar";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import type { ElectionParty, ElectionPoll } from "@/types";
import { marginRange, partyFill, pollPercent, pollPoints } from "../lib/voters";

type GroupPoll = ElectionPoll["groups"][number];

type GroupPollBarProps = {
  poll: GroupPoll;
  /** Os partidos na ordem da página: a mesma em todas as barras */
  parties: ElectionParty[];
  /** "Aposentados · 20% do eleitorado", o título da dica */
  title: string;
  className?: string;
};

/** A pesquisa num grupo como barra empilhada; a dica traz o número e a faixa de cada partido. */
export function GroupPollBar({ poll, parties, title, className }: GroupPollBarProps) {
  const points = pollPoints(poll.entries);
  const undecided = Number(poll.undecided);
  const segments = [
    ...parties.map((party) => ({
      key: String(party.id),
      fraction: (points.get(party.id) ?? 0) / 100,
      fill: partyFill(party),
    })),
    { key: "undecided", fraction: undecided / 100, color: "bg-faint-foreground/40" },
  ];

  return (
    <Tooltip>
      <TooltipTrigger render={<div className={className} />}>
        <StackedBar segments={segments} />
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-80">
        <div className="grid gap-0.5 text-left">
          <b>{title}</b>
          {parties.map((party) => {
            const value = points.get(party.id) ?? 0;
            const [low, high] = marginRange(value, poll.margin);
            return (
              <span key={party.id}>
                {party.abbr} {pollPercent(value, poll.margin)}
                {poll.margin > 0 && (
                  <span className="opacity-70">
                    {" "}
                    ({pollPercent(low, poll.margin)} a {pollPercent(high, poll.margin)})
                  </span>
                )}
              </span>
            );
          })}
          <span>Indecisos {pollPercent(undecided, poll.margin)}</span>
          {poll.margin > 0 && (
            <span className="mt-1 opacity-70">
              Margem de {poll.margin} pontos: quanto menor o grupo, menor a amostra e maior a margem.
            </span>
          )}
        </div>
      </TooltipContent>
    </Tooltip>
  );
}
