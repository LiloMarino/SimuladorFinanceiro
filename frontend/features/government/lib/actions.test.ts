import { describe, expect, it } from "vitest";
import type { ElectionPanel, GovernmentPanel } from "@/types";
import { electionPending, electionPendingCount, governmentPending, governmentPendingCount } from "./actions";

type Promise = NonNullable<GovernmentPanel["promises"]>["items"][number];

const promiseItem = (title: string, state: Promise["state"]) =>
  ({ state, promise: { title, kind: "WELFARE_SPENDING" } }) as Promise;

const governmentPanel = (overrides: Partial<GovernmentPanel>): GovernmentPanel =>
  ({
    today: "2016-09-01",
    is_president: true,
    congress: { impeachment_request: null },
    queue: [],
    promises: { last_vote: "2016-09-30", items: [promiseItem("Auxílio maior", "UNTOUCHED")] },
    ...overrides,
  }) as GovernmentPanel;

describe("governmentPending", () => {
  it("lista as promessas da chapa que ainda não andaram, com o dia da última votação que conta", () => {
    const pending = governmentPending(governmentPanel({}));

    expect(pending.idlePromises).toEqual({
      titles: ["Auxílio maior"],
      kind: "WELFARE_SPENDING",
      lastVote: "2016-09-30",
    });
    expect(governmentPendingCount(pending)).toBe(1);
  });

  it("ignora a promessa que já andou", () => {
    const panel = governmentPanel({
      promises: {
        last_vote: "2016-09-30",
        items: [promiseItem("Auxílio maior", "FULFILLED")],
      } as GovernmentPanel["promises"],
    });

    expect(governmentPending(panel).idlePromises).toBeNull();
  });

  it("some depois da última votação que conta para as promessas", () => {
    expect(governmentPending(governmentPanel({ today: "2016-10-01" })).idlePromises).toBeNull();
  });

  it("deixa as promessas para o presidente", () => {
    expect(governmentPending(governmentPanel({ is_president: false })).idlePromises).toBeNull();
  });
});

const electionPanel = (founder: boolean, overrides: Partial<ElectionPanel["parties"][number]> = {}): ElectionPanel =>
  ({
    can_edit_ticket: true,
    my_party: { party_id: 1, is_founder: founder },
    parties: [{ id: 1, vice: null, vice_phase: "NONE", promises: [], ...overrides }],
  }) as unknown as ElectionPanel;

describe("electionPending", () => {
  it("o fundador com a chapa sem vice e sem promessa tem as duas pendências", () => {
    const pending = electionPending(electionPanel(true));

    expect(pending).toEqual({ vice: true, promises: true });
    expect(electionPendingCount(pending)).toBe(2);
  });

  it("o convite de vice já enviado deixa de ser pendência", () => {
    expect(electionPending(electionPanel(true, { vice_phase: "PENDING" })).vice).toBe(false);
  });

  it("só o fundador decide a chapa", () => {
    expect(electionPending(electionPanel(false))).toEqual({ vice: false, promises: false });
  });

  it("depois do prazo de inscrição da chapa não sobra pendência", () => {
    const panel = { ...electionPanel(true), can_edit_ticket: false } as ElectionPanel;

    expect(electionPendingCount(electionPending(panel))).toBe(0);
  });
});
