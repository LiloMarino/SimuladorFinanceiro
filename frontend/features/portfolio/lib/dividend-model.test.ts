import { describe, expect, it } from "vitest";
import type { DividendBucket } from "@/types";
import { bucketLabel, bucketTitle, dividendScale, payersSentence } from "./dividend-model";

const bucket = (payers: string[]): DividendBucket => ({
  period: "2018-12-01",
  amount: "424.10",
  by_class: [],
  payers: payers.map((ticker) => ({ ticker, name: ticker, asset_class: "STOCK", amount: "10" })),
});

describe("dividendScale", () => {
  it("cobre o maior valor com marcas redondas", () => {
    expect(dividendScale(424.1)).toEqual({ ceiling: 500, ticks: [0, 100, 200, 300, 400, 500] });
  });

  it("sem proventos mantém uma escala mínima", () => {
    expect(dividendScale(0)).toEqual({ ceiling: 100, ticks: [0, 100] });
  });

  it("valores pequenos usam passos pequenos", () => {
    expect(dividendScale(3.2).ceiling).toBeGreaterThanOrEqual(3.2);
    expect(dividendScale(3.2).ticks.length).toBeLessThanOrEqual(6);
  });
});

describe("rótulos do período", () => {
  it("mês mostra o mês curto e o tooltip junta o ano", () => {
    expect(bucketLabel(bucket([]), "month")).toBe("dez");
    expect(bucketTitle(bucket([]), "month")).toBe("dez 2018");
  });

  it("ano mostra só o ano", () => {
    expect(bucketLabel(bucket([]), "year")).toBe("2018");
    expect(bucketTitle(bucket([]), "year")).toBe("2018");
  });
});

describe("payersSentence", () => {
  it("lista até três ativos e resume o resto", () => {
    expect(payersSentence(bucket([]), "month")).toBe("Nada caiu no caixa neste período.");
    expect(payersSentence(bucket(["PETR4"]), "month")).toBe("PETR4 pagou no mesmo mês.");
    expect(payersSentence(bucket(["TAEE11", "PETR4"]), "month")).toBe("TAEE11 e PETR4 pagaram no mesmo mês.");
    expect(payersSentence(bucket(["A", "B", "C", "D", "E"]), "year")).toBe("A, B, C e mais 2 pagaram no mesmo ano.");
  });
});
