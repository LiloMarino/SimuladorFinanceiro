import { describe, expect, it } from "vitest";
import type { FundOffers } from "@/types";
import {
  cashFallsShort,
  cashQuotas,
  feesText,
  holdersBoughtPercent,
  marketGapLabel,
  openOfferBadge,
  openOfferDeadline,
  preferenceCost,
  preferenceShare,
  sessionsLeftLabel,
  soldPercent,
} from "./fund-offers";

type OpenOffer = FundOffers["open"][number];
type ClosedOffer = FundOffers["closed"][number];
type PreferenceOffer = FundOffers["preference"][number];

const open = (over: Partial<OpenOffer> = {}): OpenOffer => ({
  fund_id: 1,
  ticker: "CEDR11",
  name: "Cedro Capital",
  manager_nickname: "Duda",
  kind: "initial",
  price: "100",
  quotas: "30000",
  remaining: "11600",
  session: 3,
  ends_on: "2026-11-20",
  sessions_left: 2,
  management_fee: "0.015",
  performance_fee: "0.2",
  preference_ends_on: null,
  preference_bought: null,
  ...over,
});

const closed = (over: Partial<ClosedOffer> = {}): ClosedOffer => ({
  fund_id: 1,
  ticker: "AURO11",
  name: "Aurora Gestão",
  kind: "issuance",
  price: "104.10",
  quotas: "5740",
  sold: "5740",
  closed_on: "2026-07-14",
  market_price: "106.02",
  ...over,
});

const preference = (over: Partial<PreferenceOffer> = {}): PreferenceOffer => ({
  fund_id: 2,
  ticker: "AURO11",
  name: "Aurora Gestão",
  issuance_quotas: "3574",
  price: "110.44",
  my_rights: "322",
  my_left: "322",
  holders_bought: "1180",
  preference_ends_on: "2026-12-02",
  sessions_left: 9,
  leftover_sessions: 5,
  ...over,
});

describe("sessionsLeftLabel", () => {
  it("concorda o plural e avisa o último pregão", () => {
    expect(sessionsLeftLabel(2)).toBe("faltam 2 pregões");
    expect(sessionsLeftLabel(1)).toBe("falta 1 pregão");
    expect(sessionsLeftLabel(0)).toBe("último pregão");
  });
});

describe("openOfferBadge", () => {
  it("mostra o pregão da oferta de abertura sobre o total de pregões", () => {
    expect(openOfferBadge(open())).toBe("pregão 3 de 5");
  });

  it("chama de sobra aberta a venda da emissão a todos", () => {
    expect(openOfferBadge(open({ kind: "leftover", session: null }))).toBe("sobra aberta");
  });

  it("chama de esgotada a venda sem cota, que só encerra no prazo", () => {
    const sold = open({ remaining: "0" });
    expect(openOfferBadge(sold)).toBe("esgotada");
    expect(openOfferDeadline(sold)).toBe("encerra no prazo");
    expect(openOfferDeadline(open())).toBe("faltam 2 pregões");
  });
});

describe("soldPercent", () => {
  it("11.600 à venda de 30.000 é 61,3% vendido", () => {
    expect(soldPercent(open())).toBeCloseTo(61.33, 2);
  });

  it("sem cota ofertada não há o que medir", () => {
    expect(soldPercent(open({ quotas: "0", remaining: "0" }))).toBe(0);
  });
});

describe("cashQuotas", () => {
  it("o caixa paga as cotas inteiras ao preço fixo", () => {
    expect(cashQuotas(41_250, 100, 11_600)).toBe(412);
  });

  it("não passa do que ainda está à venda", () => {
    expect(cashQuotas(10_000_000, 100, 640)).toBe(640);
  });

  it("preço zero não compra nada", () => {
    expect(cashQuotas(1000, 0, 10)).toBe(0);
  });
});

describe("cashFallsShort", () => {
  it("avisa quando o caixa não paga o que resta", () => {
    expect(cashFallsShort(open(), 41_250)).toBe(true);
  });

  it("não avisa quando o caixa paga tudo ou quando nada resta", () => {
    expect(cashFallsShort(open({ remaining: "640" }), 64_000)).toBe(false);
    expect(cashFallsShort(open({ remaining: "0" }), 0)).toBe(false);
  });
});

describe("preferência do cotista", () => {
  it("a parte é a fatia dos direitos sobre as cotas da emissão", () => {
    expect(preferenceShare(preference())).toBeCloseTo(0.09, 2);
  });

  it("o custo usa o que sobra do direito ao preço fixo", () => {
    expect(preferenceCost(preference())).toBeCloseTo(35_561.68, 2);
    expect(preferenceCost(preference({ my_left: "100" }))).toBeCloseTo(11_044, 2);
  });

  it("os cotistas compraram 1.180 de 3.574, 33% da emissão", () => {
    expect(holdersBoughtPercent(preference())).toBeCloseTo(33.02, 2);
  });
});

describe("marketGapLabel", () => {
  it("1,8% acima: o mercado paga mais que a oferta", () => {
    expect(marketGapLabel(closed())).toBe("1,8% acima da oferta");
  });

  it("abaixo quando o mercado vale menos", () => {
    expect(marketGapLabel(closed({ market_price: "93.69" }))).toBe("10,0% abaixo da oferta");
  });

  it("sem preço de hoje não há comparação", () => {
    expect(marketGapLabel(closed({ market_price: null }))).toBeNull();
  });
});

describe("feesText", () => {
  it("a oferta de abertura avisa que a carteira nasce com o dinheiro dela", () => {
    expect(feesText(open())).toBe(
      "Taxa de administração de 1,5% ao ano e de performance de 20% do que passar do CDI. Sem histórico: a carteira começa com o dinheiro da oferta.",
    );
  });

  it("a sobra da emissão fica só nas taxas", () => {
    expect(feesText(open({ kind: "leftover" }))).toBe(
      "Taxa de administração de 1,5% ao ano e de performance de 20% do que passar do CDI.",
    );
  });
});
