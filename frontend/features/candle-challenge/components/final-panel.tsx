import { ChartCandlestick, RotateCcw, Trophy } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { cn } from "@/shared/lib/utils";
import { displayShortDate } from "@/shared/lib/utils/display";
import type { CandleChallengeState, ChallengePlayer } from "@/types";
import { displayList } from "@/shared/lib/utils/display";
import { finalBand, ordinal, pointsText } from "../lib/text";
import { MarkDots } from "./mark-dots";

interface FinalPanelProps {
  state: CandleChallengeState;
  me: string | undefined;
  starting: boolean;
  onBack: () => void;
  onPlayAgain: () => void;
}

/** O fim da rodada: o vencedor, o pódio e a linha de cada pergunta; sozinho, a sequência contra o recorde. */
export function FinalPanel({ state, me, starting, onBack, onPlayAgain }: FinalPanelProps) {
  const final = state.final;
  if (!final) return null;
  const mine = state.players.find((player) => player.nickname === me);
  const actions = (
    <span className="flex gap-2">
      <Button variant="outline" onClick={onBack}>
        Voltar ao lobby
      </Button>
      <Button disabled={starting} onClick={onPlayAgain}>
        <RotateCcw />
        Jogar de novo
      </Button>
    </span>
  );

  if (state.solo) {
    const previous = final.previous_record_on ? `, de ${displayShortDate(final.previous_record_on)}` : "";
    const band = finalBand(mine?.hits ?? 0);
    return (
      <div className="grid justify-items-center gap-3 px-6 py-10 text-center">
        <span className="text-[11px] font-semibold tracking-wider text-faint-foreground uppercase">
          Fim das {state.total} perguntas · treino
        </span>
        {/* Só a faixa de leitura afiada comemora */}
        <span
          className={cn(
            "grid size-12 place-items-center rounded-full",
            band.celebrate ? "bg-warning-soft text-warning" : "bg-muted text-muted-foreground",
          )}
        >
          {band.celebrate ? <Trophy className="size-6" /> : <ChartCandlestick className="size-6" />}
        </span>
        <b className="text-2xl">{band.title}</b>
        {mine && <MarkDots marks={mine.marks} total={state.total} />}
        <span className="text-[13px] text-muted-foreground">
          {mine?.hits ?? 0} de {state.total} nesta partida ·{" "}
          {final.new_record
            ? `novo recorde: ${final.best_streak} seguidas`
            : `melhor sequência: ${final.best_streak} seguidas`}
          .{" "}
          {final.previous_record > 0
            ? `O recorde ${final.new_record ? "antigo" : "continua"} ${final.new_record ? "era" : "sendo"} ${final.previous_record} seguidas${previous}.`
            : "É a primeira vez que você joga: esse é o recorde para bater."}
        </span>
        {actions}
      </div>
    );
  }

  const winners = state.players.filter((player) => final.winners.includes(player.nickname));
  const top = winners[0]?.hits ?? 0;

  return (
    <div className="grid gap-5 px-6 py-5">
      <div className="grid gap-1 text-center">
        <span className="text-[11px] font-semibold tracking-wider text-faint-foreground uppercase">
          Fim das {state.total} perguntas
        </span>
        <b className="text-2xl">
          {winners.length === 0
            ? "Ninguém acertou nenhuma"
            : `${displayList(winners.map((w) => w.nickname))} ${winners.length > 1 ? "venceram" : "venceu"} com ${top} de ${state.total}`}
        </b>
        {mine && (
          <span className="text-[13px] text-muted-foreground">
            {winners.length > 1 && final.winners.includes(mine.nickname)
              ? "Empate em acertos divide a vitória: os dois somam uma vitória na sala."
              : `Você ficou em ${ordinal(mine.position)}, com ${pointsText(mine.hits)}.`}
          </span>
        )}
      </div>

      <Podium players={state.players} />

      <Card size="flush">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-10" />
              <TableHead>Jogador</TableHead>
              <TableHead>Pergunta a pergunta</TableHead>
              <TableHead className="text-right">Acertos</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {state.players.map((player) => (
              <TableRow key={player.nickname} variant={player.nickname === me ? "current" : "default"}>
                <TableCell>
                  <span className="font-mono text-muted-foreground">{ordinal(player.position)}</span>
                </TableCell>
                <TableCell>
                  <span className="inline-flex items-center gap-2.5">
                    <PlayerAvatar nickname={player.nickname} color={player.color} size="sm" />
                    <b className="max-w-40 truncate">{player.nickname}</b>
                    {final.winners.includes(player.nickname) && <Badge variant="warning">Venceu</Badge>}
                    {player.joined_at > 1 && (
                      <span className="text-xs text-muted-foreground">· entrou na {player.joined_at}ª</span>
                    )}
                  </span>
                </TableCell>
                <TableCell>
                  <MarkDots marks={player.marks} total={state.total} />
                </TableCell>
                <TableCell className="text-right">
                  <span className="font-mono">
                    <b>{player.hits}</b> <span className="text-muted-foreground">de {player.answered}</span>
                  </span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <span className="text-[13px] text-muted-foreground">
          {state.wins.length > 0 && (
            <>
              Na sala hoje:{" "}
              {state.wins.map((win, index) => (
                <span key={win.nickname}>
                  {index > 0 && " · "}
                  <b className={index === 0 ? "text-foreground" : undefined}>
                    {win.nickname} {win.wins} {win.wins === 1 ? "vitória" : "vitórias"}
                  </b>
                </span>
              ))}
              {" · "}
            </>
          )}
          {state.rounds} {state.rounds === 1 ? "partida" : "partidas"} do desafio
        </span>
        {actions}
      </div>
    </div>
  );
}

/** Os três primeiros, com o segundo à esquerda e o terceiro à direita. */
function Podium({ players }: { players: ChallengePlayer[] }) {
  const place = (position: number) => players.find((player) => player.position === position);
  const order = [place(2), place(1), place(3)];
  const height = ["h-[90px]", "h-[120px]", "h-[70px]"];
  if (!players.some((player) => player.hits > 0)) return null;
  return (
    <div className="flex items-end justify-center gap-4">
      {order.map((player, index) =>
        player ? (
          <div key={player.nickname} className="grid justify-items-center gap-1.5">
            <PlayerAvatar nickname={player.nickname} color={player.color} />
            <b className="max-w-28 truncate">{player.nickname}</b>
            <span className="font-mono text-xs text-muted-foreground">{pointsText(player.hits)}</span>
            <div
              className={cn(
                "flex w-28 items-start justify-center rounded-t-lg bg-muted pt-2.5 text-xl font-bold text-muted-foreground",
                height[index],
                index === 1 && "bg-warning-soft text-warning",
              )}
            >
              {ordinal(player.position)}
            </div>
          </div>
        ) : (
          <div key={index} className="w-28" />
        ),
      )}
    </div>
  );
}
