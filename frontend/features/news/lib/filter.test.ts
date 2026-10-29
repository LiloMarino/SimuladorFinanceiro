import { describe, expect, it } from "vitest";
import type { News, NewsLevel, NewsType } from "@/types";
import { filterNews, groupByDay, type JournalFilter } from "./filter";

const item = (id: number, partial: Partial<News>): News => ({
  id,
  news_date: "2016-03-14",
  news_type: "MEASURE_VOTED",
  headline: "Congresso aprova corte no IR",
  dek: null,
  tickers: [],
  ...partial,
});

const NONE: JournalFilter = { query: "", section: null, onlyMine: false };
const levels: Partial<Record<NewsType, NewsLevel>> = { PARTY_LIFE: "OFF" };
const context = {
  sectionOf: () => "POLITICS" as const,
  levelOf: (type: NewsType) => levels[type] ?? "JOURNAL",
  held: new Set(["PETR4"]),
};

describe("filterNews", () => {
  const items = [
    item(1, { headline: "Congresso aprova corte no IR", tickers: ["PETR4"] }),
    item(2, { headline: "Bia funda o PLB", news_type: "PARTY_LIFE" }),
    item(3, { headline: "Vale anuncia recompra", dek: "Até 5% das ações", tickers: ["VALE3"] }),
  ];
  const ids = (found: News[]) => found.map((found_item) => found_item.id);

  it("esconde o tipo desligado", () => {
    expect(ids(filterNews(items, NONE, context))).toEqual([1, 3]);
  });

  it("busca na manchete, na linha de apoio e nos tickers, sem distinguir maiúsculas", () => {
    expect(ids(filterNews(items, { ...NONE, query: "RECOMPRA" }, context))).toEqual([3]);
    expect(ids(filterNews(items, { ...NONE, query: "5% das" }, context))).toEqual([3]);
    expect(ids(filterNews(items, { ...NONE, query: "vale3" }, context))).toEqual([3]);
  });

  it("só minha carteira deixa as manchetes que citam um ativo que o jogador tem", () => {
    expect(ids(filterNews(items, { ...NONE, onlyMine: true }, context))).toEqual([1]);
  });

  it("filtra pela seção do tipo", () => {
    const economy = { ...context, sectionOf: () => "ECONOMY" as const };
    expect(filterNews(items, { ...NONE, section: "POLITICS" }, economy)).toEqual([]);
  });
});

describe("groupByDay", () => {
  it("junta as manchetes seguidas do mesmo dia", () => {
    const groups = groupByDay([
      item(3, { news_date: "2016-03-14" }),
      item(2, { news_date: "2016-03-14" }),
      item(1, { news_date: "2016-03-11" }),
    ]);
    expect(groups.map((g) => [g.day, g.items.length])).toEqual([
      ["2016-03-14", 2],
      ["2016-03-11", 1],
    ]);
  });
});
