import { describe, expect, it } from "vitest";
import {
  type PromiseDraft,
  type PromiseOption,
  type PromiseRow,
  draftOf,
  isComplete,
  promiseKey,
  signedDecimal,
  stateLabel,
  stateSummary,
  toRequest,
  weightedSupport,
} from "./promises";

const options: PromiseOption[] = [{ kind: "DAY_TRADE_RATE", baseline: "0.15", step: "0.10", limit: "1" }];

describe("signedDecimal", () => {
  it("escreve o sinal e a vírgula", () => {
    expect(signedDecimal(1.2)).toBe("+1,2");
    expect(signedDecimal("-0.4")).toBe("−0,4");
    expect(signedDecimal(0)).toBe("0");
  });
});

describe("stateLabel", () => {
  it("mostra o caminho andado quando há andamento", () => {
    expect(stateLabel("IN_PROGRESS", "0.5")).toBe("Em andamento · 50%");
    expect(stateLabel("CONTRARY", "-0.5")).toBe("Na direção contrária · −50%");
    expect(stateLabel("FULFILLED", "1")).toBe("Cumprida");
  });
});

describe("stateSummary", () => {
  it("conta cada estado", () => {
    expect(stateSummary([{ state: "FULFILLED" }, { state: "IN_PROGRESS" }, { state: "CONTRARY" }])).toBe(
      "1 cumprida · 1 em andamento · 1 na direção contrária",
    );
  });
});

describe("rascunho", () => {
  it("só é completo com um alvo diferente do que vale hoje", () => {
    const draft: PromiseDraft = { kind: "DAY_TRADE_RATE", target: "0.15", sector: null, segment: null };
    expect(isComplete(draft, options)).toBe(false);
    expect(isComplete({ ...draft, target: "0.1" }, options)).toBe(true);
  });

  it("o setor escolhido já é uma promessa, sem alvo", () => {
    const draft: PromiseDraft = { kind: "SECTOR_EXEMPT", target: null, sector: "Energia", segment: null };
    expect(isComplete(draft, options)).toBe(true);
    expect(toRequest(draft)).toEqual({ kind: "SECTOR_EXEMPT", sector: "Energia", segment: null });
  });

  it("a medida de imposto leva o alvo e a chave distingue o setor", () => {
    const draft: PromiseDraft = { kind: "DAY_TRADE_RATE", target: "0.1", sector: null, segment: null };
    expect(toRequest(draft)).toEqual({ kind: "DAY_TRADE_RATE", target: "0.1" });
    expect(promiseKey(draft)).not.toBe(promiseKey({ ...draft, kind: "SECTOR_EXEMPT", sector: "Energia" }));
  });

  it("volta da promessa anunciada para o rascunho", () => {
    expect(
      draftOf({
        kind: "DAY_TRADE_RATE",
        title: "Ações · day trade em 10%",
        target: "0.1",
        baseline: "0.15",
        sector: null,
        segment: null,
        announced: "2022-03-02",
      }),
    ).toEqual({ kind: "DAY_TRADE_RATE", target: "0.1", sector: null, segment: null });
  });
});

describe("weightedSupport", () => {
  it("pesa o apoio de cada grupo pelo tamanho dele", () => {
    const rows = [
      { group: "INVESTORS", support: "5.5" },
      { group: "FORMAL_WORKERS", support: "-1.5" },
    ] as PromiseRow[];
    const groups: { group: "INVESTORS" | "FORMAL_WORKERS"; weight: string }[] = [
      { group: "INVESTORS", weight: "0.08" },
      { group: "FORMAL_WORKERS", weight: "0.35" },
    ];
    expect(weightedSupport(rows, groups)).toBeCloseTo(0.44 - 0.525);
  });
});
