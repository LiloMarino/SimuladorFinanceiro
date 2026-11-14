import { afterEach, describe, expect, it, vi } from "vitest";
import type { FundAccount } from "@/types";
import {
  accountHeaders,
  getSelectedFundId,
  resolveActiveAccount,
  selectFund,
  subscribeActiveAccount,
} from "./active-account";

const personal: FundAccount = {
  fund_id: null,
  name: "Conta pessoal",
  ticker: null,
  cash: "1000.00",
  frozen_until: null,
};
const aurora: FundAccount = {
  fund_id: 3,
  name: "Aurora Gestão",
  ticker: "AURO11",
  cash: "96300.00",
  frozen_until: null,
};

// Partida própria deste arquivo: o estado do módulo é compartilhado entre os testes
const SIMULATION = 9001;

afterEach(() => {
  selectFund(SIMULATION, null);
  vi.unstubAllGlobals();
});

describe("conta escolhida", () => {
  it("começa na conta pessoal e lembra a gestora escolhida", () => {
    expect(getSelectedFundId(SIMULATION)).toBeNull();
    selectFund(SIMULATION, 3);
    expect(getSelectedFundId(SIMULATION)).toBe(3);
  });

  it("avisa quem acompanha a escolha", () => {
    const listener = vi.fn();
    const stop = subscribeActiveAccount(listener);
    selectFund(SIMULATION, 3);
    stop();
    selectFund(SIMULATION, null);
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it("guarda a escolha no navegador, por partida", () => {
    const store = new Map<string, string>();
    vi.stubGlobal("localStorage", {
      getItem: (key: string) => store.get(key) ?? null,
      setItem: (key: string, value: string) => store.set(key, value),
      removeItem: (key: string) => store.delete(key),
    });
    selectFund(SIMULATION, 3);
    expect(store.get(`active-account:${SIMULATION}`)).toBe("3");
    selectFund(SIMULATION, null);
    expect(store.has(`active-account:${SIMULATION}`)).toBe(false);
  });

  it("a escolha vale mesmo sem armazenamento no navegador", () => {
    vi.stubGlobal("localStorage", {
      getItem: () => {
        throw new Error("bloqueado");
      },
      setItem: () => {
        throw new Error("bloqueado");
      },
      removeItem: () => {
        throw new Error("bloqueado");
      },
    });
    selectFund(SIMULATION, 3);
    expect(getSelectedFundId(SIMULATION)).toBe(3);
  });
});

describe("conta em uso", () => {
  it("é a gestora escolhida enquanto ela está na lista", () => {
    expect(resolveActiveAccount([personal, aurora], 3)).toBe(aurora);
  });

  it("uma gestora que sumiu da lista volta para a pessoal", () => {
    expect(resolveActiveAccount([personal], 3)).toBe(personal);
  });

  it("sem lista não há conta em uso", () => {
    expect(resolveActiveAccount(undefined, 3)).toBeUndefined();
  });
});

describe("cabeçalho da conta", () => {
  it("a conta pessoal não envia cabeçalho", () => {
    expect(accountHeaders(null, [personal, aurora])).toEqual({});
  });

  it("a gestora escolhida vai em X-Account", () => {
    expect(accountHeaders(3, [personal, aurora])).toEqual({ "X-Account": "3" });
  });

  it("antes da lista a escolha lembrada segue valendo", () => {
    expect(accountHeaders(3, undefined)).toEqual({ "X-Account": "3" });
  });

  it("uma gestora fora da lista carregada não é enviada", () => {
    expect(accountHeaders(3, [personal])).toEqual({});
  });
});
