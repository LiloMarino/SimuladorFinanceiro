import { useEffect, useEffectEvent } from "react";
import { useSetSimulationSpeed } from "@/shared/hooks/mutations/useSetSimulationSpeed";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { countHumans, shouldPause, shouldResume } from "../lib/tutorial-progress";

/**
 * Enquanto o componente que chama este hook existe, a partida fica pausada se o jogador está sozinho
 * entre humanos; ao sair, retoma na velocidade de antes se ninguém mexeu nela nesse meio-tempo.
 */
export function useTutorialPause() {
  const { data: players } = useRoomPlayers();
  const { data: simulation } = useSimulationState();
  const { mutate: setSpeed } = useSetSimulationSpeed();

  const humans = countHumans(players ?? []);
  const speed = simulation?.speed ?? 0;
  const ready = players !== undefined && simulation !== undefined;

  const current = useEffectEvent(() => ({ humans, speed }));
  const change = useEffectEvent(setSpeed);

  // A pausa nasce com a janela e o fim dela devolve a velocidade
  useEffect(() => {
    if (!ready) return;
    const before = current();
    const paused = shouldPause(before.humans, before.speed);
    if (paused) change(0);
    return () => {
      if (shouldResume(paused, current().speed)) change(before.speed);
    };
  }, [ready]);
}
