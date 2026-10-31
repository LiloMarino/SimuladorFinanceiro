import { Repeat } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { StackedBar } from "@/shared/components/stacked-bar";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { displayNumber, displayPercent, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionRound } from "@/types";
import { NOT_VOTED } from "../lib/election-metrics";
import { RUNOFF_MAJORITY, firstRoundBefore, turnaroundGap } from "../lib/runoff";
import { PartyMark, PersonMark } from "./party-mark";
import { partyColor } from "@/shared/lib/party-colors";

type RunoffResultProps = {
  result: ElectionRound;
  /** Todos os turnos apurados: o 1º turno de onde o 2º partiu mostra se houve virada */
  results: ElectionRound[];
};

/** O 2º turno: a votação dos finalistas com a linha dos 50%, o eleitorado todo com quem não votou e a virada, se houve. */
export function RunoffResult({ result, results }: RunoffResultProps) {
  const finalists = result.parties
    .filter((party) => result.finalists.includes(party.party_id))
    .sort((a, b) => Number(b.share) - Number(a.share) || a.party_id - b.party_id);
  const notVoted = Number(result.not_voted);
  const winner = finalists.find((party) => party.party_id === result.winner);
  const valid = finalists.reduce((sum, party) => sum + Number(party.points), 0);
  const gap = turnaroundGap(firstRoundBefore(results, result), result);

  return (
    <div className="grid gap-3.5">
      {/* Votos válidos dos finalistas */}
      <div className="grid gap-3">
        {finalists.map((party) => (
          <div key={party.party_id} className="grid gap-1.5">
            <div className="flex items-center justify-between gap-3 text-[13px]">
              <span className="flex min-w-0 items-center gap-2">
                <PartyMark abbr={party.abbr} color={party.color} size="sm" />
                {party.candidate && <PersonMark person={party.candidate} />}
                <span className="truncate">{party.candidate?.name ?? party.name}</span>
                {party.party_id === result.winner && (
                  <Badge variant="success" size="sm">
                    Eleito
                  </Badge>
                )}
              </span>
              <span className="font-mono text-[15px] font-semibold">{displayPercent(party.share, 1)}</span>
            </div>
            <span className="relative h-2.5 rounded-xs bg-muted">
              <span
                className="absolute inset-y-0 left-0 rounded-xs"
                style={{ width: `${Number(party.share) * 100}%`, backgroundColor: partyColor(party) }}
              />
              <span
                aria-hidden
                className="absolute -inset-y-1 w-px bg-foreground/60"
                style={{ left: `${RUNOFF_MAJORITY}%` }}
              />
            </span>
          </div>
        ))}
        <span className="text-right text-[11px] text-faint-foreground">linha: 50% dos votos válidos</span>
      </div>

      {/* Eleitorado todo */}
      <div className="grid gap-1.5">
        <span className="inline-flex items-center gap-1 text-xs font-medium">
          Do eleitorado todo
          <MetricHint metric={NOT_VOTED} />
        </span>
        <StackedBar
          segments={[
            ...finalists.map((party) => ({
              key: String(party.party_id),
              fraction: Number(party.points) / 100,
              fill: partyColor(party),
            })),
            { key: "not-voted", fraction: notVoted / 100, color: "bg-faint-foreground/40" },
          ]}
        />
        <span className="font-mono text-xs text-muted-foreground">
          {finalists.map((party) => `${party.abbr} ${displayNumber(party.points, 1)}`).join(" · ")} · não votaram{" "}
          {displayNumber(notVoted, 1)}
        </span>
        {winner && (
          <span className="text-xs text-muted-foreground">
            Os {displayNumber(notVoted, 1)}% que continuavam indecisos em {displayShortDate(result.date)} não votaram. O
            vencedor sai só dos votos válidos: {displayNumber(winner.points, 1)} de {displayNumber(valid, 1)}, ou{" "}
            {displayPercent(winner.share, 1)}.
          </span>
        )}
      </div>

      {winner && gap !== null && (
        <Alert variant="info">
          <Repeat />
          <AlertTitle>Virada</AlertTitle>
          <AlertDescription>
            O {winner.abbr} terminou o 1º turno {displayNumber(gap, 1)} pontos atrás e venceu o 2º.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
