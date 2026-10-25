import { MetricLabel } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayPercent, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty } from "@/types";
import { INTENTION, RUNOFF, VALID_SHARE } from "../lib/election-metrics";
import { PersonMark, PartyMark } from "./party-mark";
import { PollChart } from "./poll-chart";

/** A barra de votos válidos vai até 60%: assim a marca dos 50% cai perto da ponta e o limite fica à vista. */
const BAR_SCALE = 0.6;
const WIN_LINE = 0.5;

const sortByShare = (parties: ElectionParty[]) =>
  [...parties].sort((a, b) => Number(b.valid_share) - Number(a.valid_share) || a.id - b.id);

type PollCardProps = { panel: ElectionPanel };

/** Pesquisa de intenção de voto, o 1º turno de hoje em votos válidos e a simulação do 2º turno. */
export function PollCard({ panel }: PollCardProps) {
  const ranked = sortByShare(panel.parties);
  const leaderShare = ranked[0] ? Number(ranked[0].valid_share) : 0;
  const decidedInFirstRound = leaderShare > WIN_LINE;

  return (
    <Card>
      <CardContent>
        <div className="grid gap-3.5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-[15px] font-semibold">
              <MetricLabel metric={INTENTION} />
            </h2>
            <Badge variant="secondary">Atualizada em {displayShortDate(panel.today)}</Badge>
          </div>

          {/* Legenda */}
          <div className="flex flex-wrap gap-3.5 text-xs text-muted-foreground">
            {panel.parties.map((party) => (
              <span key={party.id} className="inline-flex items-center gap-1.5">
                <span
                  className={party.is_computer ? "w-3.5 border-t-2 border-dashed" : "h-0.5 w-3.5 rounded-full"}
                  style={
                    party.is_computer
                      ? { borderColor: party.color ?? "var(--muted-foreground)" }
                      : { backgroundColor: party.color ?? "var(--muted-foreground)" }
                  }
                />
                {party.abbr}
                {party.candidate && ` · ${party.candidate.name}`}
              </span>
            ))}
            <span className="inline-flex items-center gap-1.5">
              <span className="w-3.5 border-t-2 border-dotted border-faint-foreground" />
              Indecisos
            </span>
          </div>

          <PollChart panel={panel} />

          <div className="grid gap-5 border-t pt-3.5 lg:grid-cols-[minmax(0,1.25fr)_minmax(0,1fr)]">
            {/* Se a eleição fosse hoje */}
            <div className="grid content-start gap-2.5">
              <span className="text-sm font-medium">
                <MetricLabel metric={VALID_SHARE} />
                <span className="ml-1.5 font-normal text-muted-foreground">· 1º turno, hoje</span>
              </span>
              <div className="grid gap-2">
                {ranked.map((party) => (
                  <ShareRow key={party.id} party={party} />
                ))}
                <div className="grid grid-cols-[minmax(0,190px)_1fr_52px] gap-2.5 text-[11px] text-muted-foreground">
                  <span />
                  <span className="relative h-3.5">
                    <span
                      className="absolute -translate-x-1/2 whitespace-nowrap"
                      style={{ left: `${(WIN_LINE / BAR_SCALE) * 100}%` }}
                    >
                      50%: vence no 1º turno
                    </span>
                  </span>
                  <span />
                </div>
              </div>
              <span className="text-xs text-muted-foreground">
                {decidedInFirstRound
                  ? `Se fosse hoje, ${ranked[0].abbr} venceria já no 1º turno.`
                  : ranked.length >= 2
                    ? `Ninguém passa de 50%: haveria 2º turno entre o ${ranked[0].abbr} e o ${ranked[1].abbr}.`
                    : "Ainda não há partidos suficientes para uma disputa."}
              </span>
            </div>

            {/* Simulação do 2º turno */}
            <RunoffSimulation panel={panel} />
          </div>

          <p className="rounded-lg bg-subtle px-3 py-2 text-xs leading-normal text-muted-foreground">
            {INTENTION.definition} {INTENTION.example}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function ShareRow({ party }: { party: ElectionParty }) {
  const share = Number(party.valid_share);
  return (
    <div className="grid grid-cols-[minmax(0,190px)_1fr_52px] items-center gap-2.5 text-[13px]">
      <span className="flex min-w-0 items-center gap-1.5">
        {party.candidate && <PersonMark person={party.candidate} />}
        <span className="truncate">{party.candidate?.name ?? party.name}</span>
        <PartyMark abbr={party.abbr} color={party.color} size="sm" />
      </span>
      <span className="relative h-2.5 rounded-full bg-muted">
        <span
          className="absolute inset-y-0 left-0 rounded-full"
          style={{
            width: `${Math.min((share / BAR_SCALE) * 100, 100)}%`,
            backgroundColor: party.color ?? "var(--muted-foreground)",
          }}
        />
        <span
          className="absolute -inset-y-1 border-l-2 border-dashed border-foreground"
          style={{ left: `${(WIN_LINE / BAR_SCALE) * 100}%` }}
        />
      </span>
      <span className="text-right font-mono font-semibold">{displayPercent(share, 1)}</span>
    </div>
  );
}

function RunoffSimulation({ panel }: { panel: ElectionPanel }) {
  const simulation = panel.runoff_simulation;
  const byId = new Map(panel.parties.map((party) => [party.id, party]));
  const finalists = simulation?.finalists.map((id) => byId.get(id)).filter((party) => party !== undefined) ?? [];

  return (
    <div className="grid content-start gap-2.5">
      <span className="text-sm font-medium">
        <MetricLabel metric={RUNOFF} />
      </span>
      {simulation && finalists.length === 2 ? (
        <>
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
              {simulation.entries
                .filter((entry) => simulation.finalists.includes(entry.party_id))
                .map((entry) => (
                  <span
                    key={entry.party_id}
                    style={{
                      width: `${Number(entry.share) * 100}%`,
                      backgroundColor: byId.get(entry.party_id)?.color ?? "var(--muted-foreground)",
                    }}
                  />
                ))}
            </div>
            <div className="flex justify-between font-mono text-[13px] font-semibold">
              {simulation.entries
                .filter((entry) => simulation.finalists.includes(entry.party_id))
                .map((entry) => (
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
                  Os eleitores do {from.abbr} (promessa {from.promise}) vão para o finalista com a promessa mais
                  parecida: o {to.abbr} ({to.promise}).
                </span>
              );
            })}
        </>
      ) : (
        <span className="text-xs text-muted-foreground">Precisa de pelo menos dois partidos para simular.</span>
      )}
    </div>
  );
}
