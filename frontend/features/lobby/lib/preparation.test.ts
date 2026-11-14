import { describe, expect, it } from "vitest";
import type { Preparations } from "@/types";
import { cashShare, closeRivalTag, federationCandidates, federationPartners, partyOf, rivalsOf } from "./preparation";

const PREPARATIONS: Preparations = {
  players: [
    {
      nickname: "Lilo",
      kind: "FOUND",
      party: {
        name: "Partido Liberal",
        abbr: "PRL",
        color: "#15803D",
        flags: ["FREE_MARKET", "STABILITY", "SAVER_PROTECTION"],
      },
      founder: null,
      candidate: "Duda",
      vice: null,
      vice_accepted: false,
      federation: null,
    },
    {
      nickname: "Duda",
      kind: "JOIN",
      party: null,
      founder: "Lilo",
      candidate: null,
      vice: null,
      vice_accepted: false,
      federation: null,
    },
    {
      nickname: "Caio",
      kind: "NONE",
      party: null,
      founder: null,
      candidate: null,
      vice: null,
      vice_accepted: false,
      federation: null,
    },
  ],
  reserved: [{ name: "Movimento Nacional", abbr: "MNV", flags: ["FREE_MARKET", "STABILITY", "DEVELOPMENT"] }],
  conflicts: [],
  funds: [],
  fund_locked_reason: null,
  pending_invites: 0,
  radar_neutral: "30",
  radar_flag: "80",
  locked_reason: null,
};

describe("rivalsOf", () => {
  it("junta os partidos do computador e os dos outros fundadores", () => {
    expect(rivalsOf(PREPARATIONS, "Caio").map((rival) => rival.abbr)).toEqual(["MNV", "PRL"]);
  });

  it("deixa de fora o partido do próprio jogador", () => {
    expect(rivalsOf(PREPARATIONS, "Lilo").map((rival) => rival.abbr)).toEqual(["MNV"]);
  });
});

describe("closeRivalTag", () => {
  it("marca as bandeiras repetidas do rival com 2 ou mais em comum", () => {
    const tag = closeRivalTag(["FREE_MARKET", "STABILITY", "PUBLIC_SERVICE"], rivalsOf(PREPARATIONS, "Caio"));
    expect(tag("FREE_MARKET")).toBe("MNV, PRL também");
    expect(tag("PUBLIC_SERVICE")).toBeNull();
  });

  it("não marca nada com só 1 bandeira em comum", () => {
    const tag = closeRivalTag(["DEVELOPMENT", "PUBLIC_SERVICE"], rivalsOf(PREPARATIONS, "Caio"));
    expect(tag("DEVELOPMENT")).toBeNull();
  });
});

describe("partyOf", () => {
  it("dá ao filiado o partido do fundador e diz quem encabeça a chapa", () => {
    expect(partyOf(PREPARATIONS, "Duda")).toMatchObject({ founder: "Lilo", candidate: true });
    expect(partyOf(PREPARATIONS, "Lilo")).toMatchObject({ founder: "Lilo", candidate: false });
  });

  it("é nulo para quem fica sem partido", () => {
    expect(partyOf(PREPARATIONS, "Caio")).toBeNull();
  });
});

describe("cashShare", () => {
  it("dá o peso da contribuição no saldo inicial", () => {
    expect(cashShare("500", "100000")).toBe("0,5%");
  });

  it("é zero sem saldo inicial", () => {
    expect(cashShare("500", "0")).toBe("0%");
  });
});

describe("federationPartners", () => {
  const founder = (nickname: string, federated: boolean): Preparations["players"][number] => ({
    ...PREPARATIONS.players[0]!,
    nickname,
    federation: federated ? { partner: "Lilo", name: "Federação", candidate: "Lilo" } : null,
  });

  it("lista os outros fundadores sem federação", () => {
    const preparations = {
      ...PREPARATIONS,
      players: [...PREPARATIONS.players, founder("Bia", false), founder("Zé", true)],
    };
    expect(federationPartners(preparations, "Lilo").map((player) => player.nickname)).toEqual(["Bia"]);
  });
});

describe("federationCandidates", () => {
  it("põe os fundadores primeiro e os filiados dos dois partidos depois", () => {
    const preparations: Preparations = {
      ...PREPARATIONS,
      players: [
        ...PREPARATIONS.players,
        { ...PREPARATIONS.players[0]!, nickname: "Bia" },
        { ...PREPARATIONS.players[1]!, nickname: "Edu", founder: "Bia" },
      ],
    };
    expect(federationCandidates(preparations, "Lilo", "Bia").map((entry) => entry.nickname)).toEqual([
      "Lilo",
      "Bia",
      "Duda",
      "Edu",
    ]);
  });
});
