import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayList, displayPercent, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty, ElectionPoll } from "@/types";
import { campaignEnded } from "../lib/election";
import { raceRows, type RaceRow } from "../lib/federation";
import { INTENTION, POLL_MARGIN, VALID_SHARE } from "../lib/election-metrics";
import {
  GROUP_INFO,
  inTechnicalTie,
  marginRange,
  nextPollDate,
  partyOrder,
  pollPercent,
  pollPoints,
} from "../lib/voters";
import { GroupPollRows } from "./group-poll-rows";
import { PartyMark } from "@/shared/components/party-mark";
import { PartyMarkPair } from "@/shared/components/party-mark-pair";
import { PollChart } from "./poll-chart";
import { PollLegend } from "./poll-legend";
import { PromiseBadges } from "./promise-badges";
import { partyColor } from "@/shared/lib/party-colors";

/** A barra de hoje vai até 50 pontos: quem passa disso enche a barra. */
const BAR_SCALE = 50;
const WIN_LINE = 0.5;

type PollCardProps = { panel: ElectionPanel };

/** A pesquisa mensal e pública: a corrida com a margem, o 1º turno de hoje, e cada grupo. */
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
  if (campaignEnded(panel.phase)) {
    return (
      <div className="grid justify-items-center gap-1 rounded-lg border border-dashed px-6 py-8 text-center">
        <b className="text-[15px] font-semibold">Campanha encerrada</b>
        <span className="max-w-md text-[13px] text-muted-foreground">
          A campanha acabou sem nenhuma pesquisa. O eleitorado mostra onde cada partido começou em cada grupo.
        </span>
      </div>
    );
  }
  return (
    <div className="grid justify-items-center gap-1 rounded-lg border border-dashed px-6 py-8 text-center">
      <span className="text-xs text-muted-foreground">
        Campanha aberta em {displayShortDate(panel.dates.campaign_start)}
      </span>
      <b className="text-[15px] font-semibold">
        A primeira pesquisa sai em {displayShortDate(nextPollDate(panel.today))}
      </b>
      <span className="max-w-md text-[13px] text-muted-foreground">Depois, uma pesquisa todo dia 1º.</span>
    </div>
  );
}

type PollBodyProps = { panel: ElectionPanel; poll: ElectionPoll; parties: ElectionParty[] };

function PollBody({ panel, poll, parties }: PollBodyProps) {
  const points = pollPoints(poll.entries);
  const margin = poll.margin;
  // Os dois partidos de uma federação disputam como uma linha só, somando os votos
  const rows = raceRows(parties, panel.federations, Number(panel.dates.first_round.slice(0, 4)));
  const share = (row: RaceRow) => row.parties.reduce((sum, party) => sum + Number(party.valid_share), 0);
  const [leader, runnerUp] = [...rows].sort((a, b) => share(b) - share(a));
  const mention = (row: RaceRow) => (row.federation ? `a ${row.federation.name}` : `o ${row.parties[0]?.abbr}`);
  const decidedInFirstRound = leader !== undefined && share(leader) > WIN_LINE;
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
            {rows.map((row) => {
              const total = (candidate: RaceRow) =>
                candidate.parties.reduce((sum, party) => sum + (points.get(party.id) ?? 0), 0);
              const own = total(row);
              const others = rows.filter((other) => other.key !== row.key).map(total);
              return (
                <TodayRow
                  key={row.key}
                  row={row}
                  points={points}
                  margin={margin}
                  tie={inTechnicalTie(own, others, margin)}
                />
              );
            })}
            <div className="grid grid-cols-[minmax(0,190px)_80px_120px_1fr] items-center gap-3">
              <span className="text-[13px] text-muted-foreground">Indecisos</span>
              <span className="font-mono text-muted-foreground">{pollPercent(Number(poll.undecided), margin)}</span>
              <RangeBar slices={[{ points: Number(poll.undecided), color: "var(--faint-foreground)" }]} margin={0} />
              <span />
            </div>
          </div>
          <span className="text-xs text-muted-foreground">
            {decidedInFirstRound
              ? `Nos votos válidos, ${mention(leader)} passa de 50% e venceria já no 1º turno.`
              : leader && runnerUp
                ? `Ninguém passa de 50% dos votos válidos: haveria 2º turno entre ${mention(leader)} e ${mention(runnerUp)}.`
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
    </>
  );
}

