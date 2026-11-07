import { ChartCandlestick, Play } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Spinner } from "@/shared/components/ui/spinner";
import type { CandleChallengeState } from "@/types";

interface ChallengeInviteProps {
  state: CandleChallengeState;
  joining: boolean;
  onJoin: () => void;
  onDecline: () => void;
}

/** O convite do lobby para quem ainda não entrou na rodada que alguém começou. */
export function ChallengeInvite({ state, joining, onJoin, onDecline }: ChallengeInviteProps) {
  const starter = state.players.find((player) => player.nickname === state.starter) ?? state.players[0];
  return (
    <Card size="sm" variant="info">
      <CardContent>
        <div className="grid grid-cols-[auto_1fr_auto_auto] items-center gap-3">
          <PlayerAvatar nickname={state.starter ?? "?"} color={starter?.color} />
          <div className="grid gap-0.5">
            <b>{state.starter} começou o Desafio da vela</b>
            <span className="text-[13px] text-muted-foreground">
              Pergunta {Math.min(state.number || 1, state.total)} de {state.total} · {state.players.length} jogando
            </span>
          </div>
          <Button variant="ghost" size="sm" onClick={onDecline}>
            Agora não
          </Button>
          <Button disabled={joining} onClick={onJoin}>
            {joining && <Spinner />}
            Entrar
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

/** O cartão do lobby quando ninguém joga: qualquer um pode começar. */
export function ChallengeStart({ starting, onStart }: { starting: boolean; onStart: () => void }) {
  return (
    <Card size="sm">
      <CardContent>
        <div className="grid grid-cols-[auto_1fr_auto] items-center gap-3.5">
          <span className="grid size-11 place-items-center rounded-xl bg-foreground text-background">
            <ChartCandlestick className="size-5" />
          </span>
          <div className="grid gap-0.5">
            <b>Desafio da vela</b>
            <span className="text-[13px] text-muted-foreground">
              10 perguntas de sobe ou desce com velas de verdade, enquanto a partida não começa. Todo mundo responde ao
              mesmo tempo.
            </span>
          </div>
          <Button disabled={starting} onClick={onStart}>
            {starting ? <Spinner /> : <Play />}
            Começar
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
