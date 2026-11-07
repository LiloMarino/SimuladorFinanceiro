import { describe, expect, it } from "vitest";
import { dividendsToast, splitToast } from "./corporate-actions-toast";

const line = (ticker: string, amount: string) => ({ ticker, amount });

describe("dividendsToast", () => {
  it("soma o pregão e lista os três que mais pagaram", () => {
    const toast = dividendsToast({
      dividends: [
        line("AAAA3", "10"),
        line("BBBB11", "40"),
        line("CCCC4", "25"),
        line("DDDD3", "5"),
        line("EEEE3", "1"),
      ],
      dividends_total: "81",
      splits: [],
    });

    expect(toast?.title).toContain("81,00");
    expect(toast?.description?.replaceAll(" ", " ")).toBe("BBBB11 R$ 40,00 · CCCC4 R$ 25,00 · AAAA3 R$ 10,00 e mais 2");
  });

  it("sem provento no pregão não há aviso", () => {
    expect(dividendsToast({ dividends: [], dividends_total: "0", splits: [] })).toBeNull();
  });
});

describe("splitToast", () => {
  const split = { ticker: "ABCD3", ratio: "2", shares_before: "101", shares_after: "202", fraction_amount: "0" };

  it("conta a razão e a nova quantidade", () => {
    const toast = splitToast(split);
    expect(toast.title).toBe("Desdobramento 2 para 1 em ABCD3");
    expect(toast.description).toBe("Suas ações foram de 101 para 202.");
  });

  it("avisa da fração paga em dinheiro", () => {
    expect(splitToast({ ...split, ratio: "0.1", fraction_amount: "3.5" }).description).toContain("3,50");
  });
});
