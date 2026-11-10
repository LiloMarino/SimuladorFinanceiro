import { useState, type ReactNode } from "react";
import { ChevronRight, X } from "lucide-react";
import { MetricLabel } from "@/shared/components/metric-hint";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { cn } from "@/shared/lib/utils";
import { displayMoneyWhole, displayPercent, displayShortMonthYear } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty, VoterGroup, VoterGroupInfo } from "@/types";
import { AFFINITY, BUDGET, INTENTION, SPENT } from "../lib/election-metrics";
import { raceRows } from "../lib/federation";
import { VALUE_INFO, VOTER_VALUES } from "@/shared/lib/party-flags";
import {
  GROUP_INFO,
  distanceWord,
  groupScores,
  partyOrder,
  pollPercent,
  profileMoved,
  signedPoints,
  topWants,
  valueScores,
} from "../lib/voters";
import { PartyMark, PersonMark } from "@/shared/components/party-mark";
import { ProfileRadar } from "@/shared/components/profile-radar";
import { FederationTile } from "./federation-tile";
import { PromiseBadges } from "./promise-badges";
import { ValueChips } from "@/shared/components/value-chip";
import { partyColor } from "@/shared/lib/party-colors";

const FOUNDING_COLOR = "var(--muted-foreground)";
const DISTANCE_TONE = { up: "text-success", wa: "text-warning", dn: "text-destructive" } as const;

type PartyProfilesCardProps = { panel: ElectionPanel };

