import { describe, expect, it } from "vitest";
import type { News, NewsLevel } from "@/types";
import { INITIAL_PRESENTER, presenterReducer, type PresenterState } from "./presenter";

const news = (id: number, day = "2016-03-14"): News => ({
  id,
  news_date: day,
  news_type: "MEASURE_VOTED",
  headline: `Manchete ${id}`,
  dek: null,
  tickers: [],
});

const arrive = (state: PresenterState, item: News, level: NewsLevel, rank = 0) =>
  presenterReducer(state, { type: "arrived", news: item, level, rank });

describe("presenterReducer", () => {
  it("só mostra os níveis Janela e Jornal", () => {
    expect(arrive(INITIAL_PRESENTER, news(1), "HISTORY_ONLY")).toBe(INITIAL_PRESENTER);
    expect(arrive(INITIAL_PRESENTER, news(1), "OFF")).toBe(INITIAL_PRESENTER);
  });

  it("abre o cartão com a primeira manchete do pregão", () => {
    const state = arrive(INITIAL_PRESENTER, news(1), "JOURNAL", 3);
    expect(state.lead?.news.id).toBe(1);
    expect(state.count).toBe(1);
    expect(state.expanded).toBe(true);
  });

  it("numa rajada sobe a mais importante e conta as outras", () => {
    // Rank menor é o tipo mais importante: a 2ª (rank 1) toma o cartão; a 3ª (rank 5) só entra na contagem
    let state = arrive(INITIAL_PRESENTER, news(1), "JOURNAL", 4);
    state = arrive(state, news(2), "JOURNAL", 1);
    state = arrive(state, news(3), "JOURNAL", 5);
    expect(state.lead?.news.id).toBe(2);
    expect(state.count).toBe(3);
  });

  it("um pregão novo começa outra rajada", () => {
    let state = arrive(INITIAL_PRESENTER, news(1), "JOURNAL", 0);
    state = arrive(state, news(2, "2016-03-15"), "JOURNAL", 6);
    expect(state.lead?.news.id).toBe(2);
    expect(state.count).toBe(1);
  });

  it("a manchete menos importante não reabre o cartão recolhido", () => {
    let state = arrive(INITIAL_PRESENTER, news(1), "JOURNAL", 1);
    state = presenterReducer(state, { type: "collapse" });
    expect(arrive(state, news(2), "JOURNAL", 4).expanded).toBe(false);
    expect(arrive(state, news(3), "JOURNAL", 0).expanded).toBe(true);
  });

  it("abre uma janela por vez: a de outro pregão espera a aberta fechar", () => {
    let state = arrive(INITIAL_PRESENTER, news(1), "WINDOW");
    state = arrive(state, news(2, "2016-03-15"), "WINDOW");
    expect(state.window?.id).toBe(1);
    expect(state.waiting?.id).toBe(2);

    state = presenterReducer(state, { type: "window_closed" });
    expect(state.window?.id).toBe(2);
    expect(state.waiting).toBeNull();
  });

  it("no máximo uma janela por pregão: as outras do mesmo dia vão para o cartão", () => {
    let state = arrive(INITIAL_PRESENTER, news(1), "WINDOW");
    state = arrive(state, news(2), "WINDOW");
    expect(state.window?.id).toBe(1);
    expect(state.waiting).toBeNull();
    expect(state.lead?.news.id).toBe(2);

    // Fechada a janela, outra manchete do mesmo pregão continua sem janela
    state = presenterReducer(state, { type: "window_closed" });
    state = arrive(state, news(3), "WINDOW");
    expect(state.window).toBeNull();
    expect(state.count).toBe(2);
  });
});
