import { useEffect, useState } from "react";
import type { TimelinePoint } from "@/types";

/** O tempo de cada ponto na reprodução. */
const STEP_MS = 1000;

// O ponto a `delta` passos do atual, preso entre o primeiro e o hoje
function pointAround(points: TimelinePoint[], index: number, delta: number, todayIndex: number) {
  return points[Math.min(Math.max(index + delta, 0), todayIndex)];
}

type PlaybackInput = {
  points: TimelinePoint[];
  selectedIndex: number;
  /** O índice do último ponto que já aconteceu: a reprodução para nele. */
  todayIndex: number;
  /** Só com a régua à vista o teclado e a reprodução andam. */
  enabled: boolean;
  onSelect: (point: TimelinePoint) => void;
};

/** A reprodução da régua e as setas do teclado: um ponto por segundo até o hoje; as setas pausam. */
export function useTimelinePlayback({ points, selectedIndex, todayIndex, enabled, onSelect }: PlaybackInput) {
  const [playing, setPlaying] = useState(false);
  const active = playing && enabled;

  // Cada ponto dura STEP_MS e o seguinte agenda o próximo: a régua anda até o hoje e para
  useEffect(() => {
    if (!active) return;
    const timer = setTimeout(() => {
      const next = points[selectedIndex + 1];
      if (next) onSelect(next);
      if (selectedIndex + 1 >= todayIndex) setPlaying(false);
    }, STEP_MS);
    return () => clearTimeout(timer);
  }, [active, points, selectedIndex, todayIndex, onSelect]);

  const step = (delta: number) => {
    setPlaying(false);
    const target = pointAround(points, selectedIndex, delta, todayIndex);
    if (target) onSelect(target);
  };

  // As setas ← e → andam a régua e pausam a reprodução; as setas do seletor de ano ficam com ele
  useEffect(() => {
    if (!enabled) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      if (event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) return;
      const origin = event.target;
      if (
        origin instanceof HTMLElement &&
        origin.closest("input, textarea, select, [contenteditable], [data-own-arrows]")
      ) {
        return;
      }
      event.preventDefault();
      setPlaying(false);
      const target = pointAround(points, selectedIndex, event.key === "ArrowLeft" ? -1 : 1, todayIndex);
      if (target) onSelect(target);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [enabled, points, selectedIndex, todayIndex, onSelect]);

  const toggle = () => {
    if (active) {
      setPlaying(false);
      return;
    }
    // Começando do hoje, a reprodução recomeça do primeiro ponto
    if (selectedIndex >= todayIndex && points[0]) onSelect(points[0]);
    setPlaying(true);
  };

  return {
    playing: active,
    toggle,
    pause: () => setPlaying(false),
    previous: () => step(-1),
    next: () => step(1),
  };
}
