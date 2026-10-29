import { describe, expect, it } from "vitest";
import type { RunoffRace, RunoffTransfer } from "@/types";
import { dayAfter, followTotal, runoffLeaderId, sentTo } from "./runoff";

describe("dayAfter", () => {
  it("passa para o dia seguinte, virando o mês", () => {
    expect(dayAfter("2022-10-02")).toBe("2022-10-03");
    expect(dayAfter("2022-10-31")).toBe("2022-11-01");
  });
});

describe("runoffLeaderId", () => {
  const race = (points: [number, string][]) =>
    ({
      finalists: [1, 2],
      polls: [{ entries: points.map(([party_id, value]) => ({ party_id, points: value })) }],
    }) as unknown as RunoffRace;

  it("devolve o finalista com mais pontos na última pesquisa", () => {
    expect(
      runoffLeaderId(
        race([
          [1, "44"],
          [2, "47"],
          [3, "9"],
        ]),
      ),
    ).toBe(2);
  });

  it("não escolhe líder sem pesquisa", () => {
    expect(runoffLeaderId({ finalists: [1, 2], polls: [] } as unknown as RunoffRace)).toBeNull();
    expect(runoffLeaderId(null)).toBeNull();
  });
});

describe("transferência", () => {
  const transfer = {
    groups: [
      { group: "RETIREES", sent: [{ party_id: 1, points: "12" }], would_follow: "2" },
      { group: "WELFARE", sent: [], would_follow: "4" },
    ],
  } as unknown as RunoffTransfer;

  it("lê o que o grupo mandou a cada finalista", () => {
    expect(sentTo(transfer.groups[0]!, 1)).toBe(12);
    expect(sentTo(transfer.groups[1]!, 1)).toBe(0);
  });

  it("soma o que a declaração leva pelo peso dos grupos", () => {
    const weights = new Map([
      ["RETIREES", "0.2"],
      ["WELFARE", "0.15"],
    ]);
    expect(followTotal(transfer, weights)).toBeCloseTo(1);
  });
});
