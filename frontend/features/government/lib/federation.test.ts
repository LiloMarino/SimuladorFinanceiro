import { describe, expect, it } from "vitest";
import type { ElectionParty } from "@/types";
import {
  federationCandidates,
  federationOf,
  partnerOf,
  raceFederationOf,
  raceRows,
  rejectionDelta,
} from "./federation";

function party(overrides: Partial<ElectionParty>): ElectionParty {
  return {
    id: 1,
    abbr: "PTD",
    is_computer: false,
    candidate: null,
    members: [],
    ...overrides,
  } as ElectionParty;
}

describe("federationCandidates", () => {
  it("lista os filiados do partido de jogadores, com o candidato atual primeiro", () => {
    const own = party({
      candidate: { nickname: "Bia", name: "Bia", color: null },
      members: [{ nickname: "Lilo" }, { nickname: "Bia" }] as ElectionParty["members"],
    });
    const partner = party({
      id: 2,
      abbr: "NOV",
      is_computer: true,
      candidate: { nickname: null, name: "Caio", color: null },
    });

    expect(federationCandidates(own, partner)).toEqual([
      { key: "1:Bia", partyId: 1, nickname: "Bia", label: "Bia", abbr: "PTD" },
      { key: "1:Lilo", partyId: 1, nickname: "Lilo", label: "Lilo", abbr: "PTD" },
      { key: "2:", partyId: 2, nickname: null, label: "Caio", abbr: "NOV" },
    ]);
  });
});

describe("rejectionDelta", () => {
  it("mostra a alta com sinal e esconde o que não muda", () => {
    expect(rejectionDelta({ own: "38", federated: "44" })).toBe("+6");
    expect(rejectionDelta({ own: "12", federated: "12" })).toBe("");
  });
});

describe("federationOf e partnerOf", () => {
  it("acha a federação do partido e o parceiro dele", () => {
    const federation = { parties: [1, 2] } as Parameters<typeof partnerOf>[0];
    expect(federationOf([federation], 2)).toBe(federation);
    expect(federationOf([federation], 3)).toBeUndefined();
    expect(partnerOf(federation, 1)).toBe(2);
  });
});

describe("raceRows", () => {
  const parties = [party({ id: 1, abbr: "PTD" }), party({ id: 2, abbr: "RPV" }), party({ id: 3, abbr: "NOV" })];
  const federation = { id: 9, election_year: 2027, parties: [1, 3], candidate_party_id: 3 } as Parameters<
    typeof partnerOf
  >[0];

  it("junta os dois partidos da federação da eleição numa linha, com o do candidato primeiro", () => {
    const rows = raceRows(parties, [federation], 2027);

    expect(rows.map((row) => row.parties.map((p) => p.abbr))).toEqual([["NOV", "PTD"], ["RPV"]]);
    expect(rows[0]?.federation).toBe(federation);
  });

  it("deixa os partidos separados quando a federação é de outra eleição", () => {
    const rows = raceRows(parties, [federation], 2031);

    expect(rows.map((row) => row.parties.length)).toEqual([1, 1, 1]);
    expect(raceFederationOf([federation], 2031, 1)).toBeUndefined();
  });
});
