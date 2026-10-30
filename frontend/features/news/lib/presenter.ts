import type { News, NewsLevel } from "@/types";

/** O cartão recolhe no selo depois deste tempo. */
export const CARD_MS = 6000;
/** A janela fecha sozinha depois deste tempo. */
export const WINDOW_MS = 8000;

/** Uma manchete com a posição do tipo dela no registro: quanto menor, mais importante. */
type Ranked = { news: News; rank: number };

export type PresenterState = {
  /** O pregão (data do jogo) da rajada em andamento */
  day: string | null;
  /** A manchete do cartão: a mais importante do pregão */
  lead: Ranked | null;
  /** Quantas manchetes do cartão chegaram neste pregão, a do cartão inclusive */
  count: number;
  /** Cartão aberto; recolhido, só o selo fica no canto */
  expanded: boolean;
  /** A janela aberta e a que espera ela fechar */
  window: News | null;
  waiting: News | null;
  /** O pregão da última janela que abriu ou entrou na espera */
  windowDay: string | null;
};

export type PresenterAction =
  | { type: "arrived"; news: News; level: NewsLevel; rank: number }
  | { type: "collapse" }
  | { type: "window_closed" };

export const INITIAL_PRESENTER: PresenterState = {
  day: null,
  lead: null,
  count: 0,
  expanded: false,
  window: null,
  waiting: null,
  windowDay: null,
};

/**
 * Janela, cartão ou nada, conforme o nível do tipo. Cada pregão tem no máximo uma janela: a
 * primeira manchete de nível Janela do pregão abre (ou espera a janela de um pregão anterior
 * fechar) e as outras do mesmo pregão vão para o cartão. No cartão, cada pregão é uma rajada: sobe
 * a manchete mais importante, e as outras entram na contagem "+N neste pregão".
 */
export function presenterReducer(state: PresenterState, action: PresenterAction): PresenterState {
  switch (action.type) {
    case "arrived": {
      const { news, level, rank } = action;
      if (level !== "WINDOW" && level !== "JOURNAL") return state;

      if (level === "WINDOW" && state.windowDay !== news.news_date) {
        if (state.window === null) return { ...state, window: news, windowDay: news.news_date };
        if (state.waiting === null) return { ...state, waiting: news, windowDay: news.news_date };
      }

      if (state.day !== news.news_date) {
        return { ...state, day: news.news_date, lead: { news, rank }, count: 1, expanded: true };
      }
      const outranks = state.lead === null || rank < state.lead.rank;
      return {
        ...state,
        lead: outranks ? { news, rank } : state.lead,
        count: state.count + 1,
        expanded: state.expanded || outranks,
      };
    }
    case "collapse":
      return { ...state, expanded: false };
    case "window_closed":
      return { ...state, window: state.waiting, waiting: null };
  }
}
