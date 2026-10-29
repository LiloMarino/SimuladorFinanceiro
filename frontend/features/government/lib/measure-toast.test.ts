import { describe, expect, it } from "vitest";
import type { GovernmentNotice } from "@/types";
import { monthClosedToast } from "./measure-toast";

const EMPTY_NOTICE: GovernmentNotice = {
  kind: "UPDATED",
  actor: null,
  target: null,
  party_abbr: null,
  amount: null,
  round: null,
  winner_abbr: null,
  winner_name: null,
  accepted: null,
  measure_title: null,
  yes: null,
  no: null,
  defected: null,
  effective: null,
  tickers: null,
  months_below_floor: null,
  approval: null,
  previous_approval: null,
  groups_approved: null,
  groups_reproved: null,
  ticket_deadline: null,
  first_round: null,
  campaign_action: null,
  group: null,
  rival_abbr: null,
  seats_before: null,
  seats_after: null,
  broken_by_ally: null,
};

const notice = (partial: Partial<GovernmentNotice>): GovernmentNotice => ({
  ...EMPTY_NOTICE,
  kind: "IMPEACHMENT_WARNING",
  ...partial,
});

describe("monthClosedToast", () => {
  it("conta a aprovação, a variação e o que os grupos fizeram com o apoio do partido", () => {
    const toast = monthClosedToast(
      notice({
        kind: "MONTH_CLOSED",
        party_abbr: "PRL",
        approval: 54,
        previous_approval: 57,
        groups_approved: ["FORMAL_WORKERS", "WELFARE"],
        groups_reproved: ["RETIREES"],
      }),
    );
    expect(toast.title).toBe("Mês fechado");
    expect(toast.description).toBe(
      "Aprovação 54% (▼ 3). Carteira e auxílio aprovaram: o apoio do PRL subiu neles. Aposentados reprovaram: a rejeição do PRL subiu.",
    );
  });
});
