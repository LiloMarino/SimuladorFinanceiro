import { describe, expect, it } from "vitest";
import type { ElectorateRow, VoterGroupInfo, VoterValue } from "@/types";
import {
  distanceWord,
  foundingAffinity,
  inTechnicalTie,
  lockReason,
  marginRange,
  nextPollDate,
  pollPercent,
  signedPoints,
  sortElectorate,
  topWants,
} from "./voters";

const scores = (values: Partial<Record<VoterValue, number>>) =>
  Object.entries(values).map(([value, score]) => ({ value: value as VoterValue, score: String(score) }));

// Os investidores do modelo: querem muito Mercado livre e rejeitam Justiça social
const investors: VoterGroupInfo = {
  group: "INVESTORS",
  weight: "0.08",
  margin: 11,
  readings: ["SELIC", "STOCKS"],
  wants: scores({
    FREE_MARKET: 100,
    SOCIAL_JUSTICE: 0,
    STABILITY: 75,
    DEVELOPMENT: 65,
    SAVER_PROTECTION: 75,
    PUBLIC_SERVICE: 25,
  }),
  flag_affinity: scores({
    FREE_MARKET: 12,
    SOCIAL_JUSTICE: -12,
    STABILITY: 6,
    DEVELOPMENT: 3.6,
    SAVER_PROTECTION: 6,
    PUBLIC_SERVICE: -6,
  }),
};

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

describe("foundingAffinity", () => {
  it("soma à base o que cada bandeira vale para o grupo", () => {
    // 20 + 12 + 6 + 6 = 44
    expect(foundingAffinity(investors, ["FREE_MARKET", "STABILITY", "SAVER_PROTECTION"], 20)).toBe(44);
  });

  it("não fica abaixo de zero", () => {
    expect(foundingAffinity(investors, ["SOCIAL_JUSTICE", "PUBLIC_SERVICE"], 10)).toBe(0);
  });
});

describe("topWants", () => {
  it("traz até dois valores que o grupo quer 75 ou mais, do mais querido ao menos", () => {
    expect(topWants(investors)).toEqual(["FREE_MARKET", "STABILITY"]);
  });
});

describe("margem de erro", () => {
  it("a faixa é o número mais e menos a margem, presa entre 0 e 100", () => {
    expect(marginRange(30, 3)).toEqual([27, 33]);
    expect(marginRange(2, 5)).toEqual([0, 7]);
  });

  it("é empate técnico quando a diferença cabe em duas margens", () => {
    expect(inTechnicalTie(30, [32, 22], 3)).toBe(true);
    expect(inTechnicalTie(30, [37], 3)).toBe(false);
    expect(inTechnicalTie(30, [30], 0)).toBe(false);
  });

  it("mostra inteiro com margem e uma casa sem ela", () => {
    expect(pollPercent(30.4, 3)).toBe("30%");
    expect(pollPercent(30.4, 0)).toBe("30,4%");
  });
});

describe("distanceWord", () => {
  it("separa perto, meio e longe pela distância entre o que o grupo quer e o perfil", () => {
    expect(distanceWord(90, 84).word).toBe("perto");
    expect(distanceWord(85, 50).word).toBe("meio");
    expect(distanceWord(30, 80).word).toBe("longe");
  });
});

describe("sortElectorate", () => {
  const row = (group: ElectorateRow["group"], support: number, rejection: number): ElectorateRow => ({
    group,
    affinity: "20",
    support: String(support),
    rejection: String(rejection),
    support_change: null,
    rejection_change: null,
  });
  const workers: VoterGroupInfo = { ...investors, group: "FORMAL_WORKERS", weight: "0.35" };
  const rows = [row("INVESTORS", 70, 0), row("FORMAL_WORKERS", 30, 10)];

  it("ordena pelo peso do grupo ou pelo saldo", () => {
    expect(sortElectorate(rows, [investors, workers], "weight").map((r) => r.group)).toEqual([
      "FORMAL_WORKERS",
      "INVESTORS",
    ]);
    expect(sortElectorate(rows, [investors, workers], "balance").map((r) => r.group)).toEqual([
      "INVESTORS",
      "FORMAL_WORKERS",
    ]);
  });
});

describe("nextPollDate", () => {
  it("é o dia 1º do mês seguinte, virando o ano em dezembro", () => {
    expect(nextPollDate("2021-10-14")).toBe("2021-11-01");
    expect(nextPollDate("2021-12-01")).toBe("2022-01-01");
  });
});

describe("signedPoints", () => {
  it("usa o sinal de menos tipográfico e nenhum sinal no zero", () => {
    expect(signedPoints(24)).toBe("+24");
    expect(signedPoints(-7.2)).toBe("−7");
    expect(signedPoints(0.2)).toBe("0");
  });
});
