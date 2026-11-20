import { describe, expect, it } from "vitest";
import { teamName, teamNameLookup, teamShortName } from "./teams";

describe("nome da equipe", () => {
  it("sem nome de gestora vale a cor ou o número da regra da partida", () => {
    expect(teamName(1, "COLOR")).toBe("Equipe Índigo");
    expect(teamName(1, "NUMBER")).toBe("Equipe 1");
    expect(teamShortName(2, "COLOR", null)).toBe("Carmim");
    expect(teamShortName(2, "NUMBER")).toBe("Equipe 2");
  });

  it("a equipe que leva o nome da gestora mostra só ele, em qualquer regra de nomes", () => {
    expect(teamName(1, "COLOR", "Aurora Capital")).toBe("Aurora Capital");
    expect(teamName(1, "NUMBER", "Aurora Capital")).toBe("Aurora Capital");
    expect(teamShortName(3, "COLOR", "Brisa")).toBe("Brisa");
  });
});

describe("nome da gestora por equipe", () => {
  const nameOf = teamNameLookup([
    { team: 1, name: "Aurora Capital" },
    { team: 2, name: null },
  ]);

  it("devolve o nome da gestora da equipe do jogador", () => {
    expect(nameOf(1)).toBe("Aurora Capital");
  });

  it("equipe sem gestora, desconhecida ou jogador sem equipe devolvem null", () => {
    expect(nameOf(2)).toBeNull();
    expect(nameOf(9)).toBeNull();
    expect(nameOf(null)).toBeNull();
    expect(nameOf(undefined)).toBeNull();
  });
});
