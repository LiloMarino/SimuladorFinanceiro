import { describe, expect, it } from "vitest";
import { partyColor } from "./party-colors";

describe("partyColor", () => {
  it("usa a cor do partido de jogador e a paleta fixa no do computador", () => {
    expect(partyColor({ abbr: "PRL", color: "#15803D" })).toBe("#15803D");
    expect(partyColor({ abbr: "UPR", color: null })).toBe("#7D879B");
    expect(partyColor({ abbr: "ACI", color: null })).toBe("#0369A1");
    expect(partyColor({ abbr: "MNV", color: null })).toBe("#A16207");
  });
});
