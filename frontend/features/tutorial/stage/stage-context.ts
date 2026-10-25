import { createContext, useContext, type RefObject } from "react";

export interface StageContextValue {
  /** Raiz do palco, no tamanho de projeto: as medidas do cursor partem dela. */
  root: RefObject<HTMLDivElement | null>;
  /** Escala aplicada ao palco para caber na ilustração. */
  scale: number;
}

export const StageContext = createContext<StageContextValue | null>(null);

export function useStage() {
  const ctx = useContext(StageContext);
  if (!ctx) throw new Error("useStage must be used within TutorialStage");
  return ctx;
}
