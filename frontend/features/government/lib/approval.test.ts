import { describe, expect, it } from "vitest";
import type { GovernmentApproval } from "@/types";
import {
  closingSentence,
  closingsLeft,
  deltaLabel,
  groupsSentence,
  monthsSpan,
  projection,
  projectionSentence,
  remainingMonths,
  signedFactor,
  streakMonths,
  targetArrow,
  trendOf,
  verdictCounts,
  verdictCountsSentence,
  verdictOf,
} from "./approval";

const THRESHOLDS = { approves_above: 55, reproves_below: 45 };

describe("verdictOf", () => {
  it("aprova acima de 55, reprova abaixo de 45 e fica neutro nas bordas", () => {
    expect(verdictOf(56, THRESHOLDS)).toBe("APPROVES");
    expect(verdictOf(55, THRESHOLDS)).toBe("NEUTRAL");
    expect(verdictOf(45, THRESHOLDS)).toBe("NEUTRAL");
    expect(verdictOf(44, THRESHOLDS)).toBe("REPROVES");
  });
});

describe("signedFactor", () => {
  it("usa o menos tipográfico, a vírgula e só a casa que faz falta", () => {
    expect(signedFactor("4.0")).toBe("+4");
    expect(signedFactor("-6.5")).toBe("−6,5");
    expect(signedFactor("0.0")).toBe("0");
  });
});

describe("trendOf e targetArrow", () => {
  it("compara a satisfação com o alvo", () => {
    expect(trendOf(37, 33)).toBe("falling");
    expect(trendOf(37, 40)).toBe("rising");
    expect(trendOf(63, 63)).toBe("steady");
    expect(targetArrow(37, 33)).toBe("▼ 33");
    expect(targetArrow(0, 3)).toBe("▲ 3");
    expect(targetArrow(63, 63)).toBe("= 63");
  });
});

describe("deltaLabel", () => {
  it("mostra a variação desde o fechamento anterior", () => {
    expect(deltaLabel(54, 57)).toBe("▼ 3");
    expect(deltaLabel(57, 54)).toBe("▲ 3");
    expect(deltaLabel(54, 54)).toBe("");
    expect(deltaLabel(54, null)).toBe("");
  });
});

describe("projection", () => {
  it("anda um terço do caminho até o alvo a cada mês", () => {
    expect(projection(40, 70, 3).map(Math.round)).toEqual([50, 57, 61]);
  });

  it("conta a trajetória em frase", () => {
    expect(projectionSentence(37, 33)).toBe("hoje 37, depois 36, 35 e 34");
  });
});

const approval = (partial: Partial<GovernmentApproval>) =>
  ({
    ...THRESHOLDS,
    closes_on: "2021-09-30",
    low_streak: 3,
    impeachment_months: 6,
    history: [
      { date: "2021-05-31", value: 30 },
      { date: "2021-06-30", value: 24 },
      { date: "2021-07-30", value: 23 },
      { date: "2021-08-31", value: 22 },
    ],
    groups: [],
    ...partial,
  }) as GovernmentApproval;

describe("contagem do impeachment", () => {
  it("lista os meses que já fecharam abaixo do piso", () => {
    expect(streakMonths(approval({}))).toEqual(["jun", "jul", "ago"]);
    expect(streakMonths(approval({ low_streak: 0 }))).toEqual([]);
  });

  it("diz quantos fechamentos faltam e em quais meses", () => {
    expect(closingsLeft(approval({}))).toBe(3);
    expect(remainingMonths(approval({}))).toBe("set, out e nov");
  });
});

describe("verdictCounts", () => {
  it("conta os grupos de cada veredito num fechamento", () => {
    const point = (value: number) => [{ date: "2021-08-31", value }];
    const groups = [60, 60, 50, 40, 60, 60].map((value) => ({ history: point(value) }));
    const counts = verdictCounts(approval({ groups: groups as GovernmentApproval["groups"] }), "2021-08-31");
    expect(counts).toEqual({ APPROVES: 4, NEUTRAL: 1, REPROVES: 1 });
    expect(verdictCountsSentence(counts)).toBe("4 grupos aprovaram, 1 neutro, 1 reprovou");
  });
});

describe("frases dos grupos", () => {
  it("escreve os grupos em texto corrido", () => {
    expect(groupsSentence(["FORMAL_WORKERS", "WELFARE", "ENTREPRENEURS"])).toBe("Carteira, auxílio e empreendedores");
  });

  it("conta o que o fechamento fez com o apoio do partido", () => {
    expect(
      closingSentence("PRL", {
        approved: ["WELFARE"],
        reproved: ["RETIREES"],
        neutral: ["PUBLIC_SERVANTS", "INVESTORS"],
      }),
    ).toBe(
      "Auxílio aprovaram: o apoio do PRL subiu neles. Aposentados reprovaram: a rejeição do PRL subiu. Servidores e investidores ficaram neutros.",
    );
  });
});

describe("monthsSpan", () => {
  it("mostra o ano uma vez quando os meses são do mesmo ano", () => {
    expect(monthsSpan("2021-11-30", 6)).toBe("jun a nov 2021");
  });

  it("mostra os dois anos quando a contagem atravessa a virada", () => {
    expect(monthsSpan("2021-02-26", 6)).toBe("set 2020 a fev 2021");
  });
});
