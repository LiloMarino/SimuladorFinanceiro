import { describe, expect, it } from "vitest";
import type { FundIssuanceEstimate } from "@/types";
import { emptyEstimateReason, estimateNote, estimateRaisedText, isEmptyEstimate } from "./fund-issuance-estimate";

// O dinheiro formatado separa "R$" do valor com espaço não separável
const plain = (text: string) => text.replaceAll(" ", " ");

const estimate = (overrides: Partial<FundIssuanceEstimate> = {}): FundIssuanceEstimate => ({
  quotas_min: "115",
  quotas_max: "130",
  raised_min: "11470",
  raised_max: "12940",
  commission_min: "30",
  commission_max: "60",
  performance: 0.02,
  premium: 0.1,
  ...overrides,
});

const empty = (overrides: Partial<FundIssuanceEstimate> = {}) =>
  estimate({
    quotas_min: "0",
    quotas_max: "0",
    raised_min: "0",
    raised_max: "0",
    commission_min: "0",
    commission_max: "0",
    ...overrides,
  });

describe("isEmptyEstimate", () => {
  it("é vazia só quando nenhum extremo compra cota", () => {
    expect(isEmptyEstimate(empty())).toBe(true);
    expect(isEmptyEstimate(estimate({ quotas_min: "0" }))).toBe(false);
  });
});

describe("estimateRaisedText", () => {
  it("mostra do menor ao maior valor", () => {
    expect(plain(estimateRaisedText(estimate()))).toBe("R$ 11.470,00 a R$ 12.940,00");
  });

  it("mostra um valor só quando os extremos coincidem", () => {
    expect(plain(estimateRaisedText(estimate({ raised_max: "11470" })))).toBe("R$ 11.470,00");
  });
});

describe("estimateNote", () => {
  it("diz as cotas e a comissão que já saiu do dinheiro", () => {
    expect(plain(estimateNote(estimate()))).toBe(
      "115 a 130 cotas, já com a comissão dos banqueiros (R$ 30,00 a R$ 60,00) descontada",
    );
  });

  it("sem comissão diz só as cotas", () => {
    expect(estimateNote(estimate({ commission_min: "0", commission_max: "0", quotas_max: "115" }))).toBe("115 cotas");
  });
});

describe("emptyEstimateReason", () => {
  it("gestora abaixo do CDI e sem ágio: diz os dois motivos", () => {
    expect(emptyEstimateReason(empty({ performance: -0.02, premium: 0 }))).toBe(
      "Bots e Mercado só compram quando a gestora rende acima do CDI ou a cota tem ágio: a gestora rende 2 pontos abaixo do CDI e a cota não tem ágio.",
    );
  });

  it("desempenho igual ao CDI", () => {
    expect(emptyEstimateReason(empty({ performance: 0, premium: 0 }))).toContain("rende o mesmo que o CDI");
  });

  it("com atrativo mas sem compra, o problema é o tamanho da sobra", () => {
    expect(emptyEstimateReason(empty({ performance: 0.03, premium: 0 }))).toContain("sobra é pequena demais");
  });
});
