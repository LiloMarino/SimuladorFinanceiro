import { describe, expect, it } from "vitest";
import type { ElectionMap } from "@/types";
import {
  changeOf,
  classifyPlace,
  defaultPlace,
  extremes,
  fallbackLens,
  lensAvailability,
  lensSentence,
  mixColor,
  paintedParty,
  placesOf,
  resultSentence,
  scaleCenter,
  scalePosition,
  standings,
  statesWon,
  votesInMillions,
} from "./map-lenses";

const group = (score: string) =>
  (["INVESTORS", "ENTREPRENEURS", "FORMAL_WORKERS", "PUBLIC_SERVANTS", "RETIREES", "WELFARE"] as const).map((g) => ({
    group: g,
    score: g === "WELFARE" ? score : "0.1",
  }));

const place = (
  code: string,
  name: string,
  kind: "STATE" | "REGION",
  region: string | null,
  share: string,
  margin: number,
) =>
  ({
    code,
    name,
    kind,
    region,
    electorate: Math.round(Number(share) * 155_756_933),
    electorate_share: share,
    margin,
    groups: group(code === "BA" ? "0.33" : "0.10"),
  }) as ElectionMap["places"][number];

const entries = (rows: [number, string][]) => rows.map(([party_id, points]) => ({ party_id, points }));

// Dois estados (BA no Nordeste, SC no Sul) e as duas regiões deles; dois partidos, 1 e 2
const map = {
  places: [
    place("BA", "Bahia", "STATE", "NORTHEAST", "0.07", 5),
    place("SC", "Santa Catarina", "STATE", "SOUTH", "0.035", 7),
    place("NORTHEAST", "Nordeste", "REGION", null, "0.27", 3),
    place("SOUTH", "Sul", "REGION", null, "0.14", 4),
  ],
  national_groups: group("0.15"),
  parties: [
    { id: 1, abbr: "PTD", name: "Partido A", color: "#0A4F24" },
    { id: 2, abbr: "UNI", name: "Partido B", color: "#1F49C7" },
    { id: 3, abbr: "VRD", name: "Partido C", color: null },
  ],
  viewer_party_id: null,
  poll: {
    previous_date: "2027-07-26",
    next_date: "2027-09-26",
    date: "2027-08-26",
    runoff: false,
    places: [
      {
        code: "BA",
        entries: entries([
          [1, "45"],
          [2, "30"],
          [3, "10"],
        ]),
        undecided: "15",
        previous_entries: entries([
          [1, "41"],
          [2, "31"],
          [3, "11"],
        ]),
      },
      {
        code: "SC",
        entries: entries([
          [1, "20"],
          [2, "24"],
          [3, "22"],
        ]),
        undecided: "34",
        previous_entries: entries([
          [1, "23"],
          [2, "24"],
          [3, "20"],
        ]),
      },
      {
        code: "NORTHEAST",
        entries: entries([
          [1, "42"],
          [2, "30"],
          [3, "12"],
        ]),
        undecided: "16",
        previous_entries: [],
      },
      {
        code: "SOUTH",
        entries: entries([
          [1, "24"],
          [2, "26"],
          [3, "20"],
        ]),
        undecided: "30",
        previous_entries: [],
      },
    ],
  },
  result: null,
  rejection: [
    {
      party_id: 1,
      national: "30",
      places: [
        { code: "BA", value: "20" },
        { code: "SC", value: "48" },
      ],
    },
  ],
  approval: {
    national: "47",
    places: [
      { code: "BA", value: "55" },
      { code: "SC", value: "39" },
    ],
  },
  opens_on: "2027-03-01",
  first_round: "2027-10-03",
  phase: "CAMPAIGN",
} as unknown as ElectionMap;

const withoutPoll = { ...map, poll: null, approval: null } as ElectionMap;