/** Um bloco por partido (chapa, contas públicas e perfil em seis valores) e a comparação de um partido com o que um grupo quer. */
export function PartyProfilesCard({ panel }: PartyProfilesCardProps) {
  const parties = partyOrder(panel.parties);
  const [comparing, setComparing] = useState<number | null>(null);
  const [group, setGroup] = useState<VoterGroup>("FORMAL_WORKERS");
  const compared = parties.find((party) => party.id === comparing);
  const groupInfo = panel.groups.find((item) => item.group === group);
  // Chapa, filiados, intenção, verba e gasto existem a partir da abertura da campanha
  const campaignOpen = panel.phase !== "BEFORE_CAMPAIGN";
  const ticketOpen = panel.phase === "CAMPAIGN" && panel.today <= panel.dates.ticket_deadline;
  const margin = panel.polls.at(-1)?.margin ?? 0;
  // Os dois partidos de uma federação ocupam um cartão só
  const rows = raceRows(parties, panel.federations, Number(panel.dates.first_round.slice(0, 4)));

  return (
    <div className="@container grid gap-4">
      <div className="grid gap-0.5">
        <h2 className="text-[15px] font-semibold">Partidos na disputa</h2>
        <span className="text-[13px] text-muted-foreground">
          As bandeiras, o perfil, os filiados, a verba e o gasto de todos são públicos, como a prestação de contas de
          uma campanha. O perfil parte das bandeiras e se move com o que cada partido aprova no governo.
        </span>
      </div>

      {/* Um bloco por partido */}
      <div className="grid items-stretch gap-4 @2xl:grid-cols-2 @6xl:grid-cols-3">
        {rows.map((row) => {
          const [party] = row.parties;
          if (!party) return null;
          if (row.federation) {
            return (
              <FederationTile
                key={row.key}
                row={{ ...row, federation: row.federation }}
                current={row.parties.some((member) => member.id === panel.my_party?.party_id)}
                margin={margin}
              />
            );
          }
          return (
            <PartyTile
              key={row.key}
              party={party}
              selected={party.id === comparing}
              current={party.id === panel.my_party?.party_id}
              campaignOpen={campaignOpen}
              ticketOpen={ticketOpen}
              margin={margin}
              onCompare={() => setComparing(party.id)}
            />
          );
        })}
      </div>

      {/* Partido contra um grupo */}
      {compared && groupInfo && (
        <Card>
          <CardContent>
            <GroupComparison
              party={compared}
              group={groupInfo}
              groups={panel.groups}
              onGroupChange={setGroup}
              onClose={() => setComparing(null)}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}

type PartyTileProps = {
  party: ElectionParty;
  selected: boolean;
  current: boolean;
  campaignOpen: boolean;
  ticketOpen: boolean;
  margin: number;
  onCompare: () => void;
};

function PartyTile({ party, selected, current, campaignOpen, ticketOpen, margin, onCompare }: PartyTileProps) {
  const moved = profileMoved(party);
  return (
    <div className={cn("rounded-xl", selected && "ring-2 ring-primary")}>
      <Card variant={current ? "info" : "default"} className="h-full">
        <CardContent className="h-full">
          <div className="flex h-full flex-col gap-3.5">
            {/* Nome e chapa */}
            <div className="grid gap-1.5">
              <div className="flex items-center gap-2">
                <PartyMark abbr={party.abbr} color={party.color} size="md" />
                <b className="min-w-0 flex-1 text-[15px] font-semibold">{party.name}</b>
                {party.is_computer && <Badge variant="secondary">Computador</Badge>}
                {current && <Badge variant="info">Seu partido</Badge>}
              </div>
              <span className="flex min-h-5 flex-wrap items-center gap-1.5 text-[13px] text-muted-foreground">
                {party.candidate ? (
                  <>
                    <PersonMark person={party.candidate} />
                    {party.candidate.name}
                    {campaignOpen && <span>· {ticketLine(party, ticketOpen)}</span>}
                  </>
                ) : (
                  (party.founder ?? "sem candidato")
                )}
              </span>
            </div>

            {/* Contas públicas do partido */}
            {campaignOpen && (
              <dl className="grid grid-cols-2 gap-x-4 gap-y-2.5 rounded-lg bg-subtle px-3.5 py-3">
                <Stat label={<MetricLabel metric={INTENTION} />}>
                  <span className="font-mono">{pollPercent(Number(party.intention_points), margin)}</span>
                  {margin > 0 && <span className="font-mono text-xs font-normal text-muted-foreground">±{margin}</span>}
                </Stat>
                <Stat label="Filiados">
                  {party.is_computer ? (
                    <span className="font-normal text-muted-foreground">computador</span>
                  ) : (
                    <span className="inline-flex">
                      {party.members.map((member, index) => (
                        <span
                          key={member.nickname}
                          className={index > 0 ? "-ml-1.5" : undefined}
                          title={member.nickname}
                        >
                          <PlayerAvatar nickname={member.nickname} color={member.color} size="sm" />
                        </span>
                      ))}
                    </span>
                  )}
                </Stat>
                <Stat label={<MetricLabel metric={BUDGET} />}>
                  <span className="font-mono">{displayMoneyWhole(party.budget)}</span>
                </Stat>
                <Stat label={<MetricLabel metric={SPENT} />}>
                  <span className="font-mono">{displayMoneyWhole(party.spent)}</span>
                </Stat>
              </dl>
            )}

            {/* Bandeiras e promessas */}
            <div className="grid gap-1.5">
              <span className="text-xs font-medium text-muted-foreground">Bandeiras</span>
              <ValueChips values={party.flags} />
            </div>
            <PartyPromises party={party} />

            {/* Perfil: o radar fica na base para alinhar entre os cartões */}
            <div className="mt-auto grid gap-2">
              <div className="flex justify-center">
                <ProfileRadar
                  width={360}
                  height={208}
                  labelSize={14}
                  label={`Perfil do ${party.abbr}${moved ? ", hoje e na fundação" : ""}`}
                  series={[
                    ...(moved
                      ? [
                          {
                            key: "founding",
                            scores: valueScores(party.founding_radar),
                            color: FOUNDING_COLOR,
                            dashed: true,
                          },
                        ]
                      : []),
                    { key: "today", scores: valueScores(party.radar), color: partyColor(party) },
                  ]}
                />
              </div>
              <div className="flex justify-center gap-3.5 text-xs text-muted-foreground">
                <span className="inline-flex items-center gap-1.5">
                  <span className="w-3.5 border-t-2" style={{ borderColor: partyColor(party) }} />
                  Hoje
                </span>
                {moved && (
                  <span className="inline-flex items-center gap-1.5">
                    <span className="w-3.5 border-t-2 border-dashed border-muted-foreground" />
                    Na fundação
                  </span>
                )}
              </div>
            </div>
            <span className="text-[13px] text-muted-foreground">
              Último movimento: <LastMove party={party} />
            </span>
            <Button variant="link" size="sm" className="justify-self-start" onClick={onCompare}>
              Comparar com um grupo
              <ChevronRight />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function Stat({ label, children }: { label: ReactNode; children: ReactNode }) {
  return (
    <div className="grid gap-0.5">
      <dt className="text-xs font-medium text-muted-foreground">{label}</dt>
      <dd className="flex min-h-6 items-center gap-1 font-semibold">{children}</dd>
    </div>
  );
}

function ticketLine(party: ElectionParty, ticketOpen: boolean) {
  if (party.vice) {
    if (party.vice_phase === "PENDING") return `vice: ${party.vice.name}, aguardando`;
    if (party.vice_phase === "DECLINED") return `vice: ${party.vice.name} recusou`;
    return `vice: ${party.vice.name}`;
  }
  // Com a inscrição aberta a chapa ainda pode ganhar vice; fechada, concorre sem
  return ticketOpen && !party.is_computer ? "vice: vaga aberta" : "sem vice";
}

/** As promessas da chapa nesta eleição, e as das eleições que já passaram. */
function PartyPromises({ party }: { party: ElectionParty }) {
  if (party.promises.length === 0 && party.past_promises.length === 0) return null;
  return (
    <div className="grid gap-1.5">
      {party.promises.length > 0 && (
        <div className="grid gap-1">
          <span className="text-xs font-medium text-muted-foreground">Promessas</span>
          <PromiseBadges promises={party.promises} computer={party.is_computer} />
        </div>
      )}
      {party.past_promises.map((record) => (
        <div key={record.election_year} className="grid gap-1">
          <span className="text-xs text-muted-foreground">
            Em {record.election_year} · {record.elected ? "eleita" : "não eleita"}
          </span>
          <PromiseBadges promises={record.promises} />
        </div>
      ))}
    </div>
  );
}

function LastMove({ party }: { party: ElectionParty }) {
  const [last] = party.moves;
  if (!last) {
    return party.is_computer ? "nenhum: o computador mantém o perfil da fundação" : "nenhum ainda";
  }
  return (
    <>
      <b className="font-semibold text-foreground">
        {last.moves.map((move) => `${signedPoints(Number(move.points))} ${VALUE_INFO[move.value].label}`).join(", ")}
      </b>{" "}
      · {last.description.toLowerCase()} ({displayShortMonthYear(last.date)})
    </>
  );
}

type GroupComparisonProps = {
  party: ElectionParty;
  group: VoterGroupInfo;
  groups: VoterGroupInfo[];
  onGroupChange: (group: VoterGroup) => void;
  onClose: () => void;
};

function GroupComparison({ party, group, groups, onGroupChange, onClose }: GroupComparisonProps) {
  const wants = valueScores(group.wants);
  const profile = valueScores(party.radar);
  const affinity = groupScores(party.affinity)[group.group];
  const founding = groupScores(party.founding_affinity)[group.group];
  const groupLabel = GROUP_INFO[group.group].label.toLowerCase();
  const favorites = topWants(group);

  return (
    <section className="grid gap-4">
      <div className="flex items-start justify-between gap-4">
        <div className="grid gap-0.5">
          <h3 className="text-[15px] font-semibold">{party.abbr} contra um grupo</h3>
          <span className="text-[13px] text-muted-foreground">
            Onde as duas formas se cobrem, o grupo gosta do partido.
          </span>
        </div>
        <Button variant="outline" size="sm" onClick={onClose}>
          <X />
          Fechar
        </Button>
      </div>

      <ToggleGroup
        variant="segmented"
        aria-label="Grupo de eleitores"
        className="flex-wrap"
        value={[group.group]}
        onValueChange={(values) => values[0] && onGroupChange(values[0] as VoterGroup)}
      >
        {groups.map((item) => (
          <ToggleGroupItem key={item.group} value={item.group}>
            {GROUP_INFO[item.group].short}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>

      <div className="grid items-center gap-8 lg:grid-cols-[auto_minmax(0,1fr)]">
        <div className="grid justify-items-center gap-2">
          <ProfileRadar
            width={390}
            height={286}
            label={`Perfil do ${party.abbr} contra o que os ${groupLabel} querem`}
            series={[
              { key: "wants", scores: wants, color: FOUNDING_COLOR, dashed: true },
              { key: "profile", scores: profile, color: partyColor(party) },
            ]}
          />
          <div className="flex gap-3.5 text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <span className="w-3.5 border-t-2" style={{ borderColor: partyColor(party) }} />
              Perfil do {party.abbr}
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="w-3.5 border-t-2 border-dashed border-muted-foreground" />O que os {groupLabel} querem
            </span>
          </div>
        </div>

        <div className="grid content-start gap-3">
          <div className="flex gap-6">
            <div className="grid gap-0.5">
              <span className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
                <MetricLabel metric={AFFINITY} />
              </span>
              <span className="font-mono text-2xl font-semibold">{Math.round(affinity)}</span>
              <span className="text-xs text-muted-foreground">era {Math.round(founding)} na fundação</span>
            </div>
            <div className="grid gap-0.5">
              <span className="text-xs font-medium tracking-wide text-muted-foreground uppercase">Peso</span>
              <span className="font-mono text-2xl font-semibold">{displayPercent(group.weight, 0)}</span>
              <span className="text-xs text-muted-foreground">do eleitorado</span>
            </div>
          </div>

          <div className="grid gap-2 border-t pt-3">
            {VOTER_VALUES.map((value) => {
              const distance = distanceWord(wants[value], profile[value]);
              return (
                <div
                  key={value}
                  className="grid grid-cols-[minmax(0,170px)_90px_90px_60px] items-center gap-2.5 text-xs"
                >
                  <b className="font-semibold" style={{ color: VALUE_INFO[value].color }}>
                    {VALUE_INFO[value].label}
                  </b>
                  <span className="font-mono">quer {Math.round(wants[value])}</span>
                  <span className="font-mono">
                    {party.abbr} {Math.round(profile[value])}
                  </span>
                  <span className={cn("text-right font-mono font-semibold", DISTANCE_TONE[distance.tone])}>
                    {distance.word}
                  </span>
                </div>
              );
            })}
          </div>

          {favorites.length > 0 && (
            <p className="rounded-lg bg-subtle px-3 py-2 text-xs leading-normal text-muted-foreground">
              O que os {groupLabel} mais querem:{" "}
              {favorites
                .map(
                  (value) =>
                    `${VALUE_INFO[value].label} (${distanceWord(wants[value], profile[value]).word} do ${party.abbr})`,
                )
                .join(" e ")}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
