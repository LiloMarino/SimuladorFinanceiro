const STORAGE_KEY = "tutorial";

export type TutorialStyle = "edge-tab" | "menu-item" | "topbar-button" | "off";

export const DEFAULT_TUTORIAL_STYLE: TutorialStyle = "edge-tab";

export interface TutorialState {
  /** Tópicos que o jogador abriu. */
  seen: string[];
  /** Tópicos cujo aviso já foi respondido (Ver tópico, Agora não ou ×). */
  nudged: string[];
  /** A janela já foi aberta alguma vez: o contador do botão deixa de ser azul. */
  opened: boolean;
  style: TutorialStyle;
  /** A aba da borda está recolhida em alça. */
  collapsed: boolean;
}

export const EMPTY_TUTORIAL_STATE: TutorialState = {
  seen: [],
  nudged: [],
  opened: false,
  style: DEFAULT_TUTORIAL_STYLE,
  collapsed: false,
};

const STYLES: readonly TutorialStyle[] = ["edge-tab", "menu-item", "topbar-button", "off"];

const isStringList = (value: unknown): value is string[] =>
  Array.isArray(value) && value.every((item) => typeof item === "string");

/** Lê o que o navegador guardou; campo ausente ou fora do formato volta ao valor inicial. */
export function parseTutorialState(raw: string | null): TutorialState {
  if (!raw) return EMPTY_TUTORIAL_STATE;
  try {
    const data = JSON.parse(raw) as Record<string, unknown>;
    return {
      seen: isStringList(data.seen) ? data.seen : [],
      nudged: isStringList(data.nudged) ? data.nudged : [],
      opened: data.opened === true,
      style: STYLES.find((style) => style === data.style) ?? DEFAULT_TUTORIAL_STYLE,
      collapsed: data.collapsed === true,
    };
  } catch {
    return EMPTY_TUTORIAL_STATE;
  }
}

/** O estado fica no navegador: vale para o jogador em qualquer sala. */
export function loadTutorialState(): TutorialState {
  try {
    return parseTutorialState(localStorage.getItem(STORAGE_KEY));
  } catch {
    return EMPTY_TUTORIAL_STATE;
  }
}

export function saveTutorialState(state: TutorialState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Sem armazenamento (aba privada, dados bloqueados): o progresso só não é lembrado
  }
}

const withId = (ids: string[], id: string) => (ids.includes(id) ? ids : [...ids, id]);

export const markSeen = (state: TutorialState, id: string): TutorialState => ({
  ...state,
  seen: withId(state.seen, id),
});

export const markNudged = (state: TutorialState, id: string): TutorialState => ({
  ...state,
  nudged: withId(state.nudged, id),
});
