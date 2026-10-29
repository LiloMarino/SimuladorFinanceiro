import { useEffect, useReducer } from "react";
import type { PropsWithChildren } from "react";
import { useNotificationCatalog } from "@/shared/hooks/queries/useNotificationCatalog";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { rankOf } from "../lib/catalog";
import { levelFor } from "../lib/filter";
import { CARD_MS, INITIAL_PRESENTER, WINDOW_MS, presenterReducer } from "../lib/presenter";
import { NewsPresenterContext } from "./NewsPresenterContext";

/**
 * Dono da manchete que está na tela: cada manchete nova passa pelo nível que o jogador deu ao
 * tipo dela (janela, jornal, só no histórico ou desligado) e vira janela, cartão ou nada.
 */
export function NewsPresenterProvider({ children }: PropsWithChildren) {
  const [state, dispatch] = useReducer(presenterReducer, INITIAL_PRESENTER);
  const { preferences } = useNotificationPreferences();
  const { data: catalog } = useNotificationCatalog();
  const { data: portfolio } = usePortfolio();
  const held = new Set((portfolio?.variable_income ?? []).map((position) => position.ticker));

  useRealtime("news_published", (news) => {
    const chosen = preferences?.news[news.news_type];
    if (!chosen || !catalog) return;
    const level = levelFor(chosen, preferences.news_held_only[news.news_type] ?? false, news.tickers, held);
    dispatch({ type: "arrived", news, level, rank: rankOf(catalog, news.news_type) });
  });

  // O cartão recolhe no selo CARD_MS depois da última manchete que o abriu
  useEffect(() => {
    if (!state.expanded) return;
    const timer = setTimeout(() => dispatch({ type: "collapse" }), CARD_MS);
    return () => clearTimeout(timer);
  }, [state.expanded, state.lead, state.count]);

  // A janela fecha sozinha; a que esperava a vez abre em seguida
  useEffect(() => {
    if (state.window === null) return;
    const timer = setTimeout(() => dispatch({ type: "window_closed" }), WINDOW_MS);
    return () => clearTimeout(timer);
  }, [state.window]);

  return (
    <NewsPresenterContext.Provider
      value={{
        state,
        position: preferences?.news_position,
        closeWindow: () => dispatch({ type: "window_closed" }),
      }}
    >
      {children}
    </NewsPresenterContext.Provider>
  );
}
