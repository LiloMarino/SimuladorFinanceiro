import { describe, expect, it } from "vitest";
import type { News } from "@/types";
import { pickToday } from "./today";

const item = (id: number, partial: Partial<News>): News => ({
  id,
  news_date: "2030-10-07",
  news_type: "STRONG_MOVE",
  headline: `Manchete ${id}`,
  dek: null,
  tickers: [],
  party_abbrs: [],
  change_pct: null,
  ...partial,
});

const ids = (found: News[]) => found.map((news) => news.id);

describe("pickToday", () => {
  it("põe a maior variação na frente, para cima ou para baixo", () => {
    const found = pickToday([
      item(1, { tickers: ["AAA3"], change_pct: 6.1 }),
      item(2, { tickers: ["BBB3"], change_pct: -9.4 }),
      item(3, { tickers: ["CCC3"], change_pct: 7.3 }),
    ]);

    expect(ids(found)).toEqual([2, 3, 1]);
  });

  it("deixa as sem variação para depois, na ordem em que chegaram", () => {
    const found = pickToday([
      item(1, { news_type: "MEASURE_VOTED" }),
      item(2, { tickers: ["AAA3"], change_pct: 0.4 }),
      item(3, { news_type: "PARTY_LIFE" }),
    ]);

    expect(ids(found)).toEqual([2, 1, 3]);
  });

  it("mantém um ativo só, com a manchete de maior variação", () => {
    const found = pickToday([
      item(1, { news_type: "WEEK_HIGH", tickers: ["VALE3"], change_pct: 2.1 }),
      item(2, { tickers: ["VALE3"], change_pct: -5.9 }),
      item(3, { tickers: ["ITUB4"], change_pct: 5.1 }),
    ]);

    expect(ids(found)).toEqual([2, 3]);
  });

  it("corta em quatro: a grande e as três menores", () => {
    const found = pickToday([1, 2, 3, 4, 5, 6].map((id) => item(id, { tickers: [`T${id}`], change_pct: 10 - id })));

    expect(ids(found)).toEqual([1, 2, 3, 4]);
  });

  it("aceita menos de quatro manchetes e nenhuma", () => {
    expect(ids(pickToday([item(1, {})]))).toEqual([1]);
    expect(pickToday([])).toEqual([]);
  });
});
