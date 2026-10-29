import { describe, expect, it } from "vitest";
import type { GovernmentNotice } from "@/types";
import { monthClosedToast, warningToast } from "./measure-toast";

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
  chance: null,
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
};

const notice = (partial: Partial<GovernmentNotice>): GovernmentNotice => ({
  ...EMPTY_NOTICE,
  kind: "IMPEACHMENT_WARNING",
  ...partial,
});

describe("warningToast", () => {
  const rule = { floor: 25, impeachment_months: 6 };

  it("avisa quantos fechamentos o governo passou abaixo do piso e quantos faltam", () => {
    const toast = warningToast(notice({ months_below_floor: 3, approval: 22 }), rule);
    expect(toast.title).toBe("3 de 6 meses seguidos abaixo de 25%");
    expect(toast.description).toContain("Aprovação de 22%");
    expect(toast.description).toContain("Mais 3 fechamentos abaixo do piso");
  });

  it("no penúltimo mês diz que o próximo fechamento decide", () => {
    const toast = warningToast(notice({ months_below_floor: 5, approval: 22 }), rule);
    expect(toast.description).toContain("Se o próximo fechamento ficar abaixo do piso");
  });
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
