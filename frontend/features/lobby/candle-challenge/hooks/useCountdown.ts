import { useEffect, useState } from "react";

const TICK_MS = 100;

/**
 * Quanto falta, em ms, contando do instante em que o servidor mediu. O relógio é do
 * servidor: a tela só desconta o tempo que passou desde que a mensagem chegou. Quem
 * usa dá `key` à pergunta, e cada pergunta começa um relógio novo.
 */
export function useCountdown(remainingMs: number) {
  const [left, setLeft] = useState(remainingMs);

  useEffect(() => {
    const deadline = performance.now() + remainingMs;
    const timer = window.setInterval(() => setLeft(Math.max(0, deadline - performance.now())), TICK_MS);
    return () => window.clearInterval(timer);
  }, [remainingMs]);

  return left;
}
