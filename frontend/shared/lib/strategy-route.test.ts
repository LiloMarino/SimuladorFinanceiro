import { describe, expect, it } from "vitest";
import type { FundAccount } from "@/types";
import { strategyFundId, strategyPaths, strategyRoute } from "./strategy-route";

const account = (overrides: Partial<FundAccount>): FundAccount => ({
  fund_id: null,
  name: "Conta pessoal",
  ticker: null,
  cash: "0",
  frozen_until: null,
  automatic: false,
  eliminated_on: null,
  role: null,
  ...overrides,
});

describe("strategyRoute", () => {
  it("a conta pessoal usa a rota pessoal", () => {
    expect(strategyRoute(account({}))).toEqual({ kind: "personal" });
  });

  it("sem lista de contas vale a rota pessoal", () => {
    expect(strategyRoute(undefined)).toEqual({ kind: "personal" });
  });

  it("com escolha de conta e a lista a caminho a rota fica pendente", () => {
    expect(strategyRoute(undefined, true)).toEqual({ kind: "pending" });
  });

  it("com a conta conhecida a lista a caminho não pesa", () => {
    expect(strategyRoute(account({}), true)).toEqual({ kind: "personal" });
    expect(strategyRoute(account({ fund_id: 7, name: "Alfa", role: "manager" }), true)).toEqual({
      kind: "fund",
      fundId: 7,
    });
  });

  it("a gestora usa a rota dela, pelo id", () => {
    expect(strategyRoute(account({ fund_id: 7, name: "Alfa", role: "manager" }))).toEqual({ kind: "fund", fundId: 7 });
    expect(strategyRoute(account({ fund_id: 7, name: "Alfa", role: "comanager" }))).toEqual({
      kind: "fund",
      fundId: 7,
    });
  });

  it("o Fundo Soberano não tem rota de automático", () => {
    expect(strategyRoute(account({ fund_id: 0, name: "Fundo Soberano", role: "president" }))).toEqual({
      kind: "sovereign",
    });
  });
});

describe("strategyFundId", () => {
  it("só a gestora tem id de rota", () => {
    expect(strategyFundId({ kind: "fund", fundId: 7 })).toBe(7);
    expect(strategyFundId({ kind: "personal" })).toBeNull();
    expect(strategyFundId({ kind: "sovereign" })).toBeNull();
    expect(strategyFundId({ kind: "pending" })).toBeNull();
  });
});

describe("strategyPaths", () => {
  it("a conta pessoal fala com /api/strategies", () => {
    const paths = strategyPaths(null);
    expect(paths.mine).toBe("/api/strategies/me");
    expect(paths.log).toBe("/api/strategies/me/log");
    expect(paths.view("rsi")).toBe("/api/strategies/rsi/view");
  });

  it("a gestora fala com /api/funds/{id}/strategy", () => {
    const paths = strategyPaths(7);
    expect(paths.mine).toBe("/api/funds/7/strategy");
    expect(paths.log).toBe("/api/funds/7/strategy/log");
    expect(paths.view("rsi")).toBe("/api/funds/7/strategy/rsi/view");
  });
});
