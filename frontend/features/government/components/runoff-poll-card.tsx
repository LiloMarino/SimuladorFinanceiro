import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayDayMonth, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty, ElectionPoll, RunoffRace } from "@/types";
import { RUNOFF, UNDECIDED } from "../lib/election-metrics";
import { inTechnicalTie, marginRange, pollPercent, pollPoints } from "../lib/voters";
import { GroupPollRows } from "./group-poll-rows";
import { PartyMark, PersonMark } from "@/shared/components/party-mark";
import { PollLegend } from "./poll-legend";
import { partyColor } from "@/shared/lib/party-colors";

const ROW = "grid grid-cols-[minmax(0,220px)_90px_1fr_auto] items-center gap-3";

type RunoffPollCardProps = { panel: ElectionPanel; race: RunoffRace };

/** A pesquisa semanal do 2º turno, no total e por grupo de eleitores. */
export function RunoffPollCard({ panel, race }: RunoffPollCardProps) {
  const finalists = race.finalists
    .map((id) => panel.parties.find((party) => party.id === id))
    .filter((party): party is ElectionParty => party !== undefined);
  const latest = race.polls.at(-1);

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4.5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="grid gap-0.5">
              <h2 className="text-[15px] font-semibold">
                <MetricLabel metric={RUNOFF} />
              </h2>
              <span className="text-[13px] text-muted-foreground">
                Semanal entre os turnos e pública: todos na sala veem a mesma.
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {latest && <Badge variant="secondary">Atualizada em {displayShortDate(latest.date)}</Badge>}
              {race.next_poll && <Badge variant="secondary">Próxima em {displayDayMonth(race.next_poll)}</Badge>}
              {latest && latest.margin > 0 && <Badge variant="info">Margem de {latest.margin} pontos no total</Badge>}
            </div>
          </div>

          {latest ? (
            <RunoffPollBody panel={panel} poll={latest} finalists={finalists} />
          ) : (
            <div className="grid justify-items-center gap-1 rounded-lg border border-dashed px-6 py-8 text-center">
              <b className="text-[15px] font-semibold">
                A primeira pesquisa sai {race.next_poll ? `em ${displayDayMonth(race.next_poll)}` : "em breve"}
              </b>
              <span className="max-w-md text-[13px] text-muted-foreground">
                Até lá, os votos de quem saiu já estão divididos entre os finalistas, como mostra a tabela abaixo.
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

type RunoffPollBodyProps = { panel: ElectionPanel; poll: ElectionPoll; finalists: ElectionParty[] };

function RunoffPollBody({ panel, poll, finalists }: RunoffPollBodyProps) {
  const points = pollPoints(poll.entries);
  const margin = poll.margin;

  return (
    <>
      <PollLegend parties={finalists} />

      {/* Se o 2º turno fosse hoje */}
      <div className="grid gap-3">
        <span className="text-xs font-medium">Se o 2º turno fosse hoje</span>
        {finalists.map((party) => {
          const own = points.get(party.id) ?? 0;
          const others = finalists.filter((other) => other.id !== party.id).map((other) => points.get(other.id) ?? 0);
          const [low, high] = marginRange(own, margin);
          return (
            <div key={party.id} className={ROW}>
              <span className="flex min-w-0 items-center gap-2">
                <PartyMark abbr={party.abbr} color={party.color} size="sm" />
                {party.candidate && <PersonMark person={party.candidate} />}
                <span className="truncate text-[13px]">{party.candidate?.name ?? party.name}</span>
              </span>
              <span className="font-mono text-[15px] font-semibold whitespace-nowrap">
                {pollPercent(own, margin)}
                {margin > 0 && <span className="font-normal text-faint-foreground"> ±{margin}</span>}
              </span>
              <span className="relative h-2.5 rounded-xs bg-muted">
                {margin > 0 && (
                  <span
                    className="absolute inset-y-0 rounded-xs opacity-25"
                    style={{ left: `${low}%`, width: `${high - low}%`, backgroundColor: partyColor(party) }}
                  />
                )}
                <span
                  className="absolute inset-y-0 left-0 rounded-xs opacity-85"
                  style={{ width: `${own}%`, backgroundColor: partyColor(party) }}
                />
              </span>
              {inTechnicalTie(own, others, margin) ? (
                <Badge variant="warning" size="sm">
                  Empate técnico
                </Badge>
              ) : (
                <span />
              )}
            </div>
          );
        })}
        <div className={ROW}>
          <span className="inline-flex items-center gap-1 text-[13px] text-muted-foreground">
            Indecisos
            <MetricHint metric={UNDECIDED} />
          </span>
          <span className="font-mono text-muted-foreground">{pollPercent(Number(poll.undecided), margin)}</span>
          <span className="relative h-2.5 rounded-xs bg-muted">
            <span
              className="absolute inset-y-0 left-0 rounded-xs bg-faint-foreground/40"
              style={{ width: `${Number(poll.undecided)}%` }}
            />
          </span>
          <span />
        </div>
        <span className="text-xs text-muted-foreground">
          Quem continuar indeciso na votação não vota: o vencedor sai só dos votos dados.
        </span>
      </div>

      {/* Por grupo de eleitores */}
      <div className="grid gap-3 border-t pt-4">
        <span className="text-xs font-medium">
          Por grupo de eleitores · {finalists.map((party) => party.abbr).join(" e ")} e indecisos
        </span>
        <GroupPollRows groups={panel.groups} polls={poll.groups} parties={finalists} />
      </div>
    </>
  );
}
