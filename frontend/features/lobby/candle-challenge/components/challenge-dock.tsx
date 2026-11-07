import { ChartCandlestick, Maximize2 } from "lucide-react";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displaySignedPercent } from "@/shared/lib/utils/display";
import type { CandleChallengeState, ChallengeDirection } from "@/types";
import { useCountdown } from "../hooks/useCountdown";
import { secondsLeft } from "../lib/countdown";
import { ordinal } from "../lib/text";
import { findPlayer, isWatching } from "../lib/view";
import { VoteButtons } from "./vote-buttons";

interface ChallengeDockProps {
  state: CandleChallengeState;
  direction: ChallengeDirection | null;
  me: string | undefined;
  onVote: (direction: ChallengeDirection) => void;
  onOpen: () => void;
}

/** A janela recolhida num cartão no canto: dá para responder sem abrir. */
export function ChallengeDock({ state, direction, me, onVote, onOpen }: ChallengeDockProps) {
  const player = findPlayer(state, me);
  const watching = isWatching(state, player);
  const question = state.phase === "question" ? state.question : null;
  const reveal = state.phase === "reveal" ? state.reveal : null;

  return (
    <div className="fixed right-4 bottom-4 z-40 w-80 rounded-xl shadow-lg" role="region" aria-label="Desafio da vela">
      <Card size="sm">
        <CardContent>
          <div className="grid gap-2">
            <div className="flex items-center gap-2">
              <ChartCandlestick className="size-4 text-muted-foreground" />
              <b className="flex-1 text-[13px]">
                {state.status === "finished"
                  ? "Desafio da vela terminou"
                  : `Pergunta ${Math.min(state.number, state.total)} de ${state.total}`}
              </b>
              {question && <DockTime key={question.id} remainingMs={question.remaining_ms} />}
              <button
                type="button"
                onClick={onOpen}
                className="grid size-6 place-items-center rounded-md text-muted-foreground hover:bg-muted"
                aria-label="Abrir o desafio"
              >
                <Maximize2 className="size-3.5" />
              </button>
            </div>
            {question && <VoteButtons compact direction={direction} disabled={watching || !player} onVote={onVote} />}
            {reveal && (
              <span className="text-[13px]">
                {reveal.outcome === "void"
                  ? "Pergunta anulada: ficou no mesmo preço."
                  : `${reveal.outcome === "up" ? "Subiu" : "Desceu"} ${displaySignedPercent(reveal.change, 1)}${player?.last === "hit" ? " · você acertou" : player?.last === "miss" ? " · você errou" : ""}`}
              </span>
            )}
            <button
              type="button"
              onClick={onOpen}
              className="text-left text-xs text-muted-foreground hover:text-foreground"
            >
              {player && !state.solo
                ? `Você ${ordinal(player.position)} · ${player.hits} de ${player.answered} · `
                : ""}
              clique para abrir
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function DockTime({ remainingMs }: { remainingMs: number }) {
  const left = useCountdown(remainingMs);
  return <b className="font-mono text-[13px] text-primary">{secondsLeft(left)} s</b>;
}
