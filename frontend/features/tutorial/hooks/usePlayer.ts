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
    if (!playing) return;
    const next = beat + 1;
    const last = next >= beats.length;
    const seconds = last ? duration - beats[beat].start + LOOP_PAUSE : beats[next].start - beats[beat].start;
    const timer = setTimeout(() => setBeat(last ? 0 : next), seconds * 1000);
    return () => clearTimeout(timer);
  }, [beat, playing, beats, duration]);

  return {
    beat,
    step: beats[beat].step,
    playing,
    toggle: () => setPlaying((current) => !current),
    /** Salta para o primeiro trecho do passo. */
    jumpToStep: (step: number) => setBeat(Math.max(0, beats.findIndex((item) => item.step === step))),
  };
}

export type Player = ReturnType<typeof usePlayer>;
