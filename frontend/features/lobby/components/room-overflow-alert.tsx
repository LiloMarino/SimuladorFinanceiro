import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { joinNames } from "../lib/join-names";

type RoomOverflowAlertProps = {
  /** Quem está na sala, nunca jogou a partida salva e não cabe nas vagas dela */
  names: string[];
};

/** Partida salva que não comporta a sala: diz quem fica sem vaga e o que fazer. */
export function RoomOverflowAlert({ names }: RoomOverflowAlertProps) {
  const single = names.length === 1;
  return (
    <Alert variant="warning">
      <TriangleAlert />
      <AlertTitle>Não cabe quem está na sala</AlertTitle>
      <AlertDescription>
        {joinNames(names)} nunca {single ? "jogou" : "jogaram"} esta partida. {single ? "Ele sai" : "Eles saem"} da sala
        ou você escolhe outra.
      </AlertDescription>
    </Alert>
  );
}
