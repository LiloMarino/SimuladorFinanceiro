import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayList, displayPercent, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty, ElectionPoll } from "@/types";
import { INTENTION, POLL_MARGIN, RUNOFF, VALID_SHARE } from "../lib/election-metrics";
import {
  GROUP_INFO,
  inTechnicalTie,
  marginRange,
  nextPollDate,
  partyFill,
  partyOrder,
  pollPercent,
  pollPoints,
} from "../lib/voters";
import { GroupPollBar } from "./group-poll-bar";
import { PersonMark, PartyMark } from "./party-mark";
import { PollChart } from "./poll-chart";
import { PollLegend } from "./poll-legend";

/** A barra de hoje vai até 50 pontos: quem passa disso enche a barra. */
const BAR_SCALE = 50;
const WIN_LINE = 0.5;

type PollCardProps = { panel: ElectionPanel };

/** A pesquisa mensal e pública: a corrida com a margem, o 1º turno de hoje, cada grupo e a simulação do 2º turno. */
export function PollCard({ panel }: PollCardProps) {
  const latest = panel.polls.at(-1);
  const parties = partyOrder(panel.parties);

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4.5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="grid gap-0.5">
              <h2 className="text-[15px] font-semibold">
                <MetricLabel metric={INTENTION} />
              </h2>
              <span className="text-[13px] text-muted-foreground">Mensal e pública: todos na sala veem a mesma.</span>
            </div>
            {latest && (
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">Atualizada em {displayShortDate(latest.date)}</Badge>
                {latest.margin > 0 && <Badge variant="info">Margem de {latest.margin} pontos no total</Badge>}
              </div>
            )}
          </div>

          {latest ? <PollBody panel={panel} poll={latest} parties={parties} /> : <FirstPollPending panel={panel} />}
        </div>
      </CardContent>
    </Card>
  );
}

function FirstPollPending({ panel }: { panel: ElectionPanel }) {
  return (
    <div className="grid justify-items-center gap-1 rounded-lg border border-dashed px-6 py-8 text-center">
      <span className="text-xs text-muted-foreground">
        Campanha aberta em {displayShortDate(panel.dates.campaign_start)}
      </span>
      <b className="text-[15px] font-semibold">
        A primeira pesquisa sai em {displayShortDate(nextPollDate(panel.today))}
      </b>
      <span className="max-w-md text-[13px] text-muted-foreground">
        Um mês depois de a campanha abrir, e depois todo dia 1º. Até lá, o eleitorado mostra onde cada partido começa em
        cada grupo.
      </span>
    </div>
  );
}

type PollBodyProps = { panel: ElectionPanel; poll: ElectionPoll; parties: ElectionParty[] };

