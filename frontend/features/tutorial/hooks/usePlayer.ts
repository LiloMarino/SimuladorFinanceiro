import { useEffect, useState } from "react";
import type { HowToTopic } from "../lib/topics";
import { usePrefersReducedMotion } from "@/shared/hooks/usePrefersReducedMotion";

/** Pausa entre o fim de uma volta e o começo da próxima, em segundos. */
const LOOP_PAUSE = 1;

/** Reprodução em loop da animação de um tópico: o trecho em cena é sempre um dos `beats` do tópico. */
export function usePlayer(topic: HowToTopic) {
  const reducedMotion = usePrefersReducedMotion();
  const [beat, setBeat] = useState(0);
  const [playing, setPlaying] = useState(!reducedMotion);
  const { beats, duration } = topic;

  // Cada trecho agenda o seguinte; o último agenda o recomeço depois da pausa
  useEffect(() => {
    const current = beats[beat];
    if (!playing || !current) return;
    const upcoming = beats[beat + 1];
    const seconds = upcoming ? upcoming.start - current.start : duration - current.start + LOOP_PAUSE;
    const timer = setTimeout(() => setBeat(upcoming ? beat + 1 : 0), seconds * 1000);
    return () => clearTimeout(timer);
  }, [beat, playing, beats, duration]);

  return {
    beat,
    step: beats[beat]?.step ?? 0,
    playing,
    toggle: () => setPlaying((current) => !current),
    /** Salta para o primeiro trecho do passo. */
    jumpToStep: (step: number) =>
      setBeat(
        Math.max(
          0,
          beats.findIndex((item) => item.step === step),
        ),
      ),
  };
}

export type Player = ReturnType<typeof usePlayer>;
