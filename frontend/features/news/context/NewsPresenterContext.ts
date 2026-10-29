import { createContext } from "react";
import type { NewsPosition } from "@/types";
import type { PresenterState } from "../lib/presenter";

export type NewsPresenterContextType = {
  state: PresenterState;
  /** Onde o jogador escolheu ver o jornal; indefinido enquanto as configurações não chegaram */
  position: NewsPosition | undefined;
  closeWindow: () => void;
};

export const NewsPresenterContext = createContext<NewsPresenterContextType | null>(null);
