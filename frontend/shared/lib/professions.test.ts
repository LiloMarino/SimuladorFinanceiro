import { describe, expect, it } from "vitest";
import {
  availableBotProfessions,
  availableProfessions,
  EXPANSION_NAME,
  PROFESSIONS,
  visibleProfession,
  type RoomRules,
} from "./professions";

const room = (overrides: Partial<RoomRules> = {}): RoomRules => ({
  funds_enabled: true,
  government_enabled: true,
  inflation_adjusted: true,
  monthly_salary: "5000",
  start_date: "2010-01-01",
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

  it("sem correção pela inflação sai o aumento acima da inflação", () => {
    const noInflation = room({ inflation_adjusted: false });
    expect(visibleProfession("CLT", noInflation).gains).toEqual([{ text: "Renda cheia" }]);
    expect(visibleProfession("CLT", noInflation).tags).toContain("gdp");
    expect(visibleProfession("PUBLIC_SERVANT", noInflation).tags).toEqual(["personalTax"]);
  });

  it("o Locador mostra as vantagens, as desvantagens e as etiquetas dos imóveis em qualquer sala", () => {
    const landlord = visibleProfession("LANDLORD", room({ inflation_adjusted: false }));
    expect(landlord.gains).toHaveLength(2);
    expect(landlord.losses).toHaveLength(2);
    expect(landlord.tags).toEqual(["unemployment", "gdp", "personalTax"]);
    expect(visibleProfession("LANDLORD", room({ government_enabled: false })).tags).toEqual(["unemployment", "gdp"]);
  });
});

describe("availableProfessions", () => {
  it("na sala com correção pela inflação, as duas expansões e início depois do IVG-R oferece todas", () => {
    expect(availableProfessions(room())).toHaveLength(Object.keys(PROFESSIONS).length);
    expect(availableProfessions(room())).toContain("FREELANCER");
  });

  it("sem correção pela inflação o Autônomo some e as outras ficam na mesma ordem", () => {
    const withInflation = availableProfessions(room());
    const without = availableProfessions(room({ inflation_adjusted: false }));
    expect(without).not.toContain("FREELANCER");
    expect(without).toEqual(withInflation.filter((profession) => profession !== "FREELANCER"));
  });

  it("sem a expansão a profissão dela some", () => {
    expect(availableProfessions(room({ government_enabled: false }))).not.toContain("COMMISSIONED");
    expect(availableProfessions(room({ funds_enabled: false }))).not.toContain("OFFERS_BANKER");
    expect(availableProfessions(room({ funds_enabled: false }))).toContain("COMMISSIONED");
  });

  it("o Locador só aparece em sala que começa no primeiro mês do IVG-R ou depois", () => {
    expect(availableProfessions(room({ start_date: "2000-01-01" }))).not.toContain("LANDLORD");
    expect(availableProfessions(room({ start_date: "2001-02-01" }))).not.toContain("LANDLORD");
    expect(availableProfessions(room({ start_date: "2001-03-01" }))).toContain("LANDLORD");
    expect(availableProfessions(room({ start_date: "2019-01-01" }))).toContain("LANDLORD");
  });

  it("o bot também não recebe o Locador em sala que começa antes do IVG-R", () => {
    expect(availableBotProfessions(room({ start_date: "2000-01-01" }))).not.toContain("LANDLORD");
    expect(availableBotProfessions(room({ start_date: "2001-03-01" }))).toContain("LANDLORD");
  });

  it("o bot não recebe o Comissionado, que segue o partido escolhido pelo jogador", () => {
    expect(availableBotProfessions(room())).not.toContain("COMMISSIONED");
    expect(availableBotProfessions(room())).toContain("OFFERS_BANKER");
  });
});

describe("visibleProfession das profissões novas", () => {
  it("o Herdeiro não tem etiqueta: sem renda de trabalho nada mexe nela", () => {
    expect(visibleProfession("HEIR", room()).tags).toEqual([]);
  });

  it("cada profissão de variável traz a etiqueta dela", () => {
    expect(visibleProfession("EXPORTER", room()).tags).toEqual(["dollar", "corporateTax"]);
    expect(visibleProfession("BANKER", room()).tags).toEqual(["unemployment", "selic", "personalTax"]);
    expect(visibleProfession("BROKER", room()).tags).toEqual(["personalTax"]);
  });
});

describe("selos do card", () => {
  it("só o Herdeiro é difícil", () => {
    const hard = (Object.keys(PROFESSIONS) as (keyof typeof PROFESSIONS)[]).filter((p) => PROFESSIONS[p].hard);
    expect(hard).toEqual(["HEIR"]);
  });

  it("as profissões das expansões levam o nome da expansão e as outras não", () => {
    const requires = (profession: keyof typeof PROFESSIONS) =>
      EXPANSION_NAME[PROFESSIONS[profession].requires ?? "inflationAdjusted"];
    expect(requires("COMMISSIONED")).toBe("Governo & Política");
    expect(requires("OFFERS_BANKER")).toBe("Gestoras");
    expect(requires("CLT")).toBeUndefined();
    expect(requires("FREELANCER")).toBeUndefined();
  });
});
