import { describe, expect, it } from "vitest";
import type { ElectionPanel } from "@/types";
import { donationContext, roundToast } from "./round-toast";

const party = (id: number, abbr: string, share: string) => ({
  party_id: id,
  abbr,
  name: abbr,
  color: null,
  is_computer: false,
  candidate: null,
  vice: null,
  points: share,
  share,
});

/** 1º turno: FDS 38%, UPR 36%, PRL 26% — ninguém passa de 50%, FDS e UPR vão ao 2º turno */
function panelFor(myParty: number, winner: number | null = null, round = 1) {
  return {
    my_party: { party_id: myParty },
    dates: { runoff: "2018-10-28", donation_deadline: "2018-10-27" },
    last_result: {
      round,
      winner,
      finalists: [1, 2],
      parties: [party(1, "FDS", "0.38"), party(2, "UPR", "0.36"), party(3, "PRL", "0.26")],
    },
  } as unknown as ElectionPanel;
}

describe("roundToast", () => {
  it("avisa o finalista que enfrenta o rival e a data do 2º turno", () => {
    const toast = roundToast(panelFor(1));
    expect(toast?.title).toBe("Seu partido vai ao 2º turno");
    expect(toast?.description).toContain("enfrenta o UPR");
    expect(toast?.description).toContain("38%");
  });

  it("avisa quem ficou fora com a posição e o convite a doar", () => {
    const toast = roundToast(panelFor(3));
    expect(toast?.title).toBe("O PRL ficou fora do 2º turno");
    expect(toast?.description).toContain("3º lugar");
    expect(toast?.donate).toBe(true);
  });

  it("comemora a vitória do partido de quem vê", () => {
    expect(roundToast(panelFor(1, 1, 2))?.tone).toBe("success");
  });

  it("não avisa quem não tem partido", () => {
    const panel = { ...panelFor(1), my_party: null } as unknown as ElectionPanel;
    expect(roundToast(panel)).toBeNull();
  });
});

describe("donationContext", () => {
  const panel = {
    parties: [{ id: 1, abbr: "FDS" }, { id: 2, abbr: "UPR" }],
    runoff_simulation: { winner: 1 },
  } as unknown as ElectionPanel;

  it("diz contra quem lidera quando a doação vai ao outro finalista", () => {
    expect(donationContext(panel, "UPR")).toBe("Contra o FDS, que lidera a simulação do 2º turno.");
  });

  it("diz a favor quando a doação vai a quem lidera", () => {
    expect(donationContext(panel, "FDS")).toBe("A favor do FDS, que lidera a simulação do 2º turno.");
  });
});
