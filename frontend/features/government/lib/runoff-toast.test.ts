import { describe, expect, it } from "vitest";
import type { GovernmentNotice } from "@/types";
import { endorsementToast, roundResultToast } from "./runoff-toast";

const notice = (overrides: Partial<GovernmentNotice>) =>
  ({ kind: "ELECTION_RESULT", ...overrides }) as GovernmentNotice;

describe("roundResultToast", () => {
  it("conta quem vai ao 2º turno e quem pode declarar apoio", () => {
    const toast = roundResultToast(
      notice({
        round: 1,
        winner_abbr: null,
        finalists: ["FDS", "PRL"],
        runoff: "2022-10-28",
        endorsers: { MRC: "Rafa" },
      }),
    );
    expect(toast.title).toBe("Resultado do 1º turno");
    expect(toast.description).toContain("FDS e PRL vão ao 2º turno, em 28 out");
    expect(toast.description).toContain("Rafa (MRC) pode declarar apoio a um dos dois.");
  });

  it("anuncia o vencedor com a fatia dos votos válidos", () => {
    const toast = roundResultToast(
      notice({
        round: 2,
        winner_abbr: "PRL",
        winner_name: "Lilo",
        winner_share: "0.507",
        inauguration: "2023-01-01",
      }),
    );
    expect(toast.tone).toBe("success");
    expect(toast.description).toContain("Lilo (PRL) venceu com 50,7% dos votos válidos");
    expect(toast.description).toContain("Posse em 01 jan");
  });
});

describe("endorsementToast", () => {
  const notice = (overrides: Partial<GovernmentNotice>) =>
    ({ kind: "ENDORSEMENT", actor: "Rafa", party_abbr: "MRC", rival_abbr: "PRL", ...overrides }) as GovernmentNotice;

  it("conta o apoio a um finalista", () => {
    expect(endorsementToast(notice({})).title).toBe("Rafa (MRC) declarou apoio ao PRL");
  });

  it("conta a neutralidade quando não há finalista", () => {
    const toast = endorsementToast(notice({ rival_abbr: null }));
    expect(toast.title).toBe("Rafa (MRC) declarou neutralidade");
  });
});
