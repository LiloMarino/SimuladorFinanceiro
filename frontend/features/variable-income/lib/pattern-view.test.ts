import { describe, expect, it } from "vitest";
import type { CandlePattern, ChallengeAnswer } from "@/types";
import {
  displayPatternDays,
  hitRate,
  isAnswerFresh,
  nextScaleWithPatterns,
  patternOn,
  patternsSince,
  periodScore,
} from "./pattern-view";

const pattern = (end: string, hit: boolean | null, start = end): CandlePattern => ({
  code: "hammer",
  start,
  end,
  direction: "up",
  change_5d: hit === null ? null : 0.02,
  hit,
});

describe("pattern view", () => {
  it("recorta os padrões do período pelo dia em que terminam", () => {
    const all = [pattern("2024-01-02", true), pattern("2024-02-10", false), pattern("2024-03-01", null)];
    expect(patternsSince(all, "2024-02-01").map((p) => p.end)).toEqual(["2024-02-10", "2024-03-01"]);
    expect(patternsSince(all, null)).toHaveLength(3);
  });

  it("conta só os padrões com desfecho no placar do período", () => {
    const score = periodScore([pattern("2024-01-02", true), pattern("2024-01-05", false), pattern("2024-01-09", null)]);
    expect(score).toEqual({ hits: 1, checked: 2 });
  });

  it("só dá a taxa de acerto a partir de 10 ocorrências", () => {
    expect(hitRate({ code: "hammer", checked: 9, hits: 9 })).toBeNull();
    expect(hitRate({ code: "hammer", checked: 10, hits: 6 })).toBe(0.6);
  });

  it("acha o padrão de várias velas por qualquer dia dele", () => {
    const engulfing = pattern("2023-12-27", true, "2023-12-26");
    expect(patternOn([engulfing], "2023-12-26")).toBe(engulfing);
    expect(patternOn([engulfing], "2023-12-28")).toBeUndefined();
  });

  it("sugere o primeiro período maior que tem padrões", () => {
    const counts: Record<string, number> = { "1m": 0, "3m": 0, "1a": 14 };
    expect(nextScaleWithPatterns(["1m", "3m", "1a"], "1m", (scale) => counts[scale])).toEqual({
      scale: "1a",
      count: 14,
    });
    expect(nextScaleWithPatterns(["1m", "3m", "1a"], "1a", (scale) => counts[scale])).toBeNull();
  });

  it("escreve os dias do padrão", () => {
    expect(displayPatternDays({ start: "2024-01-14", end: "2024-01-14" })).toBe("14 jan");
    expect(displayPatternDays({ start: "2023-12-26", end: "2023-12-27" })).toBe("26–27 dez");
    expect(displayPatternDays({ start: "2023-12-29", end: "2024-01-02" })).toBe("29 dez – 02 jan");
  });

  it("mantém na faixa a resposta que espera e a conferida há pouco", () => {
    const answer = (status: ChallengeAnswer["status"], settles_on: string) =>
      ({ status, settles_on }) as ChallengeAnswer;
    expect(isAnswerFresh(answer("waiting", "2024-03-21"), "2024-03-14")).toBe(true);
    expect(isAnswerFresh(answer("hit", "2024-03-21"), "2024-03-25")).toBe(true);
    expect(isAnswerFresh(answer("hit", "2024-03-21"), "2024-04-30")).toBe(false);
  });
});
