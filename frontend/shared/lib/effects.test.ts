import { describe, expect, it } from "vitest";
import { curvePath, inflationTone, phaseText, signedIpca, signedStocks } from "./effects";

describe("efeito na inflação", () => {
  it("escreve pontos de IPCA e variação da bolsa com sinal", () => {
    expect(signedIpca("0.55")).toBe("+0,55");
    expect(signedIpca("-0.12")).toBe("−0,12");
    expect(signedIpca("0.001")).toBe("—");
    expect(signedStocks("-0.048")).toBe("−4,8%");
    expect(signedStocks("0.024")).toBe("+2,4%");
  });

  it("pinta inflação a mais de vermelho e a menos de verde", () => {
    expect(inflationTone("0.4")).toBe("destructive");
    expect(inflationTone("-0.4")).toBe("success");
    expect(inflationTone("0")).toBe("default");
  });

  it("diz em que fase o efeito está", () => {
    expect(phaseText("RISING", "2023-05-10", "2024-09-10")).toBe("chegando: cheio em mai");
    expect(phaseText("FALLING", "2023-05-10", "2024-09-10")).toBe("caindo: some em set");
  });

  it("desenha a curva com a linha do zero dentro da área", () => {
    expect(curvePath([0], 100, 30)).toBeNull();
    const rising = curvePath([0, 1, 2], 100, 30, 0);
    expect(rising?.zero).toBe(30);
    const cut = curvePath([0, -1, -2], 100, 30, 0);
    expect(cut?.zero).toBe(0);
  });
});
