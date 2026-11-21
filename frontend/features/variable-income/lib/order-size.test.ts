import { describe, expect, it } from "vitest";
import { orderSizeOf } from "./order-size";

describe("tamanho da ordem enviado ao servidor", () => {
  it("o Máx vai como intenção, sem número", () => {
    expect(orderSizeOf({ maxChosen: true, byAmount: false, quantity: "100", amount: "0" })).toEqual({ max_size: true });
  });

  it("o Máx vale também na compra por valor (Tudo)", () => {
    expect(orderSizeOf({ maxChosen: true, byAmount: true, quantity: "0", amount: "500.00" })).toEqual({
      max_size: true,
    });
  });

  it("sem o Máx, vai o número que o jogador digitou", () => {
    expect(orderSizeOf({ maxChosen: false, byAmount: false, quantity: "100", amount: "0" })).toEqual({
      quantity: "100",
    });
    expect(orderSizeOf({ maxChosen: false, byAmount: true, quantity: "0", amount: "500.00" })).toEqual({
      amount: "500.00",
    });
  });
});
