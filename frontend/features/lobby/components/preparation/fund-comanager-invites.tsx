import { useState } from "react";
import { CircleAlert, Info, Lock, Mail, UserCheck } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import type { MyPreparation } from "@/types";
import { useAnswerFundComanager } from "../../hooks/mutations/useAnswerFundComanager";
import { sharePercent } from "../../lib/fund-comanagers";

type FundComanagerInvitesProps = {
  invites: MyPreparation["fund_comanager_invites"];
  /** Por que aceitar está travado; nulo quando o jogador pode aceitar */
  acceptLock: string | null;
  /** Cada jogador fica em um grupo só: aceitar convite tira a gestora própria */
  exclusiveGroups: boolean;
};

/** Os convites de co-gestão que o jogador recebeu: aceitar ou recusar, e a confirmação dos que aceitou. */
export function FundComanagerInvites({ invites, acceptLock, exclusiveGroups }: FundComanagerInvitesProps) {
  const answer = useAnswerFundComanager();
  const [refusal, setRefusal] = useState<string | null>(null);
  const pending = invites.filter((invite) => !invite.accepted);
  const accepted = invites.filter((invite) => invite.accepted);

  const respond = (owner: string, accept: boolean) => {
    setRefusal(null);
    answer.mutate({ owner, accept }, { onError: (err) => setRefusal(err.message) });
  };

  return (
    <>
      {/* Convites sem resposta */}
      {pending.map((invite) => (
        <Alert key={invite.owner} variant="fund">
          <Mail />
          <AlertTitle>
            {invite.owner} te convidou para co-gestora da {invite.fund_name}, com {sharePercent(invite.share)} das
            taxas.
          </AlertTitle>
          <AlertDescription>
            Você opera a carteira da gestora junto com ela e segue com a sua própria preparação.
          </AlertDescription>
          <AlertAction>
            <div className="flex items-center gap-2">
              <Button
                type="button"
                size="sm"
                variant="fund"
                disabled={answer.isPending || acceptLock !== null}
                onClick={() => respond(invite.owner, true)}
              >
                Aceitar
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                disabled={answer.isPending}
                onClick={() => respond(invite.owner, false)}
              >
                Recusar
              </Button>
            </div>
          </AlertAction>
        </Alert>
      ))}
      {pending.length > 0 && acceptLock !== null && (
        <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Lock className="size-3.5" /> {acceptLock}
        </p>
      )}
      {pending.length > 0 && acceptLock === null && (
        <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Info className="size-3.5" />
          {exclusiveGroups
            ? "Aceitar te põe na equipe dessa gestora: quem está num grupo não funda outra."
            : "Aceitar não impede fundar a sua própria gestora"}
        </p>
      )}

      {/* Convites aceitos */}
      {accepted.map((invite) => (
        <Alert key={invite.owner} variant="success">
          <UserCheck />
          <AlertDescription>
            Você começa como co-gestor da {invite.fund_name}, de {invite.owner}, com {sharePercent(invite.share)} das
            taxas.
          </AlertDescription>
        </Alert>
      ))}
      {refusal && (
        <Alert variant="destructive">
          <CircleAlert />
          <AlertDescription>{refusal}</AlertDescription>
        </Alert>
      )}
    </>
  );
}
