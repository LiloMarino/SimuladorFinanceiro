import { describe, expect, it } from "vitest";
import type { Preparations } from "@/types";
import {
  cleanTickerLetters,
  fundChoice,
  fundFormSchema,
  fundFromForm,
  fundTabBadge,
  fundToForm,
  hasFundConflict,
  nameOwners,
  rivalFunds,
  tickerHint,
} from "./fund-preparation";

const assets = [
  { ticker: "PETR3", name: "Petrobras ON" },
  { ticker: "PETR4", name: "Petrobras PN" },
  { ticker: "VALE3", name: "Vale ON" },
];

const base = (funds: Preparations["funds"], fundConflicts: string[] = []): Preparations =>
  ({
    funds,
    conflicts: [],
    fund_conflicts: fundConflicts,
    fund_locked_reason: null,
    locked_reason: null,
  }) as unknown as Preparations;

const aurora = { nickname: "Ana", name: "Aurora Gestão", ticker: "AURO11" };
const bia = { nickname: "Bia", name: "Bia Investimentos", ticker: "BIAI11" };

describe("formulário da gestora", () => {
  it("a sigla salva vira as quatro letras e volta com o 11", () => {
    const form = fundToForm({ name: "Aurora Gestão", ticker: "AURO11" });
    expect(form).toEqual({ name: "Aurora Gestão", letters: "AURO" });
    expect(fundFromForm({ name: "  Aurora Gestão ", letters: "AURO" })).toEqual({
      name: "Aurora Gestão",
      ticker: "AURO11",
    });
  });

  it("sem gestora salva o formulário nasce em branco", () => {
    expect(fundToForm(null)).toEqual({ name: "", letters: "" });
  });

  it("o nome tem de 3 a 40 letras, sem contar as bordas", () => {
    const parse = (name: string) => fundFormSchema.safeParse({ name, letters: "AURO" }).success;
    expect(parse("ab")).toBe(false);
    expect(parse("  ab  ")).toBe(false);
    expect(parse("abc")).toBe(true);
    expect(parse("a".repeat(40))).toBe(true);
    expect(parse("a".repeat(41))).toBe(false);
  });

  it("a sigla são exatamente quatro letras maiúsculas", () => {
    const parse = (letters: string) => fundFormSchema.safeParse({ name: "Aurora", letters }).success;
    expect(parse("AURO")).toBe(true);
    expect(parse("AUR")).toBe(false);
    expect(parse("AURO1")).toBe(false);
    expect(parse("auro")).toBe(false);
  });

  it("o campo da sigla limpa o que digitam: maiúsculas, só letras, até quatro", () => {
    expect(cleanTickerLetters("au1ro-x")).toBe("AURO");
    expect(cleanTickerLetters("aurora")).toBe("AURO");
  });
});

describe("conferência da sigla e do nome", () => {
  it("falta letra: ainda não confere", () => {
    expect(tickerHint("AUR", assets, [])).toEqual({ status: "incomplete" });
  });

  it("as letras de uma ação da partida acusam todas as séries dela", () => {
    expect(tickerHint("PETR", assets, [])).toEqual({ status: "asset", assets: ["PETR3", "PETR4"] });
  });

  it("a sigla de outra gestora da sala acusa o dono", () => {
    expect(tickerHint("BIAI", assets, [bia])).toEqual({ status: "taken", owners: ["Bia"] });
  });

  it("sigla sem dono nem ativo está livre", () => {
    expect(tickerHint("AURO", assets, [bia])).toEqual({ status: "free" });
  });

  it("o nome igual ao de outra gestora acusa o dono, sem diferenciar maiúsculas", () => {
    expect(nameOwners("  BIA investimentos", [bia])).toEqual(["Bia"]);
    expect(nameOwners("Aurora Gestão", [bia])).toEqual([]);
    expect(nameOwners("  ", [bia])).toEqual([]);
  });

  it("os rivais são as gestoras dos outros jogadores", () => {
    expect(rivalFunds(base([aurora, bia]), "Ana")).toEqual([bia]);
  });
});

describe("conflitos da sala", () => {
  const asset = "Ana: as letras PETR da sigla PETR11 já são de um ativo.";

  it("nome repetido entre dois jogadores é conflito para os dois", () => {
    const funds = [aurora, { ...bia, name: "aurora gestão" }];
    expect(hasFundConflict(base(funds), "Ana")).toBe(true);
    expect(hasFundConflict(base(funds), "Bia")).toBe(true);
  });

  it("sigla repetida entre dois jogadores é conflito para os dois", () => {
    const funds = [aurora, { ...bia, ticker: "AURO11" }];
    expect(hasFundConflict(base(funds), "Ana")).toBe(true);
    expect(hasFundConflict(base(funds), "Bia")).toBe(true);
  });

  it("letras de ativo só pesam para quem escolheu a sigla", () => {
    const funds = [aurora, bia];
    const preparations = base(funds, [asset]);
    expect(hasFundConflict(preparations, "Ana")).toBe(true);
    expect(hasFundConflict(preparations, "Bia")).toBe(false);
  });

  it("quem não preparou gestora não tem conflito", () => {
    expect(hasFundConflict(base([bia]), "Ana")).toBe(false);
  });
});

describe("selo e escolha da aba", () => {
  it("expansão desligada: o selo diz que está desligada", () => {
    expect(fundTabBadge(false, base([]), "Ana")).toEqual({ label: "desligada nas regras", variant: "outline" });
  });

  it("gestora preparada sem conflito mostra a sigla", () => {
    expect(fundTabBadge(true, base([aurora, bia]), "Ana")).toEqual({ label: "AURO11", variant: "fund" });
  });

  it("gestora em conflito mostra o conflito", () => {
    const funds = [aurora, { ...bia, ticker: "AURO11" }];
    expect(fundTabBadge(true, base(funds), "Ana")).toEqual({ label: "em conflito", variant: "destructive" });
  });

  it("sem gestora preparada não há selo, e a aba abre em Sem gestora", () => {
    expect(fundTabBadge(true, base([bia]), "Ana")).toBeNull();
    expect(fundChoice(base([bia]), "Ana")).toBe("NONE");
    expect(fundChoice(base([aurora]), "Ana")).toBe("FOUND");
  });
});
