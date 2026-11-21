import { describe, expect, it } from "vitest";
import { gameTypeWithoutExpansion } from "./expansion-game-type";

describe("tipo de partida ao desligar uma expansão", () => {
  it("o tipo que depende da expansão volta a Clássica", () => {
    expect(gameTypeWithoutExpansion("FUND_TAKEOVER", "funds")).toBe("CLASSIC");
    expect(gameTypeWithoutExpansion("POLITICAL", "government")).toBe("CLASSIC");
  });

  it("o tipo de outra expansão fica como está", () => {
    expect(gameTypeWithoutExpansion("FUND_TAKEOVER", "government")).toBe("FUND_TAKEOVER");
    expect(gameTypeWithoutExpansion("POLITICAL", "funds")).toBe("POLITICAL");
  });

  it("os tipos de qualquer partida ficam como estão", () => {
    expect(gameTypeWithoutExpansion("GOAL_RACE", "funds")).toBe("GOAL_RACE");
    expect(gameTypeWithoutExpansion("CLASSIC", "government")).toBe("CLASSIC");
  });
});
