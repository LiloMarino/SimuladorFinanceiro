import { Clock, History, Play, RefreshCw, Zap } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { ChallengeStartWarning } from "@/features/lobby/candle-challenge/components/challenge-start-warning";
import { PendingInvitesStart } from "../preparation/room-preparation";

type ContinueActionsProps = {
  simulationName: string;
  /** A pergunta do desafio da vela em andamento; nula quando não há desafio */
  challengeQuestion: number | null;
  continuing: boolean;
  busy: boolean;
  disabled: boolean;
  onContinue: () => void;
  onOpenSaved: () => void;
};

/** O host com uma partida salva selecionada: continuar ou trocar de partida. */
export function ContinueActions({
  simulationName,
  challengeQuestion,
  continuing,
  busy,
  disabled,
  onContinue,
  onOpenSaved,
}: ContinueActionsProps) {
  return (
    <div className="grid gap-2">
      {challengeQuestion !== null ? (
        <ChallengeStartWarning
          question={challengeQuestion}
          pending={continuing}
          disabled={disabled}
          onConfirm={onContinue}
        />
      ) : (
        <Button size="xl" className="min-w-0" disabled={disabled} onClick={onContinue}>
          {continuing ? <Spinner /> : <Play />}
          <span className="min-w-0 truncate">Continuar {simulationName}</span>
        </Button>
      )}
      <Button variant="outline" disabled={busy} onClick={onOpenSaved}>
        <RefreshCw />
        Trocar partida
      </Button>
    </div>
  );
}

type NewGameActionsProps = {
  /** A pergunta do desafio da vela em andamento; nula quando não há desafio */
  challengeQuestion: number | null;
  creating: boolean;
  busy: boolean;
  canStart: boolean;
  /** Convites de partido sem resposta; zero quando a expansão do governo está desligada */
  pendingInvites: number;
  hasSavedSimulations: boolean;
  onCreate: () => void;
  onOpenSaved: () => void;
};

/** O host de uma partida nova: iniciar, com o aviso que pede confirmação, ou escolher uma salva. */
export function NewGameActions({
  challengeQuestion,
  creating,
  busy,
  canStart,
  pendingInvites,
  hasSavedSimulations,
  onCreate,
  onOpenSaved,
}: NewGameActionsProps) {
  return (
    <>
      {challengeQuestion !== null ? (
        <ChallengeStartWarning
          question={challengeQuestion}
          pending={creating}
          disabled={!canStart}
          onConfirm={onCreate}
        />
      ) : pendingInvites > 0 ? (
        <PendingInvitesStart count={pendingInvites} pending={creating} disabled={!canStart} onConfirm={onCreate} />
      ) : (
        <Button size="xl" disabled={!canStart} onClick={onCreate}>
          {creating ? <Spinner /> : <Zap />}
          Iniciar nova simulação
        </Button>
      )}
      {/* Sem partida salva não há o que escolher */}
      {hasSavedSimulations && (
        <Button variant="outline" disabled={busy} onClick={onOpenSaved}>
          <History />
          Escolher partida salva
        </Button>
      )}
    </>
  );
}

type WaitingForHostProps = {
  hostNickname: string;
  /** Nome da partida salva selecionada; ausente quando a partida é nova */
  simulationName: string | undefined;
};

/** Quem não é host espera o início ou a continuação. */
export function WaitingForHost({ hostNickname, simulationName }: WaitingForHostProps) {
  return (
    <div className="flex items-center justify-center gap-2 rounded-[10px] bg-background px-4 py-3.5 text-muted-foreground">
      <Clock className="size-4" />
      {simulationName ? `Esperando ${hostNickname} continuar ${simulationName}` : `Esperando ${hostNickname} iniciar`}
    </div>
  );
}
