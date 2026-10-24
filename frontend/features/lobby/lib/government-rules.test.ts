import { describe, expect, it } from "vitest";
import {
  campaignOpening,
  defaultFirstElection,
  difficultyExample,
  governmentRuleError,
  spansYears,
  wholeYears,
} from "./government-rules";

describe("spansYears", () => {
  it("conta o fim como alcançando o início mais N anos", () => {
    expect(spansYears("2020-01-01", "2025-01-01", 5)).toBe(true);
    expect(spansYears("2020-01-01", "2024-12-31", 5)).toBe(false);
  });

  it("recusa data incompleta", () => {
    expect(spansYears("2020-01-01", "01/2030", 5)).toBe(false);
  });
});

describe("wholeYears", () => {
  it("devolve os anos cheios da partida", () => {
    expect(wholeYears("2010-01-01", "2013-06-30")).toBe(3);
    expect(wholeYears("2010-01-01", "2030-12-31")).toBe(20);
  });
});

describe("defaultFirstElection", () => {
  it("cai em 7 de outubro do ano seguinte ao início", () => {
    expect(defaultFirstElection("2010-01-01", "2030-12-31")).toBe("2011-10-07");
  });

  it("não passa do fim da partida", () => {
    expect(defaultFirstElection("2010-01-01", "2011-06-30")).toBe("2011-06-30");
  });
});

describe("campaignOpening", () => {
  it("abre um ano antes da eleição", () => {
    expect(campaignOpening("2010-01-01", "2011-10-07")).toBe("2010-10-07");
  });

  it("não abre antes do início da partida", () => {
    expect(campaignOpening("2010-06-01", "2011-03-01")).toBe("2010-06-01");
  });
});

describe("governmentRuleError", () => {
  const ok = { start: "2010-01-01", end: "2030-12-31", firstElection: "2011-10-07" };

  it("aceita as datas certas", () => {
    expect(governmentRuleError(ok)).toBeNull();
  });

  it("pede 5 anos de partida", () => {
    expect(governmentRuleError({ ...ok, end: "2013-06-30" })?.path).toBe("endDate");
  });

  it("exige a primeira eleição dentro da partida", () => {
    expect(governmentRuleError({ ...ok, firstElection: "2010-01-01" })?.path).toBe("firstElection");
    expect(governmentRuleError({ ...ok, firstElection: "2031-01-01" })?.path).toBe("firstElection");
    expect(governmentRuleError({ ...ok, firstElection: "" })?.message).toBe("Escolha a data da primeira eleição.");
  });
});

describe("difficultyExample", () => {
  it("mostra a verba do computador sobre uma média de R$ 10.000", () => {
    expect(difficultyExample("EASY")).toContain("R$ 5.000");
    expect(difficultyExample("NORMAL")).toContain("R$ 10.000 por mês");
    expect(difficultyExample("HARD")).toContain("R$ 15.000");
  });
});
