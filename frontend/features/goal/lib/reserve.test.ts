import { describe, expect, it } from "vitest";
import { reserveShares, reserveTone } from "./reserve";

describe("reserveShares", () => {
  it("põe o caixa e a liquidez diária lado a lado na régua de 6 meses", () => {
    const shares = reserveShares(2.6, 3);
    expect(shares.cash).toBeCloseTo(2.6 / 6);
    expect(shares.dailyLiquidity).toBeCloseTo(0.5);
  });

  it("corta a liquidez diária quando os dois passam de 6 meses", () => {
    const shares = reserveShares(4, 5);
    expect(shares.cash).toBeCloseTo(4 / 6);
    expect(shares.cash + shares.dailyLiquidity).toBeCloseTo(1);
  });

  it("trata caixa negativo como zero", () => {
    expect(reserveShares(-1, 3)).toEqual({ cash: 0, dailyLiquidity: 0.5 });
  });
});

describe("reserveTone", () => {
  it("separa frágil, atenção e boa em 3 e 6 meses", () => {
    expect(reserveTone(2.9)).toBe("destructive");
    expect(reserveTone(3)).toBe("warning");
    expect(reserveTone(6)).toBe("success");
  });
});
