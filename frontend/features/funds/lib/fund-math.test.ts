import { describe, expect, it } from "vitest";
import { foundingSummary, offerControl, tickerFeedback } from "./fund-math";

describe("foundingSummary", () => {
  it("emite uma cota a cada R$ 100,00 levados", () => {
    // 100.000 de caixa + 60.000 em ações = 160.000; ÷ 100 = 1.600 cotas
    expect(foundingSummary(100_000, 60_000)).toEqual({ taken: 160_000, quotas: 1600, leftover: 0 });
  });

  it("arredonda as cotas para baixo e deixa a sobra na gestora", () => {
    // 1.050 ÷ 100 = 10,5 → 10 cotas; sobram R$ 50
    expect(foundingSummary(1050, 0)).toEqual({ taken: 1050, quotas: 10, leftover: 50 });
  });

  it("sem nada levado não emite cota", () => {
    expect(foundingSummary(0, 0).quotas).toBe(0);
  });
});

describe("controle da oferta", () => {
  it("a oferta de 800 cotas, vendida toda, mantém o controle", () => {
    // 5.800 ÷ (10.000 + 800) = 53,7%
    const { share, keepsControl } = offerControl(5800, 10_000, 800);
    expect(share).toBeCloseTo(0.537, 3);
    expect(keepsControl).toBe(true);
  });

  it("a oferta de 2.800 cotas, vendida toda, derruba o controle", () => {
    // 5.800 ÷ 12.800 = 45,3%
    const { share, keepsControl } = offerControl(5800, 10_000, 2800);
    expect(share).toBeCloseTo(0.453, 3);
    expect(keepsControl).toBe(false);
  });

  it("exatamente 50% não é controle", () => {
    expect(offerControl(5000, 10_000, 0).keepsControl).toBe(false);
  });
});

describe("tickerFeedback", () => {
  const free = { ticker: "AURO11", status: "free", owner_name: null } as const;

  it("com menos de 4 letras pede as 4 letras", () => {
    expect(tickerFeedback("AU", undefined, false).message).toBe("Use 4 letras");
  });

  it("enquanto a checagem não volta, mostra que está conferindo", () => {
    expect(tickerFeedback("AURO", undefined, true).message).toBe("Conferindo AURO11...");
  });

  it("a resposta de outra sigla não vale para a digitada", () => {
    expect(tickerFeedback("AURA", free, false).message).toBe("Conferindo AURA11...");
  });

  it("livre", () => {
    expect(tickerFeedback("AURO", free, false)).toEqual({ tone: "success", message: "AURO11 está livre" });
  });

  it("ativo da partida", () => {
    const check = { ticker: "PETR11", status: "asset", owner_name: null } as const;
    expect(tickerFeedback("PETR", check, false)).toEqual({
      tone: "error",
      message: "PETR já é um ativo da partida",
    });
  });

  it("gestora de outro jogador", () => {
    const check = { ticker: "BIAI11", status: "fund", owner_name: "Bia" } as const;
    expect(tickerFeedback("BIAI", check, false).message).toBe("BIAI11 é a gestora da Bia");
  });
});
