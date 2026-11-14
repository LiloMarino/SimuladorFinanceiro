import { describe, expect, it } from "vitest";
import type { Order } from "@/types";
import { describeOffer } from "./order-book";
import { isSyntheticOwner, ownerBadge, ownsOrder } from "./order-owner";

const order = (patch: Partial<Order>): Order => ({
  id: "o",
  player_nickname: "Ana Souza",
  player_color: "chart-1",
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

describe("ownerBadge", () => {
  it("jogador leva a sigla na cor dele", () => {
    const badge = ownerBadge(order({}));
    expect(badge.label).toBe("AS");
    expect(badge.tone).toBe("player");
    expect(badge.color?.background).toBe("var(--player-1)");
  });

  it("robô leva a sigla em cinza", () => {
    expect(ownerBadge(order({ owner: "bot", player_nickname: "Robô Rui" }))).toMatchObject({
      label: "RR",
      tone: "neutral",
      color: null,
    });
  });

  it("gestora leva a sigla na cor da gestora", () => {
    expect(ownerBadge(order({ owner: "fund", player_nickname: "Aurora Gestão", player_color: null }))).toMatchObject({
      label: "AG",
      tone: "fund",
    });
  });

  it.each([
    ["market", "B3"],
    ["fund_maker", "FM"],
    ["fund_issuer", "OP"],
  ] as const)("dono sintético %s tem a sigla %s em cinza", (owner, label) => {
    expect(ownerBadge(order({ owner, player_color: null }))).toMatchObject({ label, tone: "neutral" });
    expect(isSyntheticOwner(order({ owner }))).toBe(true);
  });
});

describe("ownsOrder", () => {
  it("na conta pessoal a ordem é do jogador de mesmo apelido", () => {
    const viewer = { nickname: "Ana Souza", fundName: null };
    expect(ownsOrder(order({}), viewer)).toBe(true);
    expect(ownsOrder(order({ player_nickname: "Bia" }), viewer)).toBe(false);
  });

  it("com a gestora ativa a ordem é da gestora, não do jogador", () => {
    const viewer = { nickname: "Ana Souza", fundName: "Aurora Gestão" };
    expect(ownsOrder(order({ owner: "fund", player_nickname: "Aurora Gestão" }), viewer)).toBe(true);
    expect(ownsOrder(order({}), viewer)).toBe(false);
  });

  it("dono sintético com o apelido do jogador não é dele", () => {
    expect(
      ownsOrder(order({ owner: "market", player_nickname: "Ana Souza" }), { nickname: "Ana Souza", fundName: null }),
    ).toBe(false);
  });
});

describe("describeOffer", () => {
  it("diz quem pôs a oferta", () => {
    expect(describeOffer(order({ action: "sell", owner: "market", player_nickname: "Mercado" }), "R$ 12,35")).toBe(
      "a venda de R$ 12,35 do Mercado",
    );
    expect(describeOffer(order({}), "R$ 12,35")).toBe("a compra de R$ 12,35 de Ana Souza");
    expect(describeOffer(order({ owner: "fund_maker", player_nickname: "Formador de mercado" }), "R$ 1,00")).toBe(
      "a compra de R$ 1,00 do formador de mercado",
    );
  });
});
