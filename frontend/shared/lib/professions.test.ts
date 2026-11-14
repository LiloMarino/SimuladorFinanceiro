import { describe, expect, it } from "vitest";
import { availableProfessions, PROFESSIONS, visibleProfession, type RoomRules } from "./professions";

const room = (overrides: Partial<RoomRules> = {}): RoomRules => ({
  government_enabled: true,
  inflation_adjusted: true,
  monthly_salary: "5000",
  ...overrides,
});

describe("visibleProfession", () => {
  it("na sala padrão mostra tudo da profissão", () => {
    const clt = visibleProfession("CLT", room());
    expect(clt.gains).toHaveLength(2);
    expect(clt.tags).toEqual(["unemployment", "gdp", "personalTax"]);
  });

  it("sem Governo saem os impostos e os aumentos dos servidores e aposentados", () => {
    const noGovernment = room({ government_enabled: false });
    expect(visibleProfession("CLT", noGovernment).tags).toEqual(["unemployment", "gdp"]);
    expect(visibleProfession("PUBLIC_SERVANT", noGovernment).tags).toEqual([]);
    expect(visibleProfession("PUBLIC_SERVANT", noGovernment).gains).toEqual([{ text: "Nunca é demitido" }]);
    expect(visibleProfession("WELFARE", noGovernment).tags).toEqual(["unemployment"]);
  });

  it("sem correção pela inflação sai o aumento acima da inflação e o aluguel que só sobe com ela", () => {
    const noInflation = room({ inflation_adjusted: false });
    expect(visibleProfession("CLT", noInflation).gains).toEqual([{ text: "Renda cheia" }]);
    expect(visibleProfession("CLT", noInflation).tags).toContain("gdp");
    expect(visibleProfession("PUBLIC_SERVANT", noInflation).tags).toEqual(["personalTax"]);
    expect(visibleProfession("LANDLORD", noInflation).losses).toHaveLength(1);
  });
});

describe("availableProfessions", () => {
  it("na sala com correção pela inflação oferece as doze", () => {
    expect(availableProfessions(room())).toHaveLength(Object.keys(PROFESSIONS).length);
    expect(availableProfessions(room())).toContain("FREELANCER");
  });

  it("sem correção pela inflação o Autônomo some e as outras ficam na mesma ordem", () => {
    const withInflation = availableProfessions(room());
    const without = availableProfessions(room({ inflation_adjusted: false }));
    expect(without).not.toContain("FREELANCER");
    expect(without).toEqual(withInflation.filter((profession) => profession !== "FREELANCER"));
  });
});

describe("visibleProfession das profissões novas", () => {
  it("o Herdeiro não tem etiqueta: sem renda de trabalho nada mexe nela", () => {
    expect(visibleProfession("HEIR", room()).tags).toEqual([]);
  });

  it("cada profissão de variável traz a etiqueta dela", () => {
    expect(visibleProfession("EXPORTER", room()).tags).toEqual(["dollar", "corporateTax"]);
    expect(visibleProfession("BANKER", room()).tags).toEqual(["unemployment", "selic", "personalTax"]);
    expect(visibleProfession("BROKER", room()).tags).toEqual(["stocks", "personalTax"]);
  });
});
