import { describe, expect, it } from "vitest";
import type { VoterValue } from "@/types";
import { lockReason } from "./party-flags";

describe("lockReason", () => {
  it("trava a bandeira que a escolhida exclui", () => {
    expect(lockReason("SOCIAL_JUSTICE", ["FREE_MARKET"])).toBe("Exclui Mercado livre");
  });

  it("trava as outras quando já são 3, e solta as escolhidas", () => {
    const chosen: VoterValue[] = ["FREE_MARKET", "STABILITY", "DEVELOPMENT"];
    expect(lockReason("PUBLIC_SERVICE", chosen)).toBe("Já são 3: tire uma");
    expect(lockReason("STABILITY", chosen)).toBeNull();
  });
});
