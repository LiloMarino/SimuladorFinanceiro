import { Check, Clock, X } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { cn } from "@/shared/lib/utils";
import type { CandleChallengeState, ChallengePlayer } from "@/types";
import { isWatching, repliedCount } from "../lib/view";

interface ScoreboardProps {
  state: CandleChallengeState;
  me: string | undefined;
}

/** O placar da rodada: durante a pergunta só mostra quem já respondeu, e o lado de cada um sai na revelação. */
export function Scoreboard({ state, me }: ScoreboardProps) {
  const reveal = state.phase === "reveal" ? state.reveal : null;
  const { replied, playing } = repliedCount(state);
  const watchers = state.players.filter((player) => isWatching(state, player));
  const up = reveal?.votes.filter((vote) => vote.direction === "up").length ?? 0;
  const down = reveal?.votes.filter((vote) => vote.direction === "down").length ?? 0;

  return (
    <aside className="flex flex-col gap-1 border-l bg-subtle px-2.5 py-3.5" aria-label="Placar">
      <div className="flex items-baseline justify-between px-3 pb-1.5">
        <span className="text-[11px] font-semibold tracking-wider text-faint-foreground uppercase">Placar</span>
        <span className="text-xs text-muted-foreground">
          {reveal
            ? `depois da ${state.number}ª`
            : state.phase === "question"
              ? `${replied} de ${playing} responderam`
              : "esperando a primeira"}
        </span>
      </div>

      <ol className="grid gap-1">
        {state.players.map((player) => (
          <Row key={player.nickname} player={player} state={state} mine={player.nickname === me} />
        ))}
      </ol>

      {reveal && (up > 0 || down > 0) && (
        <div className="flex flex-wrap gap-1.5 px-3 pt-2.5">
          {up > 0 && <Badge variant="success">{up === 1 ? "1 disse sobe" : `${up} disseram sobe`}</Badge>}
          {down > 0 && <Badge variant="destructive">{down === 1 ? "1 disse desce" : `${down} disseram desce`}</Badge>}
        </div>
      )}

      <div className="flex-1" />
      {watchers.length > 0 && (
        <p className="mx-3 mt-2 rounded-lg bg-info-soft px-3 py-2 text-xs text-info">
          {watchers.map((player) => player.nickname).join(", ")}{" "}
          {watchers.length === 1 ? "entrou agora e joga" : "entraram agora e jogam"} a partir da próxima pergunta.
        </p>
      )}
      {reveal && watchers.length === 0 && (
        <p className="mx-3 mt-2 text-xs text-muted-foreground">
          Os votos aparecem agora, com o resultado: ✓ e ✗ ao lado de cada nome.
        </p>
      )}
    </aside>
  );
}

function Row({ player, state, mine }: { player: ChallengePlayer; state: CandleChallengeState; mine: boolean }) {
  const watching = isWatching(state, player);
  return (
    <li
      className={cn(
        "grid grid-cols-[18px_28px_minmax(0,1fr)_auto_20px] items-center gap-2 rounded-lg px-3 py-1.5 text-[13px]",
        mine && "bg-info-soft",
      )}
    >
      <span className="font-mono text-xs text-muted-foreground">{player.position}</span>
      <PlayerAvatar nickname={player.nickname} color={player.color} size="sm" />
      <span className="truncate font-medium" title={player.nickname}>
        {player.nickname}
        {mine && <span className="font-normal text-muted-foreground"> (você)</span>}
      </span>
      <span className="font-mono font-semibold">
        {player.hits}
        <span className="font-normal text-muted-foreground"> de {player.answered}</span>
      </span>
      {watching ? <span /> : <Status state={state} player={player} />}
    </li>
  );
}

function Status({ state, player }: { state: CandleChallengeState; player: ChallengePlayer }) {
  if (state.phase === "question") {
    return player.replied ? (
      <Check className="size-4 text-primary" aria-label="respondeu" />
    ) : (
      <Clock className="size-4 text-faint-foreground" aria-label="ainda não respondeu" />
    );
  }
  if (state.phase === "reveal") {
    if (player.last === "hit") return <Check className="size-4 text-success" aria-label="acertou" />;
    if (player.last === "miss") return <X className="size-4 text-destructive" aria-label="errou" />;
  }
  return <span />;
}
