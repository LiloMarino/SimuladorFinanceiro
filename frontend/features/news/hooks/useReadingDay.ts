import { type RefObject, useEffect, useState } from "react";
import { readingDay } from "../lib/reading";

/** A folga abaixo do topo fixo: o dia conta como lido quando o título dele chega a esta distância. */
const READING_GAP = 24;

/**
 * O dia em leitura dentro do contêiner, pelos `[data-day]` dele.
 * Recalcula ao rolar, ao redimensionar e quando a lista muda de altura (mês novo carregado ou filtro).
 */
export function useReadingDay(containerRef: RefObject<HTMLElement | null>) {
  const [day, setDay] = useState<string | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let frame = 0;
    const measure = () => {
      frame = 0;
      const topbar = Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--topbar-height"));
      const sections = Array.from(container.querySelectorAll<HTMLElement>("[data-day]"), (element) => ({
        day: element.dataset.day ?? "",
        top: element.getBoundingClientRect().top,
      }));
      setDay(readingDay(sections, (Number.isNaN(topbar) ? 0 : topbar) + READING_GAP));
    };
    const schedule = () => {
      if (!frame) frame = requestAnimationFrame(measure);
    };

    // A captura no documento ouve a rolagem de qualquer contêiner: quem rola é o miolo do layout, e não a janela
    schedule();
    document.addEventListener("scroll", schedule, { capture: true, passive: true });
    window.addEventListener("resize", schedule);
    const observer = new ResizeObserver(schedule);
    observer.observe(container);
    return () => {
      cancelAnimationFrame(frame);
      document.removeEventListener("scroll", schedule, { capture: true });
      window.removeEventListener("resize", schedule);
      observer.disconnect();
    };
  }, [containerRef]);

  return day;
}