function PollBody({ panel, poll, parties }: PollBodyProps) {
  const points = pollPoints(poll.entries);
  const margin = poll.margin;
  const [leader, runnerUp] = [...parties].sort((a, b) => Number(b.valid_share) - Number(a.valid_share));
  const decidedInFirstRound = leader !== undefined && Number(leader.valid_share) > WIN_LINE;
  const example = parties[0] ? (points.get(parties[0].id) ?? 0) : 0;
  const [exampleLow, exampleHigh] = marginRange(example, margin);

  return (
    <>
      <PollLegend parties={parties} />

      <div className="grid gap-7 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
        {/* Corrida */}
        <div className="grid content-start gap-2.5">
          <span className="text-xs font-medium">
            Desde a abertura da campanha{margin > 0 && " · a faixa clara é a margem"}
          </span>
          <PollChart panel={panel} />
        </div>

        {/* Se a eleição fosse hoje */}
        <div className="grid content-start gap-3.5">
          <span className="inline-flex items-center gap-1 text-xs font-medium">
            Se a eleição fosse hoje · 1º turno
            <MetricHint metric={VALID_SHARE} />
          </span>
          <div className="grid gap-2.5">
            {parties.map((party) => {
              const own = points.get(party.id) ?? 0;
              const others = parties.filter((other) => other.id !== party.id).map((other) => points.get(other.id) ?? 0);
              return (
                <TodayRow
                  key={party.id}
                  party={party}
                  points={own}
                  margin={margin}
                  tie={inTechnicalTie(own, others, margin)}
                />
              );
            })}
            <div className="grid grid-cols-[minmax(0,190px)_80px_120px_1fr] items-center gap-3">
              <span className="text-[13px] text-muted-foreground">Indecisos</span>
              <span className="font-mono text-muted-foreground">{pollPercent(Number(poll.undecided), margin)}</span>
              <RangeBar points={Number(poll.undecided)} margin={0} color="var(--faint-foreground)" />
              <span />
            </div>
          </div>
          <span className="text-xs text-muted-foreground">
            {decidedInFirstRound
              ? `Nos votos válidos, ${leader.abbr} passa de 50% e venceria já no 1º turno.`
              : leader && runnerUp
                ? `Ninguém passa de 50% dos votos válidos: haveria 2º turno entre o ${leader.abbr} e o ${runnerUp.abbr}.`
                : "Ainda não há partidos suficientes para uma disputa."}
          </span>
          {margin > 0 && parties[0] && (
            <p className="rounded-lg bg-subtle px-3 py-2 text-xs leading-normal text-muted-foreground">
              <b className="text-foreground">{POLL_MARGIN.label}:</b> “{pollPercent(example, margin)}, com margem de{" "}
              {margin} pontos para mais ou para menos” quer dizer que o número real do {parties[0].abbr} está entre{" "}
              {pollPercent(exampleLow, margin)} e {pollPercent(exampleHigh, margin)}. Quando as faixas de dois partidos
              se cruzam, ninguém sabe quem lidera: é o empate técnico.
            </p>
          )}
        </div>
      </div>

      <GroupBreakdown panel={panel} poll={poll} parties={parties} />

      <RunoffSimulation panel={panel} />
    </>
  );
}

type TodayRowProps = { party: ElectionParty; points: number; margin: number; tie: boolean };

function TodayRow({ party, points, margin, tie }: TodayRowProps) {
  return (
    <div className="grid grid-cols-[minmax(0,190px)_80px_120px_1fr] items-center gap-3">
      <span className="flex min-w-0 items-center gap-2">
        <PartyMark abbr={party.abbr} color={party.color} size="sm" />
        <span className="truncate text-[13px]">{party.candidate?.name ?? party.name}</span>
      </span>
      <span className="font-mono text-[15px] font-semibold whitespace-nowrap">
        {pollPercent(points, margin)}
        {margin > 0 && <span className="font-normal text-faint-foreground"> ±{margin}</span>}
      </span>
      <RangeBar points={points} margin={margin} color={partyFill(party)} />
      <span>
        {tie && (
          <Badge variant="warning" size="sm">
            Empate técnico
          </Badge>
        )}
      </span>
    </div>
  );
}

/** A barra de um número da pesquisa: cheia até o número, e a faixa clara da margem em volta. */
function RangeBar({ points, margin, color }: { points: number; margin: number; color: string }) {
  const scale = (value: number) => `${Math.min(value / BAR_SCALE, 1) * 100}%`;
  const [low, high] = marginRange(points, margin);
  return (
    <span className="relative h-2.5 w-30 rounded-xs bg-muted">
      {margin > 0 && (
        <span
          className="absolute inset-y-0 rounded-xs opacity-25"
          style={{ left: scale(low), width: `calc(${scale(high)} - ${scale(low)})`, backgroundColor: color }}
        />
      )}
      <span
        className="absolute inset-y-0 left-0 rounded-xs opacity-85"
        style={{ width: scale(points), backgroundColor: color }}
      />
    </span>
  );
}

