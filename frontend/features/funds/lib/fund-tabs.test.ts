import { describe, expect, it } from "vitest";
import { tabFrom, visibleTabs } from "./fund-tabs";

describe("visibleTabs", () => {
  it("dá ao gestor as oito abas na ordem da página", () => {
    expect(visibleTabs(true)).toEqual([
      "actions",
      "overview",
      "portfolio",
      "quotas",
      "income",
      "assembly",
      "report",
      "settings",
    ]);
  });

  it("tira a carteira e as configurações de quem não gere", () => {
    expect(visibleTabs(false)).toEqual(["actions", "overview", "quotas", "income", "assembly", "report"]);
  });
});

describe("tabFrom", () => {
  it("abre a aba pedida quando o jogador a vê", () => {
    expect(tabFrom("quotas", visibleTabs(false))).toBe("quotas");
  });

  it("cai em Suas ações para valor desconhecido, ausente ou de aba escondida", () => {
    expect(tabFrom("nope", visibleTabs(true))).toBe("actions");
    expect(tabFrom(null, visibleTabs(true))).toBe("actions");
    expect(tabFrom("settings", visibleTabs(false))).toBe("actions");
  });
});
