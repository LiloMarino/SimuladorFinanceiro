import { describe, expect, it } from "vitest";
import type { TimelineMilestone, TimelinePoint } from "@/types";
import { milestoneEffect, milestoneLines, milestoneTip, type MilestoneContext } from "./map-milestones";

type Item = TimelineMilestone["items"][number];

const parties = [
  { id: 1, abbr: "PTD" },
  { id: 2, abbr: "UPR" },
];

function item(patch: Partial<Item>): Item {
  return { day: "2030-03-10", action: null, group: null, rival_id: null, partner_id: null, title: null, ...patch };
}

function milestone(kind: TimelineMilestone["kind"], items: Item[], region: TimelineMilestone["region"] = null) {
  return { after: "2030-03-01", before: "2030-04-01", party_id: 1, kind, items, region } satisfies TimelineMilestone;
}

function pollPoint(date: string, rows: Record<string, number>): TimelinePoint {
  return {
    date,
    kind: "POLL",
    happened: true,
    leaders: [],
    result: null,
    poll: {
      date,
      previous_date: null,
      next_date: null,
      runoff: false,
      places: Object.entries(rows).map(([code, points]) => ({
        code,
        undecided: "0",
        previous_entries: [],
        entries: [{ party_id: 1, points: String(points) }],
      })),
    },
  };
}

describe("milestoneLines", () => {
  it("junta as ações iguais e conta cada uma", () => {
    const rally = item({ action: "RALLY", group: "WELFARE" });
    const attack = item({ action: "ATTACK", group: "RETIREES", rival_id: 2 });
    const lines = milestoneLines(milestone("CAMPAIGN", [rally, rally, attack]), parties);
    expect(lines).toEqual(["2 comícios para quem depende de auxílio", "1 ataque ao UPR com aposentados"]);
  });

  it("lista as promessas pelo nome", () => {
    const lines = milestoneLines(milestone("PROMISE", [item({ title: "Cortar a Selic" })]), parties);
    expect(lines).toEqual(["Cortar a Selic"]);
  });

  it("distingue federação de apoio", () => {
    const lines = milestoneLines(
      milestone("ALLIANCE", [item({ title: "Frente", partner_id: 2 }), item({ partner_id: 2 })]),
      parties,
    );
    expect(lines).toEqual(["Federação Frente com UPR", "apoiou o UPR"]);
  });
});

describe("milestoneEffect", () => {
  it("diz o que o partido andou no país e na região da ação", () => {
    const text = milestoneEffect("PTD", { national: 2, region: { code: "NE", delta: 5 } }, "CAMPAIGN", "Nordeste");
    expect(text).toBe("Na pesquisa seguinte o PTD subiu 2 no país e subiu 5 no Nordeste, onde esse grupo pesa mais.");
  });

  it("fica estável quando não mexeu e some sem pesquisa dos dois lados", () => {
    expect(milestoneEffect("PTD", { national: 0, region: null }, "PROMISE", null)).toBe(
      "Na pesquisa seguinte o PTD ficou estável no país.",
    );
    expect(milestoneEffect("PTD", null, "PROMISE", null)).toBeNull();
  });
});

describe("milestoneTip", () => {
  it("monta título, intervalo e efeito com as pesquisas que cercam o marco", () => {
    const context: MilestoneContext = {
      parties,
      points: [pollPoint("2030-03-01", { NORTHEAST: 30 }), pollPoint("2030-04-01", { NORTHEAST: 35 })],
      regions: [{ code: "NORTHEAST", name: "Nordeste", electorate_share: "1" }],
    };
    const rally = item({ action: "RALLY", group: "WELFARE" });
    const tip = milestoneTip(milestone("CAMPAIGN", [rally, rally, rally], "NORTHEAST"), context);
    expect(tip.title).toBe("PTD · 3 ações de campanha");
    expect(tip.span).toBe("entre 01 mar e 01 abr 2030");
    expect(tip.effect).toBe(
      "Na pesquisa seguinte o PTD subiu 5 no país e subiu 5 no Nordeste, onde esse grupo pesa mais.",
    );
  });
});
