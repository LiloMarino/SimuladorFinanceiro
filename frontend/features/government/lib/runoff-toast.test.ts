import { describe, expect, it } from "vitest";
import type { ElectionPanel, ElectionRound, GovernmentNotice } from "@/types";
import { endorsementToast, roundResultToast } from "./runoff-toast";

const panel = {
  dates: { runoff: "2022-10-28", inauguration: "2023-01-01" },
  parties: [
    { id: 1, abbr: "FDS", founder: "Bia" },
    { id: 2, abbr: "PRL", founder: "Lilo" },
    { id: 3, abbr: "MRC", founder: "Rafa" },
  ],
} as unknown as ElectionPanel;

const party = (id: number, abbr: string, share: string, name: string) => ({
  party_id: id,
  abbr,
  share,
  candidate: { name },
});

describe("roundResultToast", () => {
  it("conta quem vai ao 2º turno e quem pode declarar apoio", () => {
    const result = {
      round: 1,
      winner: null,
      finalists: [1, 2],
      parties: [party(1, "FDS", "0.387", "Bia"), party(2, "PRL", "0.347", "Lilo"), party(3, "MRC", "0.266", "Rafa")],
    } as unknown as ElectionRound;
    const toast = roundResultToast(panel, result);
    expect(toast.title).toBe("Resultado do 1º turno");
    expect(toast.description).toContain("FDS e PRL vão ao 2º turno, em 28 out");
    expect(toast.description).toContain("Rafa (MRC) pode declarar apoio a um dos dois.");
  });

  it("anuncia o vencedor com a fatia dos votos válidos", () => {
    const result = {
      round: 2,
      winner: 2,
      finalists: [1, 2],
      parties: [party(1, "FDS", "0.493", "Bia"), party(2, "PRL", "0.507", "Lilo")],
    } as unknown as ElectionRound;
    const toast = roundResultToast(panel, result);
    expect(toast.tone).toBe("success");
    expect(toast.description).toContain("Lilo (PRL) venceu com 50,7% dos votos válidos");
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