describe("classifyPlace", () => {
  it("lidera quando a diferença passa da margem", () => {
    // 45 − 30 = 15 > margem 5
    expect(classifyPlace(standings(map, "BA", "poll"), 5)).toEqual({ kind: "leads", leader: 1, lead: 15 });
  });

  it("empata quando a diferença é igual à margem", () => {
    const ranked = [
      { partyId: 1, points: 30 },
      { partyId: 2, points: 25 },
    ];
    expect(classifyPlace(ranked, 5)).toEqual({ kind: "tie", leaders: [1, 2], lead: 5, of: 2 });
  });

  it("empata entre 3 quando o 3º também cabe na margem do 1º", () => {
    // SC: 24, 22, 20 com margem 7: 24 − 20 = 4 ≤ 7
    expect(classifyPlace(standings(map, "SC", "poll"), 7)).toEqual({
      kind: "tie",
      leaders: [2, 3],
      lead: 2,
      of: 3,
    });
  });

  it("sem margem só o empate exato é empate", () => {
    expect(
      classifyPlace(
        [
          { partyId: 1, points: 30 },
          { partyId: 2, points: 29.9 },
        ],
        0,
      ),
    ).toMatchObject({ kind: "leads" });
    expect(
      classifyPlace(
        [
          { partyId: 1, points: 30 },
          { partyId: 2, points: 30 },
        ],
        0,
      ),
    ).toMatchObject({ kind: "tie" });
  });

  it("sem partido nenhum não há classificação", () => {
    expect(classifyPlace([], 5)).toBeNull();
  });
});

describe("lensAvailability", () => {
  it("as lentes da eleição ficam apagadas sem pesquisa, com a data em que abrem", () => {
    expect(lensAvailability(withoutPoll, "leads")).toEqual({ available: false, reason: "abre em 1 mar" });
    expect(lensAvailability(withoutPoll, "result")).toEqual({ available: false, reason: "em 3 out" });
  });

  it("rejeição, aprovação e eleitorado ligam quando têm dado", () => {
    expect(lensAvailability(withoutPoll, "rejection")).toEqual({ available: true });
    expect(lensAvailability(withoutPoll, "approval")).toEqual({ available: false, reason: "sem dados por lugar" });
    expect(lensAvailability(withoutPoll, "group")).toEqual({ available: true });
  });

  it("a variação pede uma pesquisa anterior", () => {
    const first = { ...map, poll: { ...map.poll!, previous_date: null } } as ElectionMap;
    expect(lensAvailability(first, "change")).toEqual({ available: false, reason: "precisa de 2 pesquisas" });
  });

  it("a lente pedida sem dado cai na primeira que liga", () => {
    expect(fallbackLens(withoutPoll, "leads")).toBe("rejection");
    expect(fallbackLens(map, "leads")).toBe("leads");
  });
});

describe("dados por lugar", () => {
  it("a variação é o ponto de agora menos o da pesquisa anterior", () => {
    expect(changeOf(map, "BA", 1)).toBe(4);
    expect(changeOf(map, "SC", 1)).toBe(-3);
  });

  it("sem pesquisa anterior no lugar não há variação", () => {
    expect(changeOf(map, "SOUTH", 1)).toBeNull();
  });

  it("o lugar de abertura é o maior eleitorado da divisão", () => {
    expect(defaultPlace(map, "state").code).toBe("BA");
    expect(defaultPlace(map, "region").code).toBe("NORTHEAST");
    expect(placesOf(map, "region")).toHaveLength(2);
  });

  it("o partido pintado é o escolhido, depois o do jogador, depois o líder da pesquisa", () => {
    expect(paintedParty(map, 2)?.id).toBe(2);
    expect(paintedParty({ ...map, viewer_party_id: 3 }, null)?.id).toBe(3);
    // Líder nacional: o partido 1 soma 42×0,27 + 24×0,14 contra 30×0,27 + 26×0,14 do partido 2
    expect(paintedParty(map, null)?.id).toBe(1);
  });
});

