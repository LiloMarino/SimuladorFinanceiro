import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { useAuth } from "@/shared/hooks/useAuth";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { currentTitle, type AssemblyCurrent } from "../lib/fund-assembly";
import { AssemblyMergeDetails } from "./assembly-merge-details";
import { AssemblyScoreboard } from "./assembly-scoreboard";
import { AssemblyVoteForm } from "./assembly-vote-form";

type AssemblyVoteCardProps = { fund: FundDetails; assembly: AssemblyCurrent };

/** A votação aberta de uma pauta: o placar ao vivo e, a quem tem cotas, o voto. */
export function AssemblyVoteCard({ fund, assembly }: AssemblyVoteCardProps) {
  const { user } = useAuth();
  const { tally } = assembly;
  if (user === null || tally === null) return null;

  const convener = assembly.convener_user_id === user.id ? "você" : assembly.convener_nickname;
  const ends = displayDayMonth(assembly.ends_on);
  const operatorOnFee = assembly.agenda === "FEE_INCREASE" && !assembly.can_vote && fund.my_role !== "viewer";

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-2">
            {currentTitle(assembly)}
            <Badge variant="success" size="tag">
              aberta
            </Badge>
          </span>
        </CardTitle>
        <CardDescription>
          Proposta por {convener} em {displayDayMonth(assembly.called_on)} · fecha em {ends}, pregão {assembly.session}{" "}
          de {assembly.sessions}
        </CardDescription>
        <CardAction>
          <Badge variant="warning" size="tag">
            fecha em {ends}
          </Badge>
        </CardAction>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <AssemblyScoreboard assembly={assembly} tally={tally} />
          {assembly.merge !== null && <AssemblyMergeDetails merge={assembly.merge} />}
          {assembly.can_vote && (
            <AssemblyVoteForm fundId={fund.id} assembly={assembly} myQuotas={fund.assembly.my_quotas} />
          )}
          {operatorOnFee && (
            <p className="text-xs text-muted-foreground">
              O gestor e os co-gestores não votam o aumento da própria taxa: o placar conta só as cotas dos outros
              cotistas.
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
