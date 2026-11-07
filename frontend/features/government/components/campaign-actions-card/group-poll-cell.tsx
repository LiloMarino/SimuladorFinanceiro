import { partyColor } from "@/shared/lib/party-colors";
import type { ElectionParty, ElectionPoll } from "@/types";
import { pollPercent, pollPoints } from "../../lib/voters";

type GroupPollCellProps = {
  poll: ElectionPoll["groups"][number] | undefined;
  party: ElectionParty;
  parties: ElectionParty[];
};

/** A intenção de voto do partido no grupo, com a margem de erro; se outro partido lidera, o líder vem embaixo. */
export function GroupPollCell({ poll, party, parties }: GroupPollCellProps) {
  if (!poll) return <span className="text-right text-xs text-faint-foreground">sem pesquisa</span>;

  const points = pollPoints(poll.entries);
  const own = points.get(party.id) ?? 0;
  const leader = parties.reduce<ElectionParty | null>(
    (best, candidate) => (!best || (points.get(candidate.id) ?? 0) > (points.get(best.id) ?? 0) ? candidate : best),
    null,
  );
  const leaderPoints = leader ? (points.get(leader.id) ?? 0) : 0;

  return (
    <span className="grid justify-items-end">
      <span className="font-mono">
        <b style={{ color: partyColor(party) }}>
          {party.abbr} {pollPercent(own, poll.margin)}
        </b>
        {poll.margin > 0 && <span className="text-faint-foreground"> ±{poll.margin}</span>}
      </span>
      {leader && leader.id !== party.id && leaderPoints > own && (
        <span className="font-mono text-xs text-faint-foreground">
          líder {leader.abbr} {pollPercent(leaderPoints, poll.margin)}
        </span>
      )}
    </span>
  );
}
