import { describe, expect, it } from "vitest";
import type { StrategyInfo } from "@/types";
import { drawBotName, isDrawnName } from "./bot-names";

const strategy = {
  name: "Comprar e segurar",
  bot_names: ["Tio Patinhas", "Vovô Investidor", "Paciência"],
} as StrategyInfo;

describe("drawBotName", () => {
  it("sorteia entre os nomes da estratégia que a sala não tem", () => {
    // Só "Paciência" está livre: qualquer sorteio cai nele
    const taken = ["tio patinhas", "Vovô Investidor"];
    expect(drawBotName(strategy, taken, () => 0)).toBe("Paciência");
    expect(drawBotName(strategy, taken, () => 0.99)).toBe("Paciência");
  });

  it("usa o sorteio para escolher a posição na lista livre", () => {
    // Três livres: 0,5 × 3 = 1,5 → índice 1
    expect(drawBotName(strategy, [], () => 0.5)).toBe("Vovô Investidor");
  });

  it("vira '<estratégia> #2' quando a lista acaba e sobe até o menor número livre", () => {
    const all = ["Tio Patinhas", "Vovô Investidor", "Paciência"];
    expect(drawBotName(strategy, all)).toBe("Comprar e segurar #2");
    expect(drawBotName(strategy, [...all, "Comprar e segurar #2"])).toBe("Comprar e segurar #3");
  });
});

describe("isDrawnName", () => {
  it("reconhece o nome da lista e o numerado, não o digitado", () => {
    expect(isDrawnName("Paciência", strategy)).toBe(true);
    expect(isDrawnName("Comprar e segurar #7", strategy)).toBe(true);
    expect(isDrawnName("Meu bot", strategy)).toBe(false);
  });
});