function GroupBreakdown({ panel, poll, parties }: PollBodyProps) {
  const groups = new Map(panel.groups.map((group) => [group.group, group]));
  const bySize = [...panel.groups].sort((a, b) => Number(b.weight) - Number(a.weight));
  const largest = bySize[0];
  const smallest = bySize.at(-1);

  return (
    <div className="grid gap-3 border-t pt-4">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <span className="text-xs font-medium">
          Por grupo de eleitores · {displayList(parties.map((party) => party.abbr))}
        </span>
        {poll.margin > 0 && largest && smallest && (
          <span className="text-xs text-muted-foreground">
            Grupo menor, amostra menor, margem maior: ±{largest.margin} em {GROUP_INFO[largest.group].short} (
            {displayPercent(largest.weight, 0)} do eleitorado), ±{smallest.margin} em {GROUP_INFO[smallest.group].short}{" "}
            ({displayPercent(smallest.weight, 0)}
            ).
          </span>
        )}
      </div>
      <div className="grid gap-2.5">
        {poll.groups.map((groupPoll) => {
          const group = groups.get(groupPoll.group);
          if (!group) return null;
          const label = GROUP_INFO[groupPoll.group].label;
          const weight = displayPercent(group.weight, 0);
          const points = pollPoints(groupPoll.entries);
          return (
            <div key={groupPoll.group} className="grid grid-cols-[minmax(0,210px)_1fr_auto_40px] items-center gap-3">
              <span className="flex min-w-0 items-center gap-2">
                <span className="truncate text-[13px] font-medium">{label}</span>
                <span className="font-mono text-[11px] text-faint-foreground">{weight}</span>
              </span>
              <GroupPollBar poll={groupPoll} parties={parties} title={`${label} · ${weight} do eleitorado`} />
              <span className="flex justify-end gap-2.5">
                {parties.map((party) => (
                  <span
                    key={party.id}
                    className="w-7 text-right font-mono text-xs font-semibold"
                    style={{ color: partyFill(party) }}
                  >
                    {Math.round(points.get(party.id) ?? 0)}
                  </span>
                ))}
              </span>
              <span className="font-mono text-xs text-faint-foreground">
                {groupPoll.margin > 0 ? `±${groupPoll.margin}` : ""}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function RunoffSimulation({ panel }: { panel: ElectionPanel }) {
  const simulation = panel.runoff_simulation;
  const byId = new Map(panel.parties.map((party) => [party.id, party]));
  const finalists = simulation?.finalists.map((id) => byId.get(id)).filter((party) => party !== undefined) ?? [];
  if (!simulation || finalists.length !== 2) return null;
  const finalistEntries = simulation.entries.filter((entry) => simulation.finalists.includes(entry.party_id));

  return (
    <div className="grid gap-2.5 border-t pt-4">
      <span className="text-xs font-medium">
        <MetricLabel metric={RUNOFF} />
      </span>
      <div className="grid gap-1.5">
        <div className="flex justify-between gap-2 text-[13px]">
          {finalists.map((party) => (
            <span key={party.id} className="inline-flex min-w-0 items-center gap-1.5">
              {party.candidate && <PersonMark person={party.candidate} />}
              <span className="truncate">{party.candidate?.name ?? party.name}</span>
              <PartyMark abbr={party.abbr} color={party.color} size="sm" />
            </span>
          ))}
        </div>
        <div className="flex h-3 overflow-hidden rounded-full bg-muted">
          {finalistEntries.map((entry) => {
            const party = byId.get(entry.party_id);
            return (
              <span
                key={entry.party_id}
                style={{
                  width: `${Number(entry.share) * 100}%`,
                  backgroundColor: party ? partyFill(party) : undefined,
                }}
              />
            );
          })}
        </div>
        <div className="flex justify-between font-mono text-[13px] font-semibold">
          {finalistEntries.map((entry) => (
            <span key={entry.party_id}>{displayPercent(entry.share, 0)}</span>
          ))}
        </div>
      </div>
      {simulation.entries
        .filter((entry) => entry.transfer_to !== null)
        .map((entry) => {
          const from = byId.get(entry.party_id);
          const to = entry.transfer_to !== null ? byId.get(entry.transfer_to) : undefined;
          if (!from || !to) return null;
          return (
            <span key={entry.party_id} className="text-xs text-muted-foreground">
              Os eleitores do {from.abbr} se dividem entre os finalistas pelo saldo de cada um no grupo; a maior parte
              vai para o {to.abbr}.
            </span>
          );
        })}
    </div>
  );
}