type TodayRowProps = { row: RaceRow; points: Map<number, number>; margin: number; tie: boolean };

function TodayRow({ row, points, margin, tie }: TodayRowProps) {
  const [first] = row.parties;
  if (!first) return null;
  const slices = row.parties.map((party) => ({ points: points.get(party.id) ?? 0, color: partyColor(party) }));
  const total = slices.reduce((sum, slice) => sum + slice.points, 0);

  return (
    <div className="grid gap-1.5">
      <div className="grid grid-cols-[minmax(0,190px)_80px_120px_1fr] items-center gap-3">
        <span className="flex min-w-0 items-center gap-2">
          {row.federation ? (
            <PartyMarkPair parties={row.parties} size="sm" />
          ) : (
            <PartyMark abbr={first.abbr} color={first.color} size="sm" />
          )}
          <span className="truncate text-[13px]">{row.federation?.name ?? first.candidate?.name ?? first.name}</span>
        </span>
        <span className="font-mono text-[15px] font-semibold whitespace-nowrap">
          {pollPercent(total, margin)}
          {margin > 0 && <span className="font-normal text-faint-foreground"> ±{margin}</span>}
        </span>
        <RangeBar slices={slices} margin={margin} />
        <span>
          {tie && (
            <Badge variant="warning" size="sm">
              Empate técnico
            </Badge>
          )}
        </span>
      </div>
      {row.federation && (
        <span className="pl-8 text-xs text-muted-foreground">
          {row.parties
            .map((party, index) => `${party.abbr} ${displayPercent((slices[index]?.points ?? 0) / 100, 1)}`)
            .join(" + ")}
        </span>
      )}
      {first.promises.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 pl-8">
          <span className="text-xs text-muted-foreground">
            {first.is_computer ? "Promete pelos valores dele" : "Promessas"}
          </span>
          <PromiseBadges promises={first.promises} computer={first.is_computer} />
        </div>
      )}
    </div>
  );
}

/** A barra de um número da pesquisa: uma fatia por partido empilhadas até o total, e a faixa clara da margem em volta. */
function RangeBar({ slices, margin }: { slices: { points: number; color: string }[]; margin: number }) {
  const scale = (value: number) => `${Math.min(value / BAR_SCALE, 1) * 100}%`;
  const total = slices.reduce((sum, slice) => sum + slice.points, 0);
  const [low, high] = marginRange(total, margin);
  // Onde cada fatia começa: a soma das anteriores
  const starts = slices.map((_, index) => slices.slice(0, index).reduce((sum, slice) => sum + slice.points, 0));
  return (
    <span className="relative h-2.5 w-30 overflow-hidden rounded-xs bg-muted">
      {margin > 0 && (
        <span
          className="absolute inset-y-0 rounded-xs opacity-25"
          style={{ left: scale(low), width: `calc(${scale(high)} - ${scale(low)})`, backgroundColor: slices[0]?.color }}
        />
      )}
      {slices.map((slice, index) => {
        const left = scale(starts[index] ?? 0);
        return (
          <span
            key={index}
            className="absolute inset-y-0 opacity-85"
            style={{
              left,
              width: `calc(${scale((starts[index] ?? 0) + slice.points)} - ${left})`,
              backgroundColor: slice.color,
            }}
          />
        );
      })}
    </span>
  );
}

function GroupBreakdown({ panel, poll, parties }: PollBodyProps) {
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
      <GroupPollRows groups={panel.groups} polls={poll.groups} parties={parties} />
    </div>
  );
}
