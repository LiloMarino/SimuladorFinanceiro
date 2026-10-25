import { useEffect, useState } from "react";

/** Fica verdadeiro `ms` depois que a cena `scene` entra, e falso em qualquer outra cena. */
export function useAfter(scene: number, current: number, ms: number) {
  const [reached, setReached] = useState<number | null>(null);

  useEffect(() => {
    if (current !== scene) return;
    const timer = setTimeout(() => setReached(scene), ms);
    return () => clearTimeout(timer);
  }, [scene, current, ms]);

  return reached === scene && current === scene;
}
