import { Gavel } from "lucide-react";
import { useState } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { useAuth } from "@/shared/hooks/useAuth";
import { displayIsoDate } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { useAnswerAssemblyInvite } from "../hooks/mutations/useAnswerAssemblyInvite";
import { useCancelAssembly } from "../hooks/mutations/useCancelAssembly";
import { blockReason, resultText, type AssemblyCurrent } from "../lib/fund-assembly";
import { AssemblyScoreboard } from "./assembly-scoreboard";
import { ConveneDialog } from "./convene-dialog";
import { FundSection } from "./fund-section";

type FundAssemblyProps = { fund: FundDetails };

/** O convite que espera o aliado: ele aceita ou recusa, e quem convocou pode cancelar. */
function InviteBody({ fundId, current, userId }: { fundId: number; current: AssemblyCurrent; userId: number }) {
  const answer = useAnswerAssemblyInvite(fundId);
  const cancel = useCancelAssembly(fundId);
  const ends = displayIsoDate(current.ends_on);

  if (current.candidate_user_id === userId) {
    return (
      <Alert variant="info">
        <Gavel />
        <AlertTitle>{current.convener_nickname} indica você para a gestão</AlertTitle>
        <AlertDescription>
          <div className="grid gap-3">
            <p>
              Aceitando, a votação abre por 5 pregões e {current.convener_nickname} entra com o voto a favor. Responda
              até {ends}; sem resposta o convite cai como recusa.
            </p>
            <div className="flex flex-wrap gap-2">
              <Button variant="fund" size="sm" disabled={answer.isPending} onClick={() => answer.mutate(true)}>
                {answer.isPending && <Spinner />}
                Aceitar
              </Button>
              <Button
                variant="outline-destructive"
                size="sm"
                disabled={answer.isPending}
                onClick={() => answer.mutate(false)}
              >
                Recusar
              </Button>
            </div>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <p className="text-[13px] text-muted-foreground">
        {current.convener_nickname} convocou a assembleia e indicou {current.candidate_nickname}, que responde até{" "}
        {ends}. A votação abre quando ele aceitar.
      </p>
      {current.convener_user_id === userId && (
        <Button variant="outline" size="sm" disabled={cancel.isPending} onClick={() => cancel.mutate()}>
          {cancel.isPending && <Spinner />}
          Cancelar o convite
        </Button>
      )}
    </div>
  );
}

/** A seção Assembleia da página da gestora: convite, votação ao vivo, último resultado e o botão de convocar. */
export function FundAssembly({ fund }: FundAssemblyProps) {
  const { user } = useAuth();
  const [conveneOpen, setConveneOpen] = useState(false);
  const panel = fund.assembly;
  const current = panel.current;

  if (user === null) return null;
  // A assembleia nasce com a oferta pública; antes dela, e para o gestor sem nada a mostrar, a seção não aparece
  if (current === null && panel.last_result === null && (panel.block === "unlisted" || panel.block === "manager")) {
    return null;
  }

  const reason = blockReason(panel);

  return (
    <FundSection
      title="Assembleia"
      action={
        current === null && panel.block !== "manager" ? (
          <Button variant="outline" size="sm" disabled={!panel.can_convene} onClick={() => setConveneOpen(true)}>
            Convocar assembleia
          </Button>
        ) : undefined
      }
    >
      <div className="grid gap-4">
        {current?.status === "INVITED" && <InviteBody fundId={fund.id} current={current} userId={user.id} />}

        {current?.status === "VOTING" && current.tally !== null && (
          <>
            <div className="flex flex-wrap items-center gap-2 text-[13px]">
              <Badge variant="info" size="tag">
                pregão {current.session} de {current.sessions}
              </Badge>
              <span className="text-muted-foreground">
                {current.convener_nickname} convocou e indica {current.candidate_nickname}. O peso é o das cotas no
                fechamento de {displayIsoDate(current.ends_on)}.
              </span>
            </div>
            <AssemblyScoreboard fundId={fund.id} assembly={current} tally={current.tally} />
          </>
        )}

        {current === null && panel.last_result !== null && (
          <Alert variant={panel.last_result.status === "REPLACED" ? "warning" : "success"}>
            <Gavel />
            <AlertTitle>{panel.last_result.status === "REPLACED" ? "A gestão trocou" : "O gestor ficou"}</AlertTitle>
            <AlertDescription>{resultText(panel.last_result)}</AlertDescription>
          </Alert>
        )}

        {current === null && panel.last_result === null && reason === null && (
          <p className="text-[13px] text-muted-foreground">
            Quem tem 10% das cotas ou mais pode convocar os cotistas para trocar o gestor.
          </p>
        )}
        {current === null && reason !== null && <p className="text-[13px] text-muted-foreground">{reason}</p>}
      </div>

      <ConveneDialog
        open={conveneOpen}
        onOpenChange={setConveneOpen}
        fundId={fund.id}
        fundName={fund.name}
        managerNickname={fund.manager_nickname}
      />
    </FundSection>
  );
}
