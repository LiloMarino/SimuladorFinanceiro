import { PlayerAvatar } from "@/shared/components/player-avatar";
import { StackedBar } from "@/shared/components/stacked-bar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { cn } from "@/shared/lib/utils";
import { playerColorStyle } from "@/shared/lib/player-colors";
import { displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import { useCastAssemblyVote } from "../hooks/mutations/useCastAssemblyVote";
import { missingText, tallyFractions, type AssemblyCurrent, type AssemblyTally } from "../lib/fund-assembly";

type Voter = AssemblyCurrent["voters"][number];

const STANCE_BADGE = {
  favor: { variant: "success", label: "a favor" },
  against: { variant: "destructive", label: "contra" },
  abstain: { variant: "secondary", label: "não votou" },
} as const;

const LEGEND = [
  { field: "in_favor", label: "a favor", hint: "cotas de quem votou pela troca", dot: "bg-success" },
  { field: "against", label: "contra", hint: "cotas de quem votou contra, mais as do gestor", dot: "bg-destructive" },
  {
    field: "abstention",
    label: "abstenção",
    hint: "quem não votou, bots e formador de mercado",
    dot: "bg-faint-foreground",
  },
] as const;

/** A barra do placar: o tamanho de cada trecho é o peso das cotas no total da gestora. */
function TallyBar({ tally }: { tally: AssemblyTally }) {
  const fractions = tallyFractions(tally);
  return (
    <StackedBar
      size="lg"
      segments={[
        { key: "favor", fraction: fractions.favor, color: "bg-success" },
        { key: "abstention", fraction: fractions.abstention, fill: "var(--faint-foreground)" },
        { key: "against", fraction: fractions.against, color: "bg-destructive" },
      ]}
    />
  );
}

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

type AssemblyScoreboardProps = { fundId: number; assembly: AssemblyCurrent; tally: AssemblyTally };

/** O placar ao vivo da votação: a barra, a legenda, quem pesa quanto e o voto de quem pode votar. */
export function AssemblyScoreboard({ fundId, assembly, tally }: AssemblyScoreboardProps) {
  const vote = useCastAssemblyVote(fundId);

  return (
    <div className="grid gap-4">
      <div className="grid gap-2">
        <TallyBar tally={tally} />
        <ul className="flex flex-wrap gap-x-5 gap-y-1.5 text-xs text-muted-foreground">
          {LEGEND.map((item) => (
            <li key={item.field} className="flex items-center gap-1.5">
              <span className={cn("size-2 rounded-full", item.dot)} aria-hidden />
              <b className="font-mono font-semibold text-foreground">{displayQuantity(tally[item.field])}</b>
              <span>
                {item.label} ({item.hint})
              </span>
            </li>
          ))}
        </ul>
        <p className="text-[13px]">{missingText(tally)}</p>
      </div>

      {assembly.voters.length > 0 && (
        <ul className="grid">
          {assembly.voters.map((voter) => (
            <VoterRow key={voter.user_id} voter={voter} />
          ))}
        </ul>
      )}

      {assembly.can_vote && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[13px] text-muted-foreground">Seu voto, que você muda até o fim:</span>
          <Button
            size="sm"
            variant={assembly.my_vote === true ? "success" : "outline-success"}
            disabled={vote.isPending}
            onClick={() => vote.mutate({ in_favor: true })}
          >
            {vote.isPending && <Spinner />}A favor da troca
          </Button>
          <Button
            size="sm"
            variant={assembly.my_vote === false ? "destructive" : "outline-destructive"}
            disabled={vote.isPending}
            onClick={() => vote.mutate({ in_favor: false })}
          >
            Contra
          </Button>
        </div>
      )}
    </div>
  );
}
