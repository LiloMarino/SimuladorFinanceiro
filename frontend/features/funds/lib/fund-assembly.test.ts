import { describe, expect, it } from "vitest";
import type { FundDetails } from "@/types";
import {
  blockReason,
  currentOf,
  currentTitle,
  feeTitle,
  isApproved,
  missingText,
  optionOf,
  participation,
  resultScore,
  resultTitle,
  voteShares,
  votesToCastOf,
  type AssemblyCurrent,
  type AssemblyFee,
  type AssemblyOption,
  type AssemblyResult,
  type AssemblyTally,
} from "./fund-assembly";

type Panel = FundDetails["assembly"];

const tally = (over: Partial<AssemblyTally> = {}): AssemblyTally => ({
  in_favor: "200",
  against: "300",
  abstention: "500",
  total: "1000",
  missing_to_win: "101",
  ...over,
});

const fee = (over: Partial<AssemblyFee> = {}): AssemblyFee => ({
  management_from: "0.015000",
  management_to: "0.020000",
  performance_from: "0.200000",
  performance_to: "0.200000",
  ...over,
});

const current = (over: Partial<AssemblyCurrent> = {}): AssemblyCurrent => ({
  id: 1,
  agenda: "REPLACE_MANAGER",
  status: "VOTING",
  convener_user_id: 2,
  convener_nickname: "Ana",
  candidate_user_id: 3,
  candidate_nickname: "Bia",
  fee: null,
  merge: null,
  called_on: "2026-11-18",
  started_on: "2026-11-18",
  ends_on: "2026-11-24",
  session: 1,
  sessions: 5,
  tally: tally(),
  voters: [],
  non_voting: "0",
  my_vote: null,
  can_vote: true,
  ...over,
});

const option = (over: Partial<AssemblyOption> = {}): AssemblyOption => ({
  agenda: "REPLACE_MANAGER",
  can_convene: false,
  block: null,
  next_allowed_on: null,
  ...over,
});

const panel = (over: Partial<Panel> = {}): Panel => ({
  current: [],
  history: [],
  options: [],
  merge_partners: [],
  convene_quotas: "100",
  my_quotas: "40",
  blocked_founding_until: null,
  ...over,
});

const result = (over: Partial<AssemblyResult> = {}): AssemblyResult => ({
  id: 9,
  agenda: "REPLACE_MANAGER",
  status: "KEPT",
  convener_nickname: "Bia",
  candidate_nickname: "Bia",
  previous_manager_nickname: "Ana",
  started_on: "2026-10-27",
  closed_on: "2026-11-02",
  tally: tally({ in_favor: "182", against: "818" }),
  fee: null,
  effective_on: null,
  partner_ticker: null,
  partner_name: null,
  absorbed: false,
  merge_shortfall: null,
  ...over,
});

describe("votações abertas", () => {
  it("acha a votação e a pauta de cada agenda", () => {
    const base = panel({
      current: [current(), current({ id: 2, agenda: "FEE_INCREASE" })],
      options: [option({ agenda: "FEE_INCREASE" })],
    });
    expect(currentOf(base, "FEE_INCREASE")?.id).toBe(2);
    expect(currentOf(panel(), "FEE_INCREASE")).toBeUndefined();
    expect(optionOf(base, "FEE_INCREASE")?.agenda).toBe("FEE_INCREASE");
  });

  it("só espera o voto de quem pode votar e ainda não votou numa votação aberta", () => {
    const base = panel({
      current: [
        current({ id: 1 }),
        current({ id: 2, my_vote: true }),
        current({ id: 3, can_vote: false }),
        current({ id: 4, status: "INVITED" }),
      ],
    });
    expect(votesToCastOf(base).map((assembly) => assembly.id)).toEqual([1]);
  });
});

describe("títulos", () => {
  it("a fusão se lê pelo lado de quem consulta", () => {
    const side = (name: string) => ({ fund_id: 1, ticker: "X11", name, nav: "100", cash: "0" });
    const merge = (is_mother: boolean) => ({
      mother: side("Aurora Gestão"),
      daughter: side("Boreal Renda"),
      is_mother,
      ratio: "0.5",
      partner_tally: tally(),
      partner_voted_share: "0.5",
      partner_in_favor_share: null,
      exit_quotas: "0",
      exit_amount: "0",
      shortfall: "0",
    });
    expect(currentTitle(current({ agenda: "MERGE", merge: merge(true) }))).toBe("Incorporar a Boreal Renda");
    expect(currentTitle(current({ agenda: "MERGE", merge: merge(false) }))).toBe("Ser incorporada pela Aurora Gestão");
    expect(resultTitle(result({ agenda: "MERGE", partner_name: "Boreal Renda" }))).toBe("Incorporar a Boreal Renda");
    expect(resultTitle(result({ agenda: "MERGE", partner_name: "Aurora Gestão", absorbed: true }))).toBe(
      "Ser incorporada pela Aurora Gestão",
    );
  });

  it("o aumento diz qual taxa sobe, de quanto para quanto", () => {
    expect(feeTitle(fee())).toBe("Aumento da taxa de administração (1,5% para 2%)");
    expect(feeTitle(fee({ management_to: "0.015000", performance_to: "0.250000" }))).toBe(
      "Aumento da taxa de performance (20% para 25%)",
    );
  });

  it("duas taxas no mesmo pedido saem juntas", () => {
    expect(feeTitle(fee({ performance_to: "0.250000" }))).toBe(
      "Aumento das taxas (administração 1,5% para 2%; performance 20% para 25%)",
    );
  });

  it("a troca de gestor leva o nome do candidato", () => {
    expect(currentTitle(current())).toBe("Trocar o gestor por Bia");
    expect(currentTitle(current({ agenda: "FEE_INCREASE", fee: fee() }))).toContain("Aumento da taxa");
    expect(resultTitle(result())).toBe("Trocar o gestor (Ana por Bia)");
  });
});

