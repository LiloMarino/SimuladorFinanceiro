import { useState } from "react";
import { CardState } from "@/shared/components/card-state";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useAuth } from "@/shared/hooks/useAuth";
import { useCandleChallenge, useCandleChallengeSync } from "../hooks/queries/useCandleChallenge";
import { useCandleChallengeNotices } from "../hooks/useCandleChallengeNotices";
import { useAnswerCandleChallenge } from "../hooks/mutations/useAnswerCandleChallenge";
import { useJoinCandleChallenge } from "../hooks/mutations/useJoinCandleChallenge";
import { useLeaveCandleChallenge } from "../hooks/mutations/useLeaveCandleChallenge";
import { useStartCandleChallenge } from "../hooks/mutations/useStartCandleChallenge";
import { findPlayer, windowMode, type WindowChoice, type WindowMode } from "../lib/view";
import { ChallengeDock } from "./challenge-dock";
import { ChallengeInvite, ChallengeStart } from "./challenge-launcher";
import { ChallengeWindow } from "./challenge-window";

/**
 * O desafio da vela no lobby: o cartão para começar ou entrar, a janela de atividade e o
 * cartão no canto quando ela está recolhida. A janela abre sozinha para quem está na rodada.
 */
export function CandleChallenge() {
  const { user } = useAuth();
  const me = user?.nickname;
  useCandleChallengeSync();
  useCandleChallengeNotices();

  const query = useCandleChallenge();
  const start = useStartCandleChallenge();
  const join = useJoinCandleChallenge();
  const leave = useLeaveCandleChallenge();
  const answer = useAnswerCandleChallenge();
  const [choice, setChoice] = useState<WindowChoice | null>(null);

  if (!query.data) {
    return (
      <CardState
        label="Carregando o desafio da vela"
        error={query.error}
        onRetry={() => void query.refetch()}
        errorTitle="Não deu para carregar o desafio"
      >
        <div className="grid grid-cols-[auto_1fr_auto] items-center gap-3.5">
          <Skeleton className="size-11" />
          <div className="grid gap-1.5">
            <Skeleton className="h-4 w-40" />
            <Skeleton className="h-3.5 w-full max-w-md" />
          </div>
          <Skeleton className="h-9 w-24" />
        </div>
      </CardState>
    );
  }
  const { state, direction } = query.data;
  const joined = !!findPlayer(state, me);
  const mode = windowMode(choice, state);
  const choose = (next: WindowMode) => setChoice({ round: state.round_id, mode: next });
  const vote = (side: "up" | "down") => answer.mutate(side);

  if (joined && state.status !== "idle") {
    if (mode === "open") {
      return (
        <ChallengeWindow
          state={state}
          direction={direction}
          me={me}
          error={query.isError ? query.error : null}
          starting={start.isPending}
          onVote={vote}
          onMinimize={() => choose("minimized")}
          onClose={() => {
            if (state.status === "running") leave.mutate();
            choose("closed");
          }}
          onPlayAgain={() => start.mutate()}
          onRetry={() => void query.refetch()}
        />
      );
    }
    if (mode === "minimized") {
      return <ChallengeDock state={state} direction={direction} me={me} onVote={vote} onOpen={() => choose("open")} />;
    }
  }

  if (state.status === "running" && !joined) {
    if (mode === "declined") return null;
    return (
      <ChallengeInvite
        state={state}
        joining={join.isPending}
        onJoin={() => join.mutate(undefined, { onSuccess: () => choose("open") })}
        onDecline={() => choose("declined")}
      />
    );
  }
  if (state.status === "running") return null;

  return <ChallengeStart starting={start.isPending} onStart={() => start.mutate()} />;
}
