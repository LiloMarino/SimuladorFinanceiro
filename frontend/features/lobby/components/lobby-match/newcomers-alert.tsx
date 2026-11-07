import { UserPlus } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import type { RoomPlayer } from "@/types";
import { joinNames } from "../../lib/join-names";
import type { SimulationFormValues } from "../../lib/simulation-form";

type NewcomersAlertProps = {
  newcomers: RoomPlayer[];
  inTeams: boolean;
  startingCash: SimulationFormValues["startingCash"];
};

/** Quem nunca jogou a partida selecionada entra ao continuar, com o saldo inicial. */
export function NewcomersAlert({ newcomers, inTeams, startingCash }: NewcomersAlertProps) {
  const single = newcomers.length === 1;

  return (
    <Alert variant="info">
      <UserPlus />
      <AlertTitle>
        {joinNames(newcomers.map((p) => p.nickname))} nunca {single ? "jogou" : "jogaram"} esta partida
      </AlertTitle>
      <AlertDescription>
        {single ? "Entra" : "Entram"} agora, com o saldo inicial de {startingCash} e a cor
        {inTeams && " e a equipe"} que {single ? "escolheu" : "escolheram"}.
        {inTeams && (
          <>
            {" "}
            {single ? "Escolhe" : "Escolhem"} uma equipe antes de entrar. Vale também para quem entra com a partida já
            rodando: a equipe se escolhe na tela de entrada.
          </>
        )}
      </AlertDescription>
    </Alert>
  );
}
