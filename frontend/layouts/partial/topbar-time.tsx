import { useCallback, useEffect, useState } from "react";
import { Pause, Play } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { useSetSimulationSpeed } from "@/shared/hooks/mutations/useSetSimulationSpeed";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { displayShortDate } from "@/shared/lib/utils/display";
import type { SimulationState } from "@/types";
import { SpeedPips } from "./speed-pips";
import { TopbarDate } from "./topbar-date";
import { MAX_SPEED, shortcutFor, speedForShortcut } from "./time-shortcuts";

// O motivo da pausa que não foi do jogador, mostrado na dica da data
const PAUSE_REASON_HINTS: Record<NonNullable<SimulationState["pause_reason"]>, string | null> = {
  HOST: null,
  CAMPAIGN_OPENED: "Pausa automática: campanha aberta",
  FIRST_ROUND_RESULT: "Pausa automática: resultado do 1º turno",
  RUNOFF_RESULT: "Pausa automática: resultado do 2º turno",
  IMPEACHMENT: "Pausa automática: impeachment",
};

/** Data, pausa e velocidade da partida, com os atalhos Espaço (pausa) e 1 a 5 (velocidade). */
export function TopbarTime() {
  const { data: simData } = useSimulationState();
  const { mutate: setSpeedApi, isPending: loading } = useSetSimulationSpeed();

  // Velocidade 0 é a pausa; o play retoma na última velocidade escolhida
  const [resumeSpeed, setResumeSpeed] = useState(1);
  const speed = simData?.speed ?? 0;
  const paused = speed === 0;
  const pauseHint = PAUSE_REASON_HINTS[simData?.pause_reason ?? "HOST"];

  // A aba do navegador avisa a pausa para quem está em outra aba
  useEffect(() => {
    if (!paused) return;
    const title = document.title;
    document.title = `⏸ ${title}`;
    return () => {
      document.title = title;
    };
  }, [paused]);

  const changeSpeed = useCallback(
    (newSpeed: number) => {
      if (newSpeed === speed) return;
      setResumeSpeed(newSpeed > 0 ? newSpeed : speed || 1);
      setSpeedApi(newSpeed);
    },
    [speed, setSpeedApi],
  );

  // Atalhos de teclado em toda a tela
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const shortcut = shortcutFor(event);
      if (!shortcut || loading) return;
      event.preventDefault();
      changeSpeed(speedForShortcut(shortcut, speed, resumeSpeed));
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [changeSpeed, loading, speed, resumeSpeed]);

  return (
    <div className="flex items-center gap-2 rounded-lg border border-border bg-subtle p-1">
      <TopbarDate
        date={simData?.current_date ? displayShortDate(simData.current_date) : undefined}
        paused={paused}
        maxSpeed={speed === MAX_SPEED}
        pauseHint={pauseHint}
      />
      <Button
        variant="dark"
        size="icon-sm"
        disabled={loading}
        aria-label={paused ? "Retomar simulação" : "Pausar simulação"}
        onClick={() => changeSpeed(paused ? resumeSpeed : 0)}
      >
        {paused ? <Play /> : <Pause />}
      </Button>
      <SpeedPips speed={speed} resumeSpeed={resumeSpeed} disabled={loading} onChange={changeSpeed} />
    </div>
  );
}
