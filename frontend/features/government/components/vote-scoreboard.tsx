import { MetricLabel } from "@/shared/components/metric-hint";
import { cn } from "@/shared/lib/utils";
import { FORECAST } from "../lib/government-metrics";
import { outlook, rangeLabel, SEAT_TOTAL, seatShare, type Vote } from "../lib/house";

const TONE = { passes: "text-success", falls: "text-destructive", open: "text-warning" } as const;

/** O placar da votação: os votos Sim numa barra de 0 a 101, com a marca dos votos necessários para passar. */
export function VoteScoreboard({ vote }: { vote: Vote }) {
  const voted = vote.yes !== null;
  // Aberta: o Sim garantido (low) é a parte escura e a faixa até high é a clara; votada, o Sim é o que foi contado
  const solid = voted ? vote.yes : vote.low;
  const upTo = voted ? vote.yes : vote.high;
  const value = voted ? `${vote.yes}` : rangeLabel(vote.low, vote.high);

  return (
    <div className="grid gap-2 rounded-[10px] border p-3.5">
      <div className="flex items-baseline justify-between gap-3">
        {voted ? (
          <span className="text-xs font-medium text-muted-foreground">Placar</span>
        ) : (
          <MetricLabel metric={FORECAST} />
        )}
        <span className="text-[13px] text-muted-foreground">
          Sim · {vote.needed} votos Sim para passar{" "}
          <b className={cn("font-mono text-[22px]", voted ? "text-foreground" : TONE[outlook(vote)])}>{value}</b>
        </span>
      </div>
      <div
        role="img"
        aria-label={`Placar: ${value} votos Sim de ${SEAT_TOTAL}, ${vote.needed} para passar`}
        className="relative h-2.5 rounded-full bg-muted"
      >
        {upTo !== null && (
          <span
            className="absolute inset-y-0 left-0 rounded-full bg-foreground opacity-28"
            style={{ width: `${seatShare(upTo)}%` }}
          />
        )}
        {solid !== null && (
          <span
            className="absolute inset-y-0 left-0 rounded-full bg-foreground"
            style={{ width: `${seatShare(solid)}%` }}
          />
        )}
        <span
          className="absolute -top-1.25 h-5 w-0.5 rounded-[1px] bg-destructive"
          style={{ left: `${seatShare(vote.needed)}%` }}
        />
      </div>
      <div className="relative h-4 font-mono text-xs text-faint-foreground">
        <span className="absolute left-0">0</span>
        <span className="absolute -translate-x-1/2" style={{ left: `${seatShare(vote.needed)}%` }}>
          {vote.needed}
        </span>
        <span className="absolute right-0">{SEAT_TOTAL}</span>
      </div>
    </div>
  );
}
