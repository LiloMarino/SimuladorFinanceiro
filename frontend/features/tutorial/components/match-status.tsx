import { Clock, Pause } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { displayShortDate } from "@/shared/lib/utils/display";
import { useTutorialPause } from "../hooks/useTutorialPause";
import { countHumans } from "../lib/tutorial-progress";

/** Pausa a partida enquanto a janela está aberta e o jogador está sozinho; não desenha nada. */
export function MatchPause() {
  useTutorialPause();
  return null;
}

/** Quem está na sala, em uma frase para o cabeçalho. */
export function MatchSubtitle() {
  const { data: players } = useRoomPlayers();
  const humans = countHumans(players ?? []);
  return humans > 1 ? `${humans} jogadores na sala` : "Você está sozinho na sala";
}

/** O que acontece com o tempo enquanto a janela está aberta, e a data da partida. */
export function MatchStatus() {
  const { data: players } = useRoomPlayers();
  const { data: simulation } = useSimulationState();
  const alone = countHumans(players ?? []) <= 1;

  return (
    <>
      {alone ? (
        <Badge variant="info">
          <Pause />
          Partida pausada até você fechar
        </Badge>
      ) : (
        <Badge variant="warning">
          <Clock />
          O tempo continua correndo
        </Badge>
      )}
      <span className="font-mono text-[13px] text-muted-foreground">
        {simulation?.current_date ? displayShortDate(simulation.current_date) : "—"}
      </span>
    </>
  );
}
