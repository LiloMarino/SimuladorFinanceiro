import { describe, expect, it } from "vitest";
import type { GovernmentNotice } from "@/types";
import { dealAnsweredToast, dealBrokenToast, dealEndedToast } from "./deal-toast";

const NOTICE: GovernmentNotice = {
  kind: "DEAL_ANSWERED",
  actor: null,
  target: null,
  party_abbr: "PRL",
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
  seats_before: 46,
  seats_after: 74,
  broken_by_ally: null,
};

describe("dealAnsweredToast", () => {
  it("conta a base que cresce quando o líder aceita", () => {
    const toast = dealAnsweredToast({ ...NOTICE, actor: "Lilo", accepted: true, effective: "2023-09-14" });
    expect(toast.tone).toBe("success");
    expect(toast.title).toBe("Lilo aceitou: o PRL entra na base");
    expect(toast.description).toContain("Base de 46 para 74 cadeiras, até 14");
  });

  it("conta a recusa com a data da nova proposta", () => {
    const toast = dealAnsweredToast({ ...NOTICE, actor: "Lilo", accepted: false, effective: "2023-04-28" });
    expect(toast.tone).toBe("warning");
    expect(toast.title).toBe("Lilo recusou a proposta");
    expect(toast.description).toContain("Nova proposta a partir de 28");
  });

  it("nomeia o partido quando quem responde é o computador", () => {
    expect(dealAnsweredToast({ ...NOTICE, accepted: true }).title).toBe("PRL aceitou entrar na base");
  });
});

describe("dealBrokenToast", () => {
  it("culpa o governo quando ele corta a emenda", () => {
    const toast = dealBrokenToast({
      ...NOTICE,
      rival_abbr: "FDS",
      groups_reproved: ["INVESTORS"],
      broken_by_ally: false,
    });
    expect(toast.title).toBe("O governo FDS rompeu o acordo com o PRL");
    expect(toast.description).toContain("culpam o FDS");
  });

  it("conta a base que cai quando o aliado sai", () => {
    const toast = dealBrokenToast({
      ...NOTICE,
      rival_abbr: "FDS",
      groups_reproved: ["INVESTORS"],
      broken_by_ally: true,
      seats_before: 74,
      seats_after: 46,
    });
    expect(toast.title).toBe("O PRL saiu da base");
    expect(toast.description).toContain("de 74 para 46");
  });
});

describe("dealEndedToast", () => {
  it("separa o fim na posse do fim de prazo", () => {
    expect(dealEndedToast({ ...NOTICE, party_abbr: "UPR, ACI", accepted: true }).title).toContain("posse");
    expect(dealEndedToast({ ...NOTICE, party_abbr: "UPR", accepted: false }).title).toBe(
      "Acordo com o UPR chegou ao fim",
    );
  });
});
