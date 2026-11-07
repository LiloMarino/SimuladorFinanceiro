import { describe, expect, it } from "vitest";
import type { CandleChallengeState, CandleChallengeView, ChallengePlayer } from "@/types";
import { isWatching, repliedCount, windowMode, withState } from "./view";

const player = (overrides: Partial<ChallengePlayer> = {}): ChallengePlayer => ({
  nickname: "Ana",
  color: "chart-1",
  position: 1,
  hits: 0,
  answered: 0,
  joined_at: 1,
  replied: false,
  last: null,
  marks: [],
  ...overrides,
});

const state = (overrides: Partial<CandleChallengeState> = {}): CandleChallengeState => ({
  status: "running",
  phase: "question",
  round_id: 1,
  starter: "Ana",
  solo: false,
  number: 1,
  total: 10,
  question: { id: 1 } as CandleChallengeState["question"],
  reveal: null,
  players: [player()],
  final: null,
  wins: [],
  rounds: 0,
  streak: 0,
  record: 0,
  ...overrides,
});

describe("resposta do jogador no cache", () => {
  const prev: CandleChallengeView = { state: state(), direction: "up" };

  it("mantém o lado enquanto é a mesma pergunta", () => {
    expect(withState(prev, state()).direction).toBe("up");
  });

  it("apaga o lado em outra pergunta, mesmo com o mesmo número (anulada)", () => {
    const next = state({ question: { id: 2 } as CandleChallengeState["question"] });
    expect(withState(prev, next).direction).toBeNull();
  });

  it("apaga o lado na revelação", () => {
    expect(withState(prev, state({ phase: "reveal", question: null })).direction).toBeNull();
  });

  it("começa sem lado quando não havia nada em cache", () => {
    expect(withState(undefined, state()).direction).toBeNull();
  });
});

describe("quem entrou no meio", () => {
  it("assiste enquanto a primeira pergunta dele é uma das próximas", () => {
    const late = player({ nickname: "Caio", joined_at: 2 });
    expect(isWatching(state({ number: 1 }), late)).toBe(true);
    expect(isWatching(state({ number: 1 }), player())).toBe(false);
    expect(isWatching(state({ number: 2 }), late)).toBe(false);
  });

  it("não entra na conta de quem respondeu", () => {
    const players = [
      player({ replied: true }),
      player({ nickname: "Bia" }),
      player({ nickname: "Caio", joined_at: 2 }),
    ];
    expect(repliedCount(state({ players }))).toEqual({ replied: 1, playing: 2 });
  });
});

describe("janela", () => {
  it("abre sozinha em rodada nova", () => {
    expect(windowMode(null, state())).toBe("open");
    expect(windowMode({ round: 1, mode: "minimized" }, state({ round_id: 2 }))).toBe("open");
  });

  it("lembra a escolha da rodada", () => {
    expect(windowMode({ round: 1, mode: "minimized" }, state())).toBe("minimized");
  });
});
