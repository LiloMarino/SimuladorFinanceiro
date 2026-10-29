import { describe, expect, it } from "vitest";
import { isRaise, isSpending } from "@/shared/lib/spending-kinds";
import type { GroupReaction } from "@/types";
import {
  checkValue,
  chipFits,
  chipValueText,
  pointsOf,
  reasonOf,
  signedPointsOf,
  splitReactions,
  spendingValue,
  stepChips,
  valueWindow,
  windowSentence,
} from "./spending";

const AUXILIO = { value: "0.014", step: "0.005", limit: "0.05" };
const RAISE_AT_FLOOR = { value: "0", step: "0.03", limit: "0.15" };

describe("rótulos", () => {
  it("escreve o auxílio como fatia do PIB e o reajuste como ganho real", () => {
    expect(spendingValue("WELFARE_SPENDING", "0.014")).toBe("1,4% do PIB");
    expect(spendingValue("SERVANT_RAISE", "0.02")).toBe("ganho real de 2% ao ano");
    expect(pointsOf("0.0125")).toBe("1,25");
    expect(signedPointsOf("-0.005")).toBe("−0,5");
  });

  it("separa os quatro tipos de gasto dos outros", () => {
    expect(isSpending("PUBLIC_WORKS")).toBe(true);
    expect(isSpending("STOCK_PROFIT_RATE")).toBe(false);
    expect(isRaise("RETIREE_RAISE")).toBe(true);
    expect(isRaise("WELFARE_SPENDING")).toBe(false);
  });
});

describe("janela do passo", () => {
  it("anda um passo para cada lado do valor de hoje", () => {
    expect(valueWindow(AUXILIO)).toEqual({ min: 0.009, max: 0.019 });
  });

  it("não desce abaixo de 0% nem passa do teto", () => {
    expect(valueWindow(RAISE_AT_FLOOR)).toEqual({ min: 0, max: 0.03 });
    expect(valueWindow({ value: "0.049", step: "0.005", limit: "0.05" }).max).toBe(0.05);
  });

  it("marca os atalhos que cabem na janela", () => {
    expect(stepChips("WELFARE_SPENDING")).toEqual([-0.5, -0.25, 0.25, 0.5]);
    expect(chipFits(RAISE_AT_FLOOR, -1)).toBe(false);
    expect(chipFits(RAISE_AT_FLOOR, 3)).toBe(true);
    expect(chipValueText(AUXILIO, 0.5)).toBe("1,9");
    expect(chipValueText(AUXILIO, -0.25)).toBe("1,15");
  });
});

describe("checkValue", () => {
  it("lê o número digitado em % e devolve a fração", () => {
    expect(checkValue(AUXILIO, "1,9")).toEqual({ status: "ok", fraction: "0.019" });
    expect(checkValue(AUXILIO, "0,9")).toEqual({ status: "ok", fraction: "0.009" });
  });

  it("trava o número fora do passo", () => {
    expect(checkValue(AUXILIO, "2,4")).toMatchObject({ status: "outside" });
    expect(checkValue(RAISE_AT_FLOOR, "-1")).toMatchObject({ status: "outside" });
  });

  it("não envia campo vazio nem o valor de hoje", () => {
    expect(checkValue(AUXILIO, "")).toEqual({ status: "empty" });
    expect(checkValue(AUXILIO, "1,4")).toEqual({ status: "same" });
  });

  it("explica a janela na frase de ajuda", () => {
    expect(windowSentence("WELFARE_SPENDING", AUXILIO)).toBe(
      "Hoje 1,4%. Numa medida, de 0,9% a 1,9%: até 0,5 ponto para cima ou para baixo.",
    );
  });
});

describe("quem gosta e quem não gosta", () => {
  const reactions: GroupReaction[] = [
    { group: "INVESTORS", points: "2" },
    { group: "WELFARE", points: "-6" },
    { group: "PUBLIC_SERVANTS", points: "0" },
    { group: "RETIREES", points: "1" },
    { group: "FORMAL_WORKERS", points: "-1" },
  ];

  it("ordena os grupos e deixa de fora quem não muda", () => {
    const { likes, dislikes } = splitReactions(reactions);
    expect(likes.map((reaction) => reaction.group)).toEqual(["INVESTORS", "RETIREES"]);
    expect(dislikes.map((reaction) => reaction.group)).toEqual(["WELFARE", "FORMAL_WORKERS"]);
  });

  it("dá o motivo direto a quem recebe e o da inflação aos outros", () => {
    expect(reasonOf("WELFARE_SPENDING", "WELFARE", -6, false)).toBe("recebem menos quando a medida vale");
    expect(reasonOf("WELFARE_SPENDING", "WELFARE", 6, true)).toBe("recebem mais quando a medida vale");
    expect(reasonOf("WELFARE_SPENDING", "INVESTORS", 2, false)).toBe("inflação e dívida mais baixas");
    expect(reasonOf("WELFARE_SPENDING", "INVESTORS", -1, true)).toBe("inflação, dívida e SELIC mais altas");
    expect(reasonOf("WELFARE_SPENDING", "RETIREES", -1, true)).toBe("a inflação come o benefício");
    expect(reasonOf("WELFARE_SPENDING", "ENTREPRENEURS", 1, false)).toBe("crédito mais barato com a SELIC");
    expect(reasonOf("WELFARE_SPENDING", "FORMAL_WORKERS", -1, false)).toBe("menos consumo, menos vaga");
  });
});
