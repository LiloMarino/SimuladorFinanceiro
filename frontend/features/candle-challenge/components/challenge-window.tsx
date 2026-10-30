import { useEffect } from "react";
import { Dialog, DialogContent } from "@/shared/components/ui/dialog";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ErrorState } from "@/shared/components/error-state";
import { cn } from "@/shared/lib/utils";
import type ApiError from "@/shared/lib/models/ApiError";
import type { CandleChallengeState, ChallengeDirection } from "@/types";
import { findPlayer, isWatching } from "../lib/view";
import { ChallengeHeader } from "./challenge-header";
import { FinalPanel } from "./final-panel";
import { QuestionPanel } from "./question-panel";
import { RevealPanel } from "./reveal-panel";
import { Scoreboard } from "./scoreboard";

interface ChallengeWindowProps {
  state: CandleChallengeState;
  direction: ChallengeDirection | null;
  me: string | undefined;
  /** A consulta falhou: a janela avisa que a conexão caiu e oferece tentar de novo. */
  error: ApiError | null;
  starting: boolean;
  onVote: (direction: ChallengeDirection) => void;
  onMinimize: () => void;
  onClose: () => void;
  onPlayAgain: () => void;
  onRetry: () => void;
}

/** A janela de atividade: abre por cima do lobby, com o palco da pergunta e o placar ao lado. */
export function ChallengeWindow({
  state,
  direction,
  me,
  error,
  starting,
  onVote,
  onMinimize,
  onClose,
  onPlayAgain,
  onRetry,
}: ChallengeWindowProps) {
  const player = findPlayer(state, me);
  const watching = isWatching(state, player);
  const finished = state.status === "finished";
  const canVote = state.phase === "question" && !watching && !!player;

  // ↑ responde sobe e ↓ responde desce, sem precisar do mouse
  useEffect(() => {
    if (!canVote || error) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "ArrowUp") onVote("up");
      else if (event.key === "ArrowDown") onVote("down");
      else return;
      event.preventDefault();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [canVote, error, onVote]);

  const myVote = state.reveal?.votes.find((vote) => vote.nickname === me)?.direction;

  return (
    <Dialog open onOpenChange={(open) => !open && (finished ? onClose() : onMinimize())}>
      <DialogContent
        flush
        showCloseButton={false}
        aria-describedby={undefined}
        className={cn(
          "top-15 max-h-[calc(100svh-4rem)] translate-y-0 overflow-y-auto",
          finished ? "sm:max-w-225" : "sm:max-w-280",
        )}
      >
        <ChallengeHeader state={state} watching={watching} onMinimize={onMinimize} onClose={onClose} />
        {error ? (
          <ErrorState
            title="Perdemos a conexão com o desafio"
            description="Sua resposta da pergunta atual pode não ter chegado. O desafio segue para os outros; ao voltar, você entra na próxima pergunta."
            error={error}
            onRetry={onRetry}
          />
        ) : finished ? (
          <FinalPanel state={state} me={me} starting={starting} onBack={onClose} onPlayAgain={onPlayAgain} />
        ) : (
          <div className={cn("grid", !state.solo && "grid-cols-[minmax(0,1fr)_300px]")}>
            <div className="px-6 py-5">
              {state.phase === "question" ? (
                <QuestionPanel state={state} me={player} direction={direction} onVote={onVote} />
              ) : state.phase === "reveal" ? (
                <RevealPanel state={state} me={player} myVote={myVote} />
              ) : (
                <WindowSkeleton />
              )}
            </div>
            {!state.solo && <Scoreboard state={state} me={me} />}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

/** O formato do palco enquanto chega a primeira pergunta. */
function WindowSkeleton() {
  return (
    <div className="grid gap-4" aria-busy aria-label="Buscando a primeira pergunta">
      <Skeleton className="h-6 w-4/5" />
      <div className="flex h-[380px] items-end gap-1.5 rounded-xl border p-3">
        {Array.from({ length: 30 }, (_, index) => (
          <Skeleton key={index} className="flex-1" style={{ height: `${25 + ((index * 37) % 55)}%` }} />
        ))}
      </div>
      <div className="flex gap-3">
        <Skeleton className="h-14 flex-1" />
        <Skeleton className="h-14 flex-1" />
      </div>
    </div>
  );
}
