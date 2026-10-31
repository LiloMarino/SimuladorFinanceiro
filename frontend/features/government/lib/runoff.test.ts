import { describe, expect, it } from "vitest";
import type { ElectionRound, RunoffRace, RunoffTransfer } from "@/types";
import {
  dayAfter,
  firstRoundBefore,
  followTotal,
  runoffLeaderId,
  sentTo,
  turnaroundGap,
  undecidedNow,
  undecidedPointsText,
} from "./runoff";

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

describe("undecidedNow", () => {
  it("soma os indecisos de cada grupo pelo peso dele", () => {
    const transfer = {
      groups: [
        { group: "RETIREES", undecided_now: "10" },
        { group: "INVESTORS", undecided_now: "5" },
      ],
    } as unknown as RunoffTransfer;
    const weights = new Map([
      ["RETIREES", "0.2"],
      ["INVESTORS", "0.1"],
    ]);
    expect(undecidedNow(transfer, weights)).toBeCloseTo(2.5);
  });
});

describe("undecidedPointsText", () => {
  it("usa o singular só para 1 ponto", () => {
    expect(undecidedPointsText(1)).toBe("1 ponto segue indeciso");
    expect(undecidedPointsText(0.6)).toBe("1 ponto segue indeciso");
  });

  it("usa o plural para zero e para mais de um", () => {
    expect(undecidedPointsText(0)).toBe("0 pontos seguem indecisos");
    expect(undecidedPointsText(7.4)).toBe("7 pontos seguem indecisos");
  });
});

describe("turnaroundGap", () => {
  const round = (number: number, date: string, shares: [number, string][], winner: number | null) =>
    ({
      round: number,
      date,
      winner,
      finalists: [1, 2],
      parties: shares.map(([party_id, share]) => ({ party_id, share })),
    }) as unknown as ElectionRound;
  const first = round(
    1,
    "2022-10-02",
    [
      [1, "0.387"],
      [2, "0.347"],
      [3, "0.266"],
    ],
    null,
  );

  it("mede a distância quando o vencedor terminou o 1º turno atrás", () => {
    expect(
      turnaroundGap(
        first,
        round(
          2,
          "2022-10-23",
          [
            [2, "0.507"],
            [1, "0.493"],
          ],
          2,
        ),
      ),
    ).toBeCloseTo(4);
  });

  it("não há virada quando o líder do 1º turno vence", () => {
    expect(
      turnaroundGap(
        first,
        round(
          2,
          "2022-10-23",
          [
            [1, "0.52"],
            [2, "0.48"],
          ],
          1,
        ),
      ),
    ).toBeNull();
  });

  it("acha o 1º turno anterior ao 2º", () => {
    const runoff = round(2, "2022-10-23", [], 2);
    const older = round(1, "2018-10-07", [], null);
    expect(firstRoundBefore([older, first, runoff], runoff)).toBe(first);
  });
});
