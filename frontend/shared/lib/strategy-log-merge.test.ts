import { describe, expect, it } from "vitest";
import type { StrategyLogRow } from "@/types";
import { mergeStrategyLog, type StrategyLogData } from "./strategy-log-merge";

function row(id: number, overrides: Partial<StrategyLogRow> = {}): StrategyLogRow {
  return {
    id,
    event_date: "2026-03-10",
    kind: "order",
    strategy_key: "buy_one",
    strategy_name: "Compra um",
    action: "buy",
    ticker: "PETR4",
    asset_name: null,
    quantity: "1",
    price: "10.00",
    order_type: "limit",
    reason: null,
    status: "open",
    detail: null,
    annual_rate: null,
    term_months: null,
    loan_number: null,
    ...overrides,
  };
}

const data = (pages: StrategyLogRow[][], total: number): StrategyLogData => ({
  pages: pages.map((items) => ({ items, total })),
  pageParams: pages.map((_page, index) => (index === 0 ? null : (pages[index - 1]?.at(-1)?.id ?? null))),
});

const ids = (result: StrategyLogData | null) => result?.pages.map((page) => page.items.map((item) => item.id));

describe("mergeStrategyLog", () => {
  it("coloca a linha nova no topo da primeira página e atualiza o total de todas", () => {
    const result = mergeStrategyLog(data([[row(5), row(4)], [row(3)]], 3), "all", [row(7), row(6)], 5);

    expect(ids(result)).toEqual([[7, 6, 5, 4], [3]]);
    expect(result?.pages.map((page) => page.total)).toEqual([5, 5]);
  });

  it("troca a linha mudada pelo id, sem mexer no total", () => {
    const result = mergeStrategyLog(data([[row(5), row(4)], [row(3)]], 3), "all", [row(3, { status: "executed" })], 3);

    expect(ids(result)).toEqual([[5, 4], [3]]);
    expect(result?.pages[1]?.items[0]?.status).toBe("executed");
  });

  it("ignora a linha mudada que a tela ainda não carregou", () => {
    const result = mergeStrategyLog(data([[row(5)]], 5), "all", [row(2, { status: "canceled" })], 5);

    expect(ids(result)).toEqual([[5]]);
  });

  it("só aplica ao filtro as linhas que ele mostra", () => {
    const mode = row(8, { kind: "enabled", status: null });
    const orders = mergeStrategyLog(data([[row(5)]], 1), "orders", [mode, row(9)], 2);
    const modes = mergeStrategyLog(
      data([[mode]], 1),
      "modes",
      [row(10), row(11, { kind: "disabled", status: null })],
      2,
    );

    expect(ids(orders)).toEqual([[9, 5]]);
    expect(ids(modes)).toEqual([[11, 8]]);
  });

  it("entra no topo mesmo na lista vazia", () => {
    expect(ids(mergeStrategyLog(data([[]], 0), "all", [row(1)], 1))).toEqual([[1]]);
  });

  it("ordena as linhas novas pelo dia e depois pelo id", () => {
    const result = mergeStrategyLog(
      data([[row(5)]], 1),
      "all",
      [row(6), row(8, { event_date: "2026-03-11" }), row(7, { event_date: "2026-03-11" })],
      4,
    );

    expect(ids(result)).toEqual([[8, 7, 6, 5]]);
  });

  it("devolve nulo quando o total cresceu além das linhas que chegaram", () => {
    expect(mergeStrategyLog(data([[row(5)]], 1), "all", [row(7)], 3)).toBeNull();
  });

  it("devolve nulo quando o total encolheu ou a lista passou dele", () => {
    expect(mergeStrategyLog(data([[row(5), row(4)]], 2), "all", [], 1)).toBeNull();
  });
});
