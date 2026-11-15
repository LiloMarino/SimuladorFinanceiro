import { UserPlus } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { displayIsoDate, displayPercent } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { useAnswerComanagerInvite } from "../hooks/mutations/useAnswerComanagerInvite";
import type { Comanager } from "../lib/fund-comanagers";

type ComanagerInviteAlertProps = {
  fund: FundDetails;
  /** O convite do jogador que consulta a gestora */
  invite: Comanager;
};

/** O convite para co-gestor, com a parte oferecida e o prazo, e os botões de aceitar e recusar. */
export function ComanagerInviteAlert({ fund, invite }: ComanagerInviteAlertProps) {
  const answer = useAnswerComanagerInvite(fund.id);
  const share = Number(invite.pending_share ?? 0);

  return (
    <Alert variant="info">
      <UserPlus />
      <AlertTitle>
        {fund.manager_nickname} convidou você para co-gestor de {fund.name}
      </AlertTitle>
      <AlertDescription>
        <div className="grid gap-3">
          <p>
            Você opera a carteira da gestora e recebe {displayPercent(share, 0)} das taxas a partir do mês seguinte ao
            aceite.
            {invite.expires_on && ` O convite vale até ${displayIsoDate(invite.expires_on)}.`}
          </p>
          <div className="flex flex-wrap gap-2">
            <Button variant="fund" size="sm" disabled={answer.isPending} onClick={() => answer.mutate(true)}>
              {answer.isPending && <Spinner />}
              Aceitar
            </Button>
            <Button variant="outline" size="sm" disabled={answer.isPending} onClick={() => answer.mutate(false)}>
              Recusar
            </Button>
          </div>
        </div>
      </AlertDescription>
    </Alert>
  );
}
