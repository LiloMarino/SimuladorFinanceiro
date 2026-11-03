import { MetricHint } from "@/shared/components/metric-hint";
import { partyColor } from "@/shared/lib/party-colors";
import { displayPercent } from "@/shared/lib/utils/display";
import type { ElectionParty, ElectionPoll, VoterGroupInfo } from "@/types";
import { POLL_MARGIN } from "../lib/election-metrics";
import { GROUP_INFO, pollPoints } from "../lib/voters";
import { GroupPollBar } from "./group-poll-bar";
import { PartyMark } from "@/shared/components/party-mark";

type GroupPollRowsProps = {
  groups: VoterGroupInfo[];
  polls: ElectionPoll["groups"];
  /** Os partidos de cada coluna de número, na ordem da pesquisa */
  parties: ElectionParty[];
};

/** A pesquisa em cada grupo de eleitores: peso, barra, o número de cada partido e a margem, com cabeçalho. */
export function GroupPollRows({ groups, polls, parties }: GroupPollRowsProps) {
  const weights = new Map(groups.map((group) => [group.group, group.weight]));
  // Uma coluna fixa por partido e a da margem: o cabeçalho e as linhas dividem as mesmas colunas
  const columns = `minmax(0,240px) minmax(0,1fr) repeat(${parties.length}, 3rem) 4.5rem`;

  return (
    <div className="grid gap-1">
      <div
        className="grid items-center gap-3 border-b pb-1.5 text-xs font-medium text-muted-foreground"
        style={{ gridTemplateColumns: columns }}
      >
        <span>Grupo e peso no eleitorado</span>
        <span>Intenção de voto no grupo</span>
        {parties.map((party) => (
          <span key={party.id} className="flex justify-end">
            <PartyMark abbr={party.abbr} color={party.color} />
          </span>
        ))}
        <span className="flex items-center justify-end gap-1">
          Margem
          <MetricHint metric={POLL_MARGIN} />
        </span>
      </div>
      {polls.map((groupPoll) => {
        const weight = weights.get(groupPoll.group);
        if (weight === undefined) return null;
        const label = GROUP_INFO[groupPoll.group].label;
        const weightLabel = displayPercent(weight, 0);
        const points = pollPoints(groupPoll.entries);
        return (
          <div key={groupPoll.group} className="grid h-8 items-center gap-3" style={{ gridTemplateColumns: columns }}>
            <span className="flex min-w-0 items-center gap-2">
              <span className="truncate text-sm">{label}</span>
              <span className="font-mono text-xs text-faint-foreground">{weightLabel}</span>
            </span>
            <GroupPollBar poll={groupPoll} parties={parties} title={`${label} · ${weightLabel} do eleitorado`} />
            {parties.map((party) => (
              <span
                key={party.id}
                className="text-right font-mono text-sm font-semibold"
                style={{ color: partyColor(party) }}
              >
                {Math.round(points.get(party.id) ?? 0)}
              </span>
            ))}
            <span className="text-right font-mono text-sm text-muted-foreground">
              {groupPoll.margin > 0 ? `±${groupPoll.margin}` : ""}
            </span>
          </div>
        );
      })}
    </div>
  );
}
