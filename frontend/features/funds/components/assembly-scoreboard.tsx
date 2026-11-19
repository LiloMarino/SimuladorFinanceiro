import { PlayerAvatar } from "@/shared/components/player-avatar";
import { StackedBar } from "@/shared/components/stacked-bar";
import { Badge } from "@/shared/components/ui/badge";
import { playerColorStyle } from "@/shared/lib/player-colors";
import { displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import { missingText, participation, voteShares, type AssemblyCurrent } from "../lib/fund-assembly";

type Voter = AssemblyCurrent["voters"][number];

const STANCE_BADGE = {
  favor: { variant: "success", label: "a favor" },
  against: { variant: "destructive", label: "contra" },
  abstain: { variant: "secondary", label: "não votou" },
} as const;

/** Quem tem cotas e para onde elas vão hoje: a linha de cada cotista jogador. */
function VoterRow({ voter }: { voter: Voter }) {
  const badge = voter.is_manager ? STANCE_BADGE.against : STANCE_BADGE[voter.stance];
  return (
    <li className="flex items-center gap-2.5 border-t border-muted py-2 text-[13px] first:border-t-0">
      <PlayerAvatar nickname={voter.nickname} {...(voter.color ? { color: voter.color } : {})} size="sm" />
      <span
        className="min-w-0 flex-1 truncate font-medium"
        style={voter.color ? { color: playerColorStyle(voter.color).background } : undefined}
        title={voter.nickname}
      >
        {voter.nickname}
        {voter.is_manager && <span className="ml-1.5 text-xs font-normal text-muted-foreground">gestor</span>}
      </span>
      <span className="font-mono text-muted-foreground">{displayQuantity(voter.quotas)}</span>
      <span className="w-14 text-right font-mono text-muted-foreground">{displayPercent(voter.share, 1)}</span>
      <Badge variant={badge.variant} size="tag" className="w-20">
        {voter.is_manager ? "conta contra" : badge.label}
      </Badge>
    </li>
  );
}

type AssemblyScoreboardProps = { assembly: AssemblyCurrent; tally: NonNullable<AssemblyCurrent["tally"]> };

/** O placar ao vivo: o peso de cada lado entre as cotas que votaram, a participação e quem pesa quanto. */
export function AssemblyScoreboard({ assembly, tally }: AssemblyScoreboardProps) {
  const shares = voteShares(tally);
  const turnout = participation(tally, assembly.non_voting);

  return (
    <div className="grid gap-3">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-1 text-[13px]">
        <span>
          <b className="font-bold">A favor</b> {displayPercent(shares.favor, 1)} · {displayQuantity(tally.in_favor)}{" "}
          cotas
        </span>
        <span>
          <b className="font-bold">Contra</b> {displayPercent(shares.against, 1)} · {displayQuantity(tally.against)}{" "}
          cotas
        </span>
      </div>
      <StackedBar
        size="lg"
        segments={[
          { key: "favor", fraction: shares.favor, color: "bg-success" },
          { key: "against", fraction: shares.against, color: "bg-destructive" },
        ]}
      />
      <p className="text-xs text-muted-foreground">
        Votaram {displayQuantity(String(turnout.voted))} de {displayQuantity(String(turnout.eligible))} cotas com voto (
        {displayPercent(turnout.share, 1)}). O formador de mercado e os bots não votam.{" "}
        {missingText(tally, assembly.agenda)}
      </p>
      {assembly.voters.length > 0 && (
        <ul className="grid">
          {assembly.voters.map((voter) => (
            <VoterRow key={voter.user_id} voter={voter} />
          ))}
        </ul>
      )}
    </div>
  );
}
