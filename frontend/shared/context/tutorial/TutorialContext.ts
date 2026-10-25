import { createContext } from "react";
import type { TopicId } from "@/shared/lib/tutorial-topic-ids";
import type { TutorialState, TutorialStyle } from "@/shared/lib/tutorial-storage";

export interface TutorialContextValue {
  state: TutorialState;
  isOpen: boolean;
  /** Tópico mostrado na janela. */
  topicId: TopicId;
  /** De onde a janela foi aberta ("dica de Crédito"); ausente quando veio do acesso comum. */
  origin: string | null;
  unseenCount: number;
  /** Abre a janela no tópico pedido; sem pedido, no primeiro que ainda não foi visto. */
  open: (topicId?: TopicId, origin?: string) => void;
  close: () => void;
  select: (topicId: TopicId) => void;
  setStyle: (style: TutorialStyle) => void;
  setCollapsed: (collapsed: boolean) => void;
  /** O aviso da tela foi respondido: não volta a aparecer para o tópico. */
  answerNudge: (topicId: TopicId) => void;
}

export const TutorialContext = createContext<TutorialContextValue | null>(null);
