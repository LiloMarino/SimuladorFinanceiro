import { Flag, TriangleAlert } from "lucide-react";
import { PartyMark } from "@/shared/components/party-mark";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import type { Preparations } from "@/types";

const invitesText = (count: number) => `${count} ${count === 1 ? "convite" : "convites"} de vice sem resposta`;

/** O resumo da preparação no cartão da nova partida: partidos, convites pendentes e os conflitos que travam o início. */
export function RoomPreparationSummary({ preparations }: { preparations: Preparations }) {
  const parties = preparations.players.filter((player) => player.kind === "FOUND" && player.party);
  return (
    <>
      <Alert variant="muted">
        <Flag />
        <AlertTitle>
          Preparação da sala: {parties.length} {parties.length === 1 ? "partido" : "partidos"}
        </AlertTitle>
        <AlertDescription>
          <span className="flex flex-wrap items-center gap-1.5">
            {parties.map(
              (player) =>
                player.party && (
                  <PartyMark key={player.nickname} abbr={player.party.abbr} color={player.party.color} size="sm" />
                ),
            )}
            {preparations.pending_invites > 0 &&
              `· ${invitesText(preparations.pending_invites)}, que segue para dentro da partida`}
          </span>
        </AlertDescription>
      </Alert>
      {preparations.conflicts.length > 0 && (
        <Alert variant="destructive">
          <TriangleAlert />
          <AlertTitle>Há partidos em conflito: a partida não inicia</AlertTitle>
          <AlertDescription>
            <ul className="list-disc pl-4">
              {preparations.conflicts.map((conflict) => (
                <li key={conflict}>{conflict}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}
    </>
  );
}

type PendingInvitesStartProps = {
  count: number;
  pending: boolean;
  disabled: boolean;
  onConfirm: () => void;
};

/** O Iniciar com convite de vice sem resposta: avisa que o partido começa sem vice e deixa iniciar mesmo assim. */
export function PendingInvitesStart({ count, pending, disabled, onConfirm }: PendingInvitesStartProps) {
  return (
    <div className="grid gap-2.5">
      <Alert variant="warning">
        <TriangleAlert />
        <AlertTitle>{invitesText(count)}</AlertTitle>
        <AlertDescription>
          Se iniciar agora, o partido começa sem vice. A chapa pode ganhar um vice depois, até a campanha abrir.
        </AlertDescription>
      </Alert>
      <Button size="xl" disabled={disabled} onClick={onConfirm}>
        {pending && <Spinner />}
        Iniciar mesmo assim
      </Button>
    </div>
  );
}
