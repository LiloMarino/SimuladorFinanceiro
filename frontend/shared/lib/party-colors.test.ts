import { describe, expect, it } from "vitest";
import { defaultPartyColor, partyColor, partyForeground } from "./party-colors";

describe("partyColor", () => {
  it("usa a cor do partido de jogador e a paleta fixa no do computador", () => {
    expect(partyColor({ abbr: "PRL", color: "#15803D" })).toBe("#15803D");
    expect(partyColor({ abbr: "UPR", color: null })).toBe("#6B6B6B");
    expect(partyColor({ abbr: "ACI", color: null })).toBe("#0F7C9C");
    expect(partyColor({ abbr: "MNV", color: null })).toBe("#7E6B17");
  });
});

describe("partyForeground", () => {
  it("segue o texto da cor de jogador de mesmo hex e deixa branco fora da paleta", () => {
    expect(partyForeground("#209993")).toBe("var(--foreground)");
    expect(partyForeground("#2350D8")).toBe("var(--primary-foreground)");
    expect(partyForeground("#15803D")).toBe("var(--primary-foreground)");
  });
});

describe("defaultPartyColor", () => {
  it("marca a cor de quem funda quando está livre", () => {
    expect(defaultPartyColor("chart-3", [])).toBe("#809614");
  });

  it("cai na 1ª cor livre quando outro partido já usa a de quem funda", () => {
    expect(defaultPartyColor("chart-1", ["#2350d8"])).toBe("#209993");
    expect(defaultPartyColor(undefined, [])).toBe("#2350D8");
  });
});
