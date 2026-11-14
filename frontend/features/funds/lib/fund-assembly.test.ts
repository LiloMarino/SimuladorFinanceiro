import { describe, expect, it } from "vitest";
import type { FundDetails } from "@/types";
import { blockReason, missingText, tallyFractions, type AssemblyTally } from "./fund-assembly";

const tally = (over: Partial<AssemblyTally> = {}): AssemblyTally => ({
  in_favor: "200",
  against: "300",
  abstention: "500",
  total: "1000",
  missing_to_replace: "101",
  ...over,
});

const panel = (over: Partial<FundDetails["assembly"]> = {}): FundDetails["assembly"] => ({
  current: null,
  last_result: null,
  can_convene: false,
  block: null,
  convene_quotas: "100",
  my_quotas: "40",
  next_allowed_on: null,
  blocked_founding_until: null,
  ...over,
});

describe("tallyFractions", () => {
  it("cada trecho pesa a sua fatia do total de cotas", () => {
    expect(tallyFractions(tally())).toEqual({ favor: 0.2, abstention: 0.5, against: 0.3 });
  });

  it("sem cotas em circulação a barra fica vazia", () => {
    expect(tallyFractions(tally({ total: "0" }))).toEqual({ favor: 0, abstention: 0, against: 0 });
  });
});

describe("missingText", () => {
  it("diz quantas cotas faltam a favor e que empate mantém o gestor", () => {
    expect(missingText(tally())).toContain("Faltam 101 cotas a favor");
    expect(missingText(tally())).toContain("Empate mantém");
  });

  it("uma cota que falta fica no singular", () => {
    expect(missingText(tally({ missing_to_replace: "1" }))).toContain("Faltam 1 cota a favor");
  });

  it("sem cotas faltando a troca já vence", () => {
    expect(missingText(tally({ missing_to_replace: "0" }))).toContain("a gestão troca");
  });
});

describe("blockReason", () => {
  it("quem pode convocar não tem motivo de bloqueio", () => {
    expect(blockReason(panel({ can_convene: true }))).toBeNull();
  });

  it("menos de 10% conta o que falta para convocar", () => {
    expect(blockReason(panel({ block: "share" }))).toBe("Convocar exige 100 cotas (10% da gestora) e você tem 40.");
  });

  it("o intervalo de 3 meses diz quando a próxima pode ser convocada", () => {
    expect(blockReason(panel({ block: "interval", next_allowed_on: "2026-04-10" }))).toContain("a cada 3 meses");
  });

  it("cada motivo tem frase própria", () => {
    const reasons = (["pending", "manager", "unlisted"] as const).map((block) => blockReason(panel({ block })));
    expect(new Set(reasons).size).toBe(3);
  });
});
