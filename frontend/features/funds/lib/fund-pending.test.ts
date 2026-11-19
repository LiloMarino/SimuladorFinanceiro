import { describe, expect, it } from "vitest";
import type { FundDetails } from "@/types";
import { fundPending, fundPendingCount, rightsLeftOf } from "./fund-pending";

const invited = { user_id: 7, status: "INVITED" };
const offer = { buyer_user_id: 7 };
const issuance = { closed_on: null, phase: "preference", my_rights: "322", my_bought: "22" };

const fundWith = (parts: Record<string, unknown>) =>
  ({
    comanagers: [],
    directed_issuance: null,
    issuance: null,
    assembly: { current: [] },
    ...parts,
  }) as unknown as FundDetails;

describe("rightsLeftOf", () => {
  it("desconta o que o jogador já comprou do direito", () => {
    expect(rightsLeftOf({ my_rights: "322", my_bought: "22" })).toBe(300);
  });

  it("é zero sem direito ou com o direito esgotado", () => {
    expect(rightsLeftOf({ my_rights: null, my_bought: null })).toBe(0);
    expect(rightsLeftOf({ my_rights: "10", my_bought: "12" })).toBe(0);
  });
});

describe("fundPending", () => {
  it("conta convite, oferta dirigida a ele e preferência aberta", () => {
    const pending = fundPending(fundWith({ comanagers: [invited], directed_issuance: offer, issuance }), 7);

    expect(pending.preferenceLeft).toBe(300);
    expect(fundPendingCount(pending)).toBe(3);
  });

  it("conta a votação aberta que espera o voto do jogador", () => {
    const open = { status: "VOTING", can_vote: true, my_vote: null };
    const voted = { status: "VOTING", can_vote: true, my_vote: true };
    const pending = fundPending(fundWith({ assembly: { current: [open, voted] } }), 7);

    expect(pending.votes).toHaveLength(1);
    expect(fundPendingCount(pending)).toBe(1);
  });

  it("ignora a oferta dirigida a outro jogador e a preferência já encerrada", () => {
    const pending = fundPending(fundWith({ directed_issuance: offer, issuance: { ...issuance, phase: "open" } }), 8);

    expect(pending.directed).toBeUndefined();
    expect(fundPendingCount(pending)).toBe(0);
  });
});
