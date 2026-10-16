import { useEffect, useRef } from "react";
import { loadColorPreference } from "@/shared/lib/player-color-preference";
import type { RoomPlayer } from "@/types";
import { useChooseColor } from "./useChooseColor";

/**
 * Ao entrar na sala o servidor dá a primeira cor livre; aqui o jogador pede a que
 * escolheu da última vez. Se já tem dono ou a cor está travada, ele fica com a que recebeu.
 */
export function useApplyColorPreference(me: RoomPlayer | undefined, locked: boolean) {
  const { mutate: chooseColor } = useChooseColor();
  const asked = useRef(false);

  useEffect(() => {
    if (!me || asked.current) return;
    asked.current = true;

    const preferred = loadColorPreference();
    if (preferred && preferred !== me.color && !locked) chooseColor(preferred);
  }, [me, locked, chooseColor]);
}
