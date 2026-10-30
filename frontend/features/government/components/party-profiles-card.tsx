import { useState } from "react";
import { ChevronRight, X } from "lucide-react";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { cn } from "@/shared/lib/utils";
import { displayPercent, displayShortMonthYear } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty, VoterGroup, VoterGroupInfo } from "@/types";
import { AFFINITY } from "../lib/election-metrics";
import { VALUE_INFO, VOTER_VALUES } from "@/shared/lib/party-flags";
import {
  GROUP_INFO,
  distanceWord,
  groupScores,
  partyFill,
  partyOrder,
  signedPoints,
  topWants,
  valueScores,
} from "../lib/voters";
import { PartyMark } from "./party-mark";
import { ProfileRadar } from "./profile-radar";
import { PromiseBadges } from "./promise-badges";
import { ValueChips } from "./value-chip";

const FOUNDING_COLOR = "var(--muted-foreground)";
const DISTANCE_TONE = { up: "text-success", wa: "text-warning", dn: "text-destructive" } as const;

type PartyProfilesCardProps = { panel: ElectionPanel };

/** O perfil público de cada partido em seis valores, e a comparação de um partido com o que um grupo quer. */
export function PartyProfilesCard({ panel }: PartyProfilesCardProps) {
  const parties = partyOrder(panel.parties);
  const [comparing, setComparing] = useState<number | null>(null);
  const [group, setGroup] = useState<VoterGroup>("FORMAL_WORKERS");
  const compared = parties.find((party) => party.id === comparing);
  const groupInfo = panel.groups.find((item) => item.group === group);

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid gap-0.5">
            <h2 className="text-[15px] font-semibold">Partidos na disputa</h2>
            <span className="text-[13px] text-muted-foreground">
              As bandeiras e o perfil de todos são públicos. O perfil parte das bandeiras e se move com o que cada
              partido aprova no governo.
            </span>
          </div>

          {/* Perfil de cada partido */}
          <div className="grid gap-3.5 md:grid-cols-2 2xl:grid-cols-3">
            {parties.map((party) => (
              <PartyTile
                key={party.id}
                party={party}
                selected={party.id === comparing}
                onCompare={() => setComparing(party.id)}
              />
            ))}
          </div>

          {/* Partido contra um grupo */}
          {compared && groupInfo && (
            <GroupComparison
              party={compared}
              group={groupInfo}
              groups={panel.groups}
              onGroupChange={setGroup}
              onClose={() => setComparing(null)}
            />
          )}
        </div>
      </CardContent>
    </Card>
  );
}

type PartyTileProps = { party: ElectionParty; selected: boolean; onCompare: () => void };

function PartyTile({ party, selected, onCompare }: PartyTileProps) {
  return (
    <div className={cn("grid content-start gap-2.5 rounded-lg border p-4", selected && "border-primary")}>
      <div className="flex items-center gap-2">
        <PartyMark abbr={party.abbr} color={party.color} size="md" />
        <div className="grid min-w-0 flex-1">
          <b className="truncate text-sm font-semibold">{party.name}</b>
          <span className="truncate text-xs text-muted-foreground">
            {party.candidate?.name ?? party.founder ?? "sem candidato"}
          </span>
        </div>
        {party.is_computer && (
          <Badge variant="secondary" size="sm">
            Computador
          </Badge>
        )}
      </div>
      <ValueChips values={party.flags} />
      <PartyPromises party={party} />
      <div className="flex justify-center">
        <ProfileRadar
          width={282}
          height={206}
          label={`Perfil do ${party.abbr}, hoje e na fundação`}
          series={[
            { key: "founding", scores: valueScores(party.founding_radar), color: FOUNDING_COLOR, dashed: true },
            { key: "today", scores: valueScores(party.radar), color: partyFill(party) },
          ]}
        />
      </div>
      <div className="flex justify-center gap-3.5 text-xs text-muted-foreground">
        <span className="inline-flex items-center gap-1.5">
          <span className="w-3.5 border-t-2" style={{ borderColor: partyFill(party) }} />
          Hoje
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="w-3.5 border-t-2 border-dashed border-muted-foreground" />
          Na fundação
        </span>
      </div>
      <span className="text-xs text-muted-foreground">
        Último movimento: <LastMove party={party} />
      </span>
      <Button variant="link" size="sm" className="justify-self-start" onClick={onCompare}>
        Comparar com um grupo
        <ChevronRight />
      </Button>
    </div>
  );
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
    <section className="grid gap-4 border-t pt-4">
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
              { key: "profile", scores: profile, color: partyFill(party) },
            ]}
          />
          <div className="flex gap-3.5 text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <span className="w-3.5 border-t-2" style={{ borderColor: partyFill(party) }} />
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
              . O perfil se move com as medidas que o partido aprova no governo, e a afinidade vai junto.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
