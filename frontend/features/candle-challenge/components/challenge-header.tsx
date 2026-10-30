import { ChartCandlestick, Flame, Minus, X } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { DialogTitle } from "@/shared/components/ui/dialog";
import type { CandleChallengeState } from "@/types";
import { useCountdown } from "../hooks/useCountdown";
import { secondsLeft } from "../lib/countdown";

interface ChallengeHeaderProps {
  state: CandleChallengeState;
  watching: boolean;
  onMinimize: () => void;
  onClose: () => void;
}

/** A barra da janela: o nome, a pergunta em que está e, na ponta, o que importa na fase. */
export function ChallengeHeader({ state, watching, onMinimize, onClose }: ChallengeHeaderProps) {
  const finished = state.status === "finished";
  return (
    <header className="flex items-center gap-3 border-b px-4 py-3">
      <span className="grid size-8 place-items-center rounded-lg bg-foreground text-background">
        <ChartCandlestick className="size-4" />
      </span>
      <div className="grid min-w-0 flex-1 gap-px">
        <DialogTitle>Desafio da vela</DialogTitle>
        <span className="text-xs text-muted-foreground">
          {finished ? (
            "Rodada terminada"
          ) : (
            <>
              Pergunta de {state.total} · 1 ponto por acerto ·{" "}
              <b className="font-mono text-foreground">{Math.min(state.number, state.total)}</b>
            </>
          )}
        </span>
      </div>
      <Tail state={state} watching={watching} />
      {!finished && (
        <Button variant="ghost" size="icon-sm" aria-label="Minimizar" title="Minimizar" onClick={onMinimize}>
          <Minus />
        </Button>
      )}
      <Button
        variant="ghost"
        size="icon-sm"
        aria-label={finished ? "Fechar" : "Sair do desafio"}
        title={finished ? "Fechar" : "Sair do desafio"}
        onClick={onClose}
      >
        <X />
      </Button>
    </header>
  );
}

function Tail({ state, watching }: { state: CandleChallengeState; watching: boolean }) {
  if (state.phase === "reveal" && state.reveal) {
    return <NextIn key={state.number} remainingMs={state.reveal.remaining_ms} last={state.number >= state.total} />;
  }
  if (watching) return <Badge variant="secondary">Assistindo</Badge>;
  if (state.solo && state.streak > 1) {
    return (
      <Badge variant="warning">
        <Flame />
        {state.streak} seguidas
      </Badge>
    );
  }
  if (state.status === "running" && state.phase === "question") {
    return <span className="hidden text-xs text-muted-foreground lg:inline">Minimize para configurar a partida</span>;
  }
  return null;
}

function NextIn({ remainingMs, last }: { remainingMs: number; last: boolean }) {
  const left = useCountdown(remainingMs);
  return (
    <span className="text-[13px] text-muted-foreground">
      {last ? "Resultado final em" : "Próxima pergunta em"}{" "}
      <b className="font-mono text-foreground">{secondsLeft(left)} s</b>
    </span>
  );
}
