import { describe, expect, it } from "vitest";
import type { Order } from "@/types";
import {
  applyOrderEvent,
  barShare,
  displayBookQuantity,
  bookSpread,
  largestQuantity,
  spreadPercentDigits,
  splitBook,
  typicalPrice,
} from "./order-book";

const order = (patch: Partial<Order>): Order => ({
  id: "o",
  player_nickname: "ana",
  player_color: null,
  owner: "player",
  action: "buy",
  order_type: "limit",
  status: "pending",
  size: "100",
  remaining: "100",
  limit_price: 10,
  placed_on: "2024-01-02",
  ...patch,
});

describe("typicalPrice", () => {
  it("é a média da máxima, da mínima e do fechamento", () => {
    expect(typicalPrice({ high: 12.6, low: 12.0, close: 12.3 })).toBeCloseTo(12.3);
  });
});

describe("splitBook", () => {
  it("separa compras e vendas abertas na ordem recebida", () => {
    const book = splitBook([
      order({ id: "b1", limit_price: 12.33 }),
      order({ id: "b2", limit_price: 12.3 }),
      order({ id: "s1", action: "sell", limit_price: 12.35 }),
    ]);
    expect(book.buys.map((o) => o.id)).toEqual(["b1", "b2"]);
    expect(book.sells.map((o) => o.id)).toEqual(["s1"]);
  });

  it("deixa de fora ordem sem preço e ordem que não está aberta", () => {
    const book = splitBook([
      order({ id: "mercado", limit_price: null }),
      order({ id: "feita", status: "executed" }),
      order({ id: "parcial", status: "partial" }),
    ]);
    expect(book.buys.map((o) => o.id)).toEqual(["parcial"]);
  });
});

describe("bookSpread", () => {
  const book = splitBook([order({ limit_price: 12.33 }), order({ action: "sell", limit_price: 12.35 })]);

  it("mede a diferença entre a melhor venda e a melhor compra", () => {
    const spread = bookSpread(book, 12.33);
    expect(spread?.amount).toBeCloseTo(0.02);
    expect(spread?.percent).toBeCloseTo(0.0016, 4);
  });

  it("não existe sem um dos lados", () => {
    expect(bookSpread(splitBook([order({})]), 12.33)).toBeNull();
  });
});

describe("barShare", () => {
  it("é a quantidade sobre a maior do livro", () => {
    expect(barShare(order({ remaining: "50" }), 200)).toBe(0.25);
  });

  it("não passa de 1 e não some abaixo do piso", () => {
    expect(barShare(order({ remaining: "300" }), 200)).toBe(1);
    expect(barShare(order({ remaining: "1" }), 1_000_000)).toBe(0.012);
  });
});

describe("largestQuantity", () => {
  it("olha os dois lados", () => {
    const book = splitBook([order({ remaining: "30" }), order({ action: "sell", remaining: "80" })]);
    expect(largestQuantity(book)).toBe(80);
  });
});

describe("spreadPercentDigits", () => {
  it("abre uma casa a mais quando a diferença é minúscula", () => {
    expect(spreadPercentDigits(0.0016)).toBe(2);
    expect(spreadPercentDigits(0.00002)).toBe(3);
  });
});

describe("displayBookQuantity", () => {
  it("abrevia de 1 milhão em diante", () => {
    expect(displayBookQuantity("4820000")).toBe("4,82 mi");
  });

  it("mantém a quantidade inteira abaixo disso", () => {
    expect(displayBookQuantity("1500")).toBe("1.500");
  });
});

describe("applyOrderEvent", () => {
  const book = [
    order({ id: "b1", action: "buy", limit_price: 10 }),
    order({ id: "b2", action: "buy", limit_price: 9 }),
    order({ id: "s1", action: "sell", limit_price: 11 }),
    order({ id: "s2", action: "sell", limit_price: 12 }),
  ];
  const ids = (orders: Order[]) => orders.map((o) => o.id);

  it("a compra nova entra no lugar do preço, depois das que chegaram antes no mesmo preço", () => {
    expect(ids(applyOrderEvent(book, order({ id: "n", action: "buy", limit_price: 10 })))).toEqual([
      "b1",
      "n",
      "b2",
      "s1",
      "s2",
    ]);
    expect(ids(applyOrderEvent(book, order({ id: "n", action: "buy", limit_price: 9.5 })))).toEqual([
      "b1",
      "n",
      "b2",
      "s1",
      "s2",
    ]);
    expect(ids(applyOrderEvent(book, order({ id: "n", action: "buy", limit_price: 8 })))).toEqual([
      "b1",
      "b2",
      "n",
      "s1",
      "s2",
    ]);
  });

  it("a venda nova entra da menor para a maior oferta", () => {
    expect(ids(applyOrderEvent(book, order({ id: "n", action: "sell", limit_price: 11.5 })))).toEqual([
      "b1",
      "b2",
      "s1",
      "n",
      "s2",
    ]);
    expect(ids(applyOrderEvent(book, order({ id: "n", action: "sell", limit_price: 10.5 })))).toEqual([
      "b1",
      "b2",
      "n",
      "s1",
      "s2",
    ]);
  });

  it("a ordem que mudou fica onde estava", () => {
    const next = applyOrderEvent(
      book,
      order({ id: "b2", action: "buy", limit_price: 9, status: "partial", remaining: "40" }),
    );
    expect(ids(next)).toEqual(ids(book));
    expect(next[1]?.remaining).toBe("40");
  });

  it("a ordem que deixou de estar aberta sai do livro", () => {
    expect(
      ids(applyOrderEvent(book, order({ id: "s1", action: "sell", limit_price: 11, status: "executed" }))),
    ).toEqual(["b1", "b2", "s2"]);
    expect(applyOrderEvent(book, order({ id: "x", status: "canceled" }))).toBe(book);
  });

  it("o livro vazio recebe a primeira ordem", () => {
    expect(ids(applyOrderEvent([], order({ id: "n" })))).toEqual(["n"]);
  });
});
