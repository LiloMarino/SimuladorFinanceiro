import { describe, expect, it } from "vitest";
import type { BaseDeal } from "@/types";
import {
  addressLabel,
  addressOf,
  amendmentSentence,
  amendmentNote,
  boostLabel,
  computerAmendmentSentence,
  favoritismSentence,
  NO_SECTOR,
  WHOLE_SECTOR,
  worksBoostSentence,
} from "./sector-address";

const deal = (overrides: Partial<BaseDeal>) =>
  ({
    status: "ACTIVE",
    is_computer: false,
    sector: null,
    segment: null,
    sector_boost: "0.03",
    ...overrides,
  }) as BaseDeal;

describe("addressOf", () => {
  it("sem setor, não há endereço nem segmento", () => {
    expect(addressOf(NO_SECTOR, "Geração")).toEqual({ sector: null, segment: null });
    expect(addressOf("", WHOLE_SECTOR)).toEqual({ sector: null, segment: null });
  });

  it("o setor inteiro vira segmento nulo", () => {
    expect(addressOf("Energia", WHOLE_SECTOR)).toEqual({ sector: "Energia", segment: null });
  });

  it("o segmento escolhido segue com o setor", () => {
    expect(addressOf("Energia", "Geração")).toEqual({ sector: "Energia", segment: "Geração" });
  });
});

describe("addressLabel", () => {
  it("nomeia o setor ou o setor com o segmento", () => {
    expect(addressLabel({ sector: "Energia", segment: null })).toBe("Energia");
    expect(addressLabel({ sector: "Energia", segment: "Geração" })).toBe("Energia · Geração");
    expect(addressLabel({ sector: null, segment: null })).toBe("");
  });
});

describe("boostLabel", () => {
  it("põe sinal e só mostra as casas que existem", () => {
    expect(boostLabel("0.03")).toBe("+3%");
    expect(boostLabel("0.0175")).toBe("+1,75%");
  });
});

describe("worksBoostSentence", () => {
  it("diz o alvo e a alta em 6 meses", () => {
    expect(worksBoostSentence({ sector: "Energia", segment: null }, "0.03")).toBe("Ações de Energia: +3% em 6 meses");
  });
});

describe("favoritismSentence", () => {
  it("diz quantos pontos de aprovação a obra custa", () => {
    expect(favoritismSentence("1.8")).toBe("Favorecimento: −1,8 ponto de aprovação enquanto a obra valer");
    expect(favoritismSentence("6")).toBe("Favorecimento: −6 pontos de aprovação enquanto a obra valer");
  });
});

describe("amendment texts", () => {
  it("a frase do acordo traz a alta cheia", () => {
    expect(amendmentSentence("0.03")).toBe("as ações do setor sobem até +3% enquanto o acordo valer");
  });

  it("o acordo em vigor traz o endereço e a alta", () => {
    expect(amendmentNote(deal({ sector: "Energia", segment: "Geração" }))).toBe("Energia · Geração: +3%");
    expect(amendmentNote(deal({ sector: null }))).toBe("");
  });

  it("a proposta que o computador responde diz para onde a emenda vai", () => {
    expect(amendmentNote(deal({ status: "PENDING", is_computer: true, sector: "Energia" }))).toBe(
      "leva a emenda para Energia: +3%",
    );
    expect(amendmentNote(deal({ status: "PENDING", is_computer: false, sector: null }))).toBe("");
  });

  it("o partido do computador leva a emenda para o setor que escolheu", () => {
    expect(computerAmendmentSentence("Energia", "0.03")).toBe("leva a emenda para Energia: +3%");
  });
});