describe("placar", () => {
  it("o peso de cada lado é entre as cotas que votaram", () => {
    expect(voteShares(tally())).toEqual({ favor: 0.4, against: 0.6 });
  });

  it("sem voto nenhum, nenhum lado pesa", () => {
    expect(voteShares(tally({ in_favor: "0", against: "0" }))).toEqual({ favor: 0, against: 0 });
  });

  it("a participação desconta quem não vota do total", () => {
    expect(participation(tally(), "200")).toEqual({ voted: 500, eligible: 800, share: 0.625 });
    expect(participation(tally({ total: "0" }), "0").share).toBe(0);
  });

  it("o resultado diz quanto foi a favor e quando vale", () => {
    expect(resultScore(result())).toBe("18,2% a favor");
    expect(resultScore(result({ effective_on: "2026-12-01" }))).toContain("vale a partir de 01/12/2026");
    expect(resultScore(result({ tally: tally({ in_favor: "0", against: "0" }) }))).toBe("sem votos");
  });

  it("aprovada é a troca feita ou o aumento aprovado", () => {
    expect(isApproved({ status: "REPLACED" })).toBe(true);
    expect(isApproved({ status: "APPROVED" })).toBe(true);
    expect(isApproved({ status: "KEPT" })).toBe(false);
    expect(isApproved({ status: "REJECTED" })).toBe(false);
  });
});

describe("missingText", () => {
  it("diz quantas cotas faltam a favor e que empate mantém o gestor", () => {
    expect(missingText(tally(), "REPLACE_MANAGER")).toContain("Faltam 101 cotas a favor");
    expect(missingText(tally(), "REPLACE_MANAGER")).toContain("Empate mantém");
  });

  it("no aumento, empate ou sem votos mantém a taxa", () => {
    expect(missingText(tally(), "FEE_INCREASE")).toContain("a taxa subir");
    expect(missingText(tally(), "FEE_INCREASE")).toContain("mantém a taxa");
  });

  it("na fusão, empate ou sem votos mantém as duas separadas", () => {
    expect(missingText(tally(), "MERGE")).toContain("a fusão sair");
    expect(missingText(tally(), "MERGE")).toContain("mantém as duas separadas");
  });

  it("uma cota que falta fica no singular", () => {
    expect(missingText(tally({ missing_to_win: "1" }), "REPLACE_MANAGER")).toContain("Faltam 1 cota a favor");
  });

  it("sem cotas faltando a pauta já vence", () => {
    expect(missingText(tally({ missing_to_win: "0" }), "REPLACE_MANAGER")).toContain("a gestão trocar");
  });
});

describe("blockReason", () => {
  it("quem pode convocar não tem motivo de bloqueio", () => {
    expect(blockReason(option({ can_convene: true }), panel())).toBeNull();
    expect(blockReason(undefined, panel())).toBeNull();
  });

  it("menos de 10% conta o que falta para convocar", () => {
    expect(blockReason(option({ block: "share" }), panel())).toBe(
      "Convocar exige 100 cotas (10% da gestora) e você tem 40.",
    );
  });

  it("o intervalo de 3 meses diz quando a próxima pode ser convocada", () => {
    expect(blockReason(option({ block: "interval", next_allowed_on: "2026-04-10" }), panel())).toContain(
      "a cada 3 meses",
    );
    expect(blockReason(option({ block: "grace", next_allowed_on: "2027-01-01" }), panel())).toContain(
      "depois da carência",
    );
  });

  it("só o gestor propõe aumento de taxa", () => {
    expect(blockReason(option({ agenda: "FEE_INCREASE", block: "manager_only" }), panel())).toBe(
      "Só o gestor propõe aumento de taxa.",
    );
  });

  it("a fusão em votação diz até quando", () => {
    expect(blockReason(option({ agenda: "MERGE", block: "pending", next_allowed_on: "2026-11-24" }), panel())).toBe(
      "Já há uma fusão em votação até 24/11.",
    );
  });

  it("a fusão tem frase própria para quem não é o gestor", () => {
    expect(blockReason(option({ agenda: "MERGE", block: "manager_only" }), panel())).toBe(
      "Só o gestor propõe a fusão.",
    );
  });

  it("a gestora congelada diz até quando", () => {
    expect(blockReason(option({ agenda: "MERGE", block: "frozen", next_allowed_on: "2027-03-01" }), panel())).toContain(
      "congelada até 01/03/2027",
    );
  });

  it("a troca de gestor e a fusão se seguram uma à outra", () => {
    expect(blockReason(option({ agenda: "MERGE", block: "swap_open" }), panel())).toContain("troca de gestor");
    expect(blockReason(option({ block: "merge_open", next_allowed_on: "2026-11-24" }), panel())).toBe(
      "Há uma fusão em votação até 24/11: a troca de gestor espera o resultado dela.",
    );
  });

  it("cada motivo tem frase própria", () => {
    const reasons = (
      [
        "pending",
        "manager",
        "unlisted",
        "manager_only",
        "no_partner",
        "busy",
        "frozen",
        "swap_open",
        "merge_open",
      ] as const
    ).map((block) => blockReason(option({ block }), panel()));
    expect(new Set(reasons).size).toBe(9);
  });
});
