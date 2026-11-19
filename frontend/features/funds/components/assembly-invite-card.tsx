import { Gavel } from "lucide-react";
import { FundSection } from "@/shared/components/fund-section";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { useAuth } from "@/shared/hooks/useAuth";
import { displayIsoDate } from "@/shared/lib/utils/display";
import { useAnswerAssemblyInvite } from "../hooks/mutations/useAnswerAssemblyInvite";
import { useCancelAssembly } from "../hooks/mutations/useCancelAssembly";
import { currentTitle, type AssemblyCurrent } from "../lib/fund-assembly";

type AssemblyInviteCardProps = { fundId: number; assembly: AssemblyCurrent };

/** O convite da troca de gestor: o indicado aceita ou recusa, e quem convocou pode cancelar. */
export function AssemblyInviteCard({ fundId, assembly }: AssemblyInviteCardProps) {
  const { user } = useAuth();
  const answer = useAnswerAssemblyInvite(fundId);
  const cancel = useCancelAssembly(fundId);
  if (user === null) return null;

  const ends = displayIsoDate(assembly.ends_on);

  return (
    <FundSection title={currentTitle(assembly)}>
      {assembly.candidate_user_id === user.id ? (
        <Alert variant="info">
          <Gavel />
          <AlertTitle>{assembly.convener_nickname} indica você para a gestão</AlertTitle>
          <AlertDescription>
            <div className="grid gap-3">
              <p>
                Aceitando, a votação abre por 5 pregões e {assembly.convener_nickname} entra com o voto a favor.
                Responda até {ends}; sem resposta o convite cai como recusa.
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
      ) : (
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-[13px] text-muted-foreground">
            {assembly.convener_nickname} convocou a assembleia e indicou {assembly.candidate_nickname}, que responde até{" "}
            {ends}. A votação abre quando ele aceitar.
          </p>
          {assembly.convener_user_id === user.id && (
            <Button variant="outline" size="sm" disabled={cancel.isPending} onClick={() => cancel.mutate()}>
              {cancel.isPending && <Spinner />}
              Cancelar o convite
            </Button>
          )}
        </div>
      )}
    </FundSection>
  );
}
