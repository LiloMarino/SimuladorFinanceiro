import { describe, expect, it } from "vitest";
import type { StrategyInfo } from "@/types";
import { inOptionOrder, paramPills, profileValues, sameTickerSet } from "./strategy-params";

const options = (...tickers: string[]) => tickers.map((ticker) => ({ ticker, name: `Empresa ${ticker}` }));

const strategy = {
  key: "moving_average",
  params: [
    { key: "short", label: "Média curta", kind: "int", default: 50, min: 5, max: 100, unit: "dias", hint: "" },
    {
      key: "share",
      label: "Quanto do caixa por compra",
      kind: "percent",
      default: 20,
      min: 5,
      max: 100,
      unit: "%",
      hint: "",
    },
    { key: "tickers", label: "Ações que ela opera", kind: "tickers", default: ["PETR4", "VALE3"], hint: "" },
  ],
} as unknown as StrategyInfo;

describe("paramPills", () => {
  it("marca só o que saiu do padrão", () => {
    const pills = paramPills(strategy, { short: 20, share: 20, tickers: ["PETR4", "VALE3"] });
    expect(pills.map((p) => p.changed)).toEqual([true, false, false]);
  });

  it("escreve o valor com a unidade", () => {
    const pills = paramPills(strategy, { short: 20, share: 30, tickers: ["PETR4"] });
    expect(pills.map((p) => p.value)).toEqual(["20 dias", "30%", "1 ação"]);
  });

  it("compara a lista de ações pela ordem e pelo conteúdo", () => {
    const pills = paramPills(strategy, { short: 50, share: 20, tickers: ["VALE3", "PETR4"] });
    expect(pills[2]?.changed).toBe(true);
  });
});

describe("inOptionOrder", () => {
  it("devolve as ações do conjunto na ordem das opções e ignora as que não existem", () => {
    expect(inOptionOrder(options("ITUB4", "PETR4", "VALE3"), ["VALE3", "XPTO3", "ITUB4"])).toEqual(["ITUB4", "VALE3"]);
  });
});

describe("sameTickerSet", () => {
  it("compara pelo conteúdo, sem ligar para a ordem", () => {
    expect(sameTickerSet(["PETR4", "VALE3"], ["VALE3", "PETR4"])).toBe(true);
    expect(sameTickerSet(["PETR4"], ["PETR4", "VALE3"])).toBe(false);
    expect(sameTickerSet([], [])).toBe(true);
  });
});

describe("profileValues", () => {
  const tickers = options("PETR4", "VALE3", "ITUB4");

  it("abre no padrão quando o perfil não tem nada salvo", () => {
    expect(profileValues(strategy, undefined, tickers)).toEqual({
      values: { short: 50, share: 20, tickers: ["PETR4", "VALE3"] },
      missing: [],
    });
  });

  it("usa o salvo e completa com o padrão o que falta", () => {
    const { values } = profileValues(strategy, { short: 20, tickers: ["ITUB4"] }, tickers);
    expect(values).toEqual({ short: 20, share: 20, tickers: ["ITUB4"] });
  });

  it("tira as ações que a partida não tem e as devolve para o aviso", () => {
    const { values, missing } = profileValues(strategy, { tickers: ["ITUB4", "XPTO3"] }, tickers);
    expect(values.tickers).toEqual(["ITUB4"]);
    expect(missing).toEqual(["XPTO3"]);
  });

  it("volta ao padrão quando nenhuma ação salva existe na partida", () => {
    const { values, missing } = profileValues(strategy, { tickers: ["XPTO3"] }, tickers);
    expect(values.tickers).toEqual(["PETR4", "VALE3"]);
    expect(missing).toEqual(["XPTO3"]);
  });
});
