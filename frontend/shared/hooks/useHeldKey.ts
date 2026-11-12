import { useEffect, useState } from "react";

/** Verdadeiro enquanto a tecla `key` está segura; soltar a tecla ou sair da janela volta a falso. */
export function useHeldKey(key: string) {
  const [held, setHeld] = useState(false);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => event.key === key && setHeld(true);
    const onKeyUp = (event: KeyboardEvent) => event.key === key && setHeld(false);
    const release = () => setHeld(false);
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    window.addEventListener("blur", release);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
      window.removeEventListener("blur", release);
    };
  }, [key]);

  return held;
}