describe("escala e cor", () => {
  it("o extremo ignora lugares sem dado", () => {
    expect(extremes({ BA: 45, SC: 20, SOUTH: null })).toEqual({
      min: { code: "SC", value: 20 },
      max: { code: "BA", value: 45 },
    });
    expect(extremes({ BA: null })).toBeNull();
  });

  it("sem centro a posição vai linear do mínimo ao máximo", () => {
    // (30 − 20) ÷ (52 − 20) = 0,3125
    expect(scalePosition(30, 20, 52, null)).toBeCloseTo(0.3125);
  });

  it("com centro, o centro é sempre 0,5 e cada metade se estica até o extremo", () => {
    expect(scalePosition(47, 39, 55, 47)).toBe(0.5);
    // Metade de cima: 0,5 + 0,5 × (51 − 47) ÷ (55 − 47) = 0,75
    expect(scalePosition(51, 39, 55, 47)).toBeCloseTo(0.75);
    // Metade de baixo: 0,5 − 0,5 × (47 − 43) ÷ (47 − 39) = 0,25
    expect(scalePosition(43, 39, 55, 47)).toBeCloseTo(0.25);
  });

  it("o centro da escala é a média do país na aprovação e zero na variação", () => {
    expect(scaleCenter(map, "approval")).toBe(47);
    expect(scaleCenter(map, "change")).toBe(0);
    expect(scaleCenter(map, "rejection")).toBeNull();
  });

  it("a cor sem miolo mistura do extremo baixo ao alto", () => {
    expect(mixColor(0.25, { from: "var(--a)", to: "var(--b)" })).toBe("color-mix(in oklab, var(--b) 25%, var(--a))");
  });

  it("a cor com miolo mistura do miolo para o extremo do lado", () => {
    const ends = { from: "var(--lo)", to: "var(--hi)", middle: "var(--mid)" };
    expect(mixColor(0.75, ends)).toBe("color-mix(in oklab, var(--hi) 50%, var(--mid))");
    expect(mixColor(0.25, ends)).toBe("color-mix(in oklab, var(--lo) 50%, var(--mid))");
    expect(mixColor(0.5, ends)).toBe("color-mix(in oklab, var(--hi) 0%, var(--mid))");
  });
});

describe("frases", () => {
  it("Desempenho diz o mais forte e o mais fraco", () => {
    const values = { BA: 45, SC: 20 };
    expect(lensSentence({ map, division: "state", lens: "performance", abbr: "PTD", values })).toBe(
      "Mais forte: Bahia, 45%. Mais fraco: Santa Catarina, 20%.",
    );
  });

  it("Quem lidera conta os listrados e a margem deles", () => {
    // Só SC (margem 7) fica listrado entre os 2 estados
    expect(lensSentence({ map, division: "state", lens: "leads", abbr: "PTD", values: {} })).toBe(
      "1 dos 2 estados listrados: a margem deles é de ±7.",
    );
  });

  it("Variação resume por região: subiu em todos ou caiu em todos", () => {
    const values = { BA: 4, SC: -3 };
    expect(lensSentence({ map, division: "state", lens: "change", abbr: "PTD", values })).toBe(
      "Cresceu em Nordeste (▲4) e caiu em Sul (▼3) desde 26 jul.",
    );
  });

  it("Aprovação explica o centro da escala", () => {
    expect(lensSentence({ map, division: "state", lens: "approval", abbr: "PTD", values: { BA: 55, SC: 39 } })).toBe(
      "O centro da escala é a média do país (47%): azul aprova mais que o país, vermelho menos.",
    );
  });
});

describe("resultado", () => {
  const result = {
    round: 1,
    date: "2027-10-03",
    national: [],
    places: [
      {
        code: "BA",
        entries: entries([
          [1, "60"],
          [2, "40"],
        ]),
      },
      {
        code: "SC",
        entries: entries([
          [1, "20"],
          [2, "80"],
        ]),
      },
      {
        code: "NORTHEAST",
        entries: entries([
          [1, "55"],
          [2, "45"],
        ]),
      },
      {
        code: "SOUTH",
        entries: entries([
          [1, "25"],
          [2, "75"],
        ]),
      },
    ],
  };
  const finished = { ...map, result } as unknown as ElectionMap;

  it("conta os estados que cada partido venceu", () => {
    expect([...statesWon(finished)]).toEqual([
      [1, 1],
      [2, 1],
    ]);
  });

  it("a frase do dialog junta o melhor e o pior estado e região", () => {
    expect(resultSentence(finished, 1)).toEqual({
      best: "Bahia (60%) e Nordeste (55%)",
      worst: "Santa Catarina (20%) e Sul (25%)",
    });
  });

  it("os votos saem dos pontos sobre o eleitorado do país", () => {
    // 34% de 155,76 mi = 52,96 mi
    expect(votesInMillions(34, 155_756_933)).toBeCloseTo(52.957, 2);
  });
});
