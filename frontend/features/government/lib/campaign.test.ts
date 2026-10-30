import { describe, expect, it } from "vitest";
import type { CampaignBand, CampaignEntry, CampaignRoll, CampaignTarget, GovernmentNotice } from "@/types";
import {
  bandEffect,
  bandOf,
  bandRange,
  campaignToast,
  chancePercent,
  effectText,
  entryTitle,
  freshGroup,
  headline,
  nthOf,
  rallyExtremes,
  ratePercent,
  resultTitle,
  signed,
  toastEffect,
} from "./campaign";

const band = (partial: Partial<CampaignBand>): CampaignBand => ({
  band: "NORMAL",
  first_roll: 7,
  last_roll: 14,
  chance: "0.4",
  support: "3",
  rejection: "0",
  ...partial,
});

const entry = (partial: Partial<CampaignEntry>): CampaignEntry => ({
  id: 1,
  date: "2022-08-14",
  kind: "EVENT",
  nickname: "Lilo",
  party_abbr: "PRL",
  party_color: "#15803D",
  group: "RETIREES",
  rival_abbr: null,
  rolls: [11],
  roll: 11,
  band: "NORMAL",
  support: "3",
  rejection: "-1",
  worth_now: "3",
  worth_share: "1",
  price: "10800",
  newsworthy: false,
  ...partial,
});

const notice = (partial: Partial<GovernmentNotice>): GovernmentNotice => ({
  kind: "CAMPAIGN_ACTION",
  actor: "Duda",
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
  campaign_action: "EVENT",
  group: "RETIREES",
  rival_abbr: null,
  seats_before: null,
  seats_after: null,
  broken_by_ally: null,
  ...partial,
});

describe("signed", () => {
  it("põe o sinal na frente, com vírgula decimal e o menos tipográfico", () => {
    expect(signed("3")).toBe("+3");
    expect(signed(-6.5)).toBe("−6,5");
    expect(signed("0")).toBe("0");
  });

  it("corta em duas casas", () => {
    // 0,75 × 0,5 = 0,375 → 0,38
    expect(signed("0.375")).toBe("+0,38");
  });
});

describe("ratePercent", () => {
  it("segue 100%, 50%, 25% e arredonda para baixo", () => {
    expect(ratePercent("1")).toBe("100%");
    expect(ratePercent("0.5")).toBe("50%");
    expect(ratePercent("0.125")).toBe("12%");
  });

  it("nunca mostra zero enquanto ainda rende", () => {
    // 0,5^5 = 3,125% → 3%; 0,5^10 ≈ 0,1% → 1%
    expect(ratePercent("0.03125")).toBe("3%");
    expect(ratePercent("0.0009765625")).toBe("1%");
  });
});

describe("faixas do dado", () => {
  it("escreve a faixa e a chance", () => {
    expect(bandRange(band({ first_roll: 1, last_roll: 1 }))).toBe("1");
    expect(bandRange(band({ first_roll: 2, last_roll: 6 }))).toBe("2–6");
    // Dois dados: 1 chance em 400
    expect(chancePercent("0.0025")).toBe("0,25%");
    expect(chancePercent("0.4")).toBe("40%");
  });

  it("mostra a rejeição quando o apoio não muda (a culatra do ataque)", () => {
    expect(bandEffect(band({ support: "-5" }))).toBe("−5");
    expect(bandEffect(band({ support: "0", rejection: "3" }))).toBe("+3 rej.");
  });

  it("acha a faixa do número rolado", () => {
    const bands = [
      band({ band: "DISASTER", first_roll: 1, last_roll: 1 }),
      band({ band: "NORMAL", first_roll: 7, last_roll: 14 }),
    ];
    expect(bandOf(bands, 14)?.band).toBe("NORMAL");
    expect(bandOf(bands, 3)).toBeUndefined();
  });
});

describe("linhas do histórico", () => {
  it("intitula a ação com o grupo e o rival", () => {
    expect(entryTitle(entry({}))).toBe("Evento com aposentados");
    expect(entryTitle(entry({ kind: "ATTACK", rival_abbr: "FDS", group: "PUBLIC_SERVANTS" }))).toBe(
      "Ataque ao FDS entre servidores",
    );
    expect(entryTitle(entry({ kind: "ATTACK_RECEIVED", party_abbr: "FDS", group: "PUBLIC_SERVANTS" }))).toBe(
      "FDS atacou entre servidores",
    );
    expect(entryTitle(entry({ kind: "BASE_BUDGET", group: null }))).toBe("Verba de base");
  });

  it("resume o efeito do dia", () => {
    expect(effectText(entry({}))).toBe("+3 · −1 rej.");
    expect(effectText(entry({ kind: "TV", group: null, rejection: "0" }))).toBe("+3 em cada");
    expect(effectText(entry({ kind: "ATTACK", rival_abbr: "FDS", support: "-5", rejection: "0" }))).toBe("FDS −5");
    expect(effectText(entry({ kind: "ATTACK_RECEIVED", support: "-5", rejection: "0" }))).toBe("−5");
  });
});

describe("resultado do dado", () => {
  const roll = (partial: Partial<CampaignEntry>): CampaignRoll => ({
    entry: entry(partial),
    target_abbr: "PRL",
    support_before: "62",
    support_after: "65",
    rejection_before: "11",
    rejection_after: "10",
  });

  it("conta o efeito de cada faixa", () => {
    expect(resultTitle(roll({ rejection: "0" }))).toBe("Evento com aposentados: +3 de apoio");
    expect(resultTitle(roll({ band: "VIRAL", support: "9" }))).toBe("Viralizou: +9 de apoio entre aposentados");
    // O comício dobra o desastre: 4 × 4 = −16
    expect(resultTitle(roll({ kind: "RALLY", band: "DISASTER", support: "-16", group: "PUBLIC_SERVANTS" }))).toBe(
      "Desastre no comício: −16 de apoio entre servidores",
    );
    expect(resultTitle(roll({ kind: "TV", group: null, support: "3" }))).toBe("TV: +3 de apoio em cada grupo");
  });

  it("o tiro que sai pela culatra soma rejeição a quem atacou", () => {
    const backfired = roll({
      kind: "ATTACK",
      rival_abbr: "FDS",
      band: "DISASTER",
      support: "0",
      rejection: "3",
    });
    expect(resultTitle(backfired)).toBe("O tiro saiu pela culatra: +3 de rejeição entre aposentados");
  });

  it("dá manchete ao desastre, ao viral e a todo ataque", () => {
    expect(headline(entry({ kind: "RALLY", band: "DISASTER", group: "PUBLIC_SERVANTS" }))).toBe(
      "Candidato do PRL se envolve em polêmica no comício com servidores",
    );
    expect(headline(entry({ band: "VIRAL" }))).toBe("Evento do PRL com aposentados viraliza");
    expect(headline(entry({ kind: "ATTACK", rival_abbr: "FDS" }))).toBe(
      "PRL parte para o ataque contra o FDS entre aposentados",
    );
  });
});

describe("campaignToast", () => {
  const mine = { abbr: "PRL", nickname: "Lilo" };

  it("avisa o partido atacado", () => {
    const toast = campaignToast(notice({ campaign_action: "ATTACK", party_abbr: "FDS", rival_abbr: "PRL" }), mine);
    expect(toast?.tone).toBe("warning");
    expect(toast?.title).toBe("O FDS atacou o PRL entre aposentados");
  });

  it("o ataque entre outros partidos é só do jornal", () => {
    expect(campaignToast(notice({ campaign_action: "ATTACK", party_abbr: "FDS", rival_abbr: "UPR" }), mine)).toBeNull();
  });

  it("conta ao partido a ação de outro filiado, e só a ela", () => {
    expect(campaignToast(notice({}), mine)?.title).toBe("Duda fez um evento com aposentados");
    expect(campaignToast(notice({ campaign_action: "TV", group: null }), mine)?.title).toBe(
      "Duda fez TV para todos os grupos",
    );
    expect(campaignToast(notice({ campaign_action: "ATTACK", rival_abbr: "FDS" }), mine)?.title).toBe(
      "Duda atacou o FDS entre aposentados",
    );
    expect(campaignToast(notice({ actor: "Lilo" }), mine)).toBeNull();
    expect(campaignToast(notice({ party_abbr: "FDS" }), mine)).toBeNull();
    expect(campaignToast(notice({}), undefined)).toBeNull();
  });
});

describe("toastEffect", () => {
  it("conta ao filiado a faixa e o efeito no partido dele", () => {
    expect(toastEffect(entry({ band: "VIRAL", roll: 20, support: "18", rejection: "0" }), "PRL")).toBe(
      "Viralizou (20): +18 de apoio ao PRL",
    );
    expect(toastEffect(entry({ kind: "TV", group: null, support: "3", rejection: "0" }), "PRL")).toBe(
      "Normal (11): +3 de apoio ao PRL em cada grupo",
    );
  });

  it("conta ao atacado o efeito, sem o dado", () => {
    const received = entry({
      kind: "ATTACK_RECEIVED",
      party_abbr: "FDS",
      band: null,
      roll: null,
      rolls: [],
      support: "-5",
      rejection: "0",
    });
    expect(toastEffect(received, "PRL")).toBe("−5 de apoio ao PRL no grupo");
  });
});

describe("rallyExtremes", () => {
  it("explica os extremos dobrados do comício", () => {
    expect(rallyExtremes("DISASTER", "-16", "4")).toEqual({
      label: "Comício dobra os extremos: perde 4× o normal",
      value: "4 × 4 = −16",
    });
    expect(rallyExtremes("VIRAL", "24", "4")?.value).toBe("6 × 4 = +24");
    expect(rallyExtremes("NORMAL", "4", "4")).toBeNull();
  });
});

describe("nthOf", () => {
  it("concorda com o nome da ação", () => {
    expect(nthOf("EVENT", 2)).toBe("o 2º");
    expect(nthOf("TV", 3)).toBe("a 3ª");
  });
});

describe("freshGroup", () => {
  const target = (group: CampaignTarget["group"], uses: number, support: string): CampaignTarget => ({
    group,
    uses_this_month: uses,
    rate: "1",
    first_by: null,
    first_day: null,
    repair_left: "0",
    repair_limit: "0",
    support: "10",
    rejection: "10",
    bands: [band({ support })],
    average: "0",
  });

  it("escolhe o grupo ainda sem uso onde o ganho normal é maior", () => {
    const targets = [target("RETIREES", 1, "9"), target("PUBLIC_SERVANTS", 0, "6"), target("FORMAL_WORKERS", 0, "3")];
    expect(freshGroup(targets)).toEqual({ group: "PUBLIC_SERVANTS", effect: "+6" });
    expect(freshGroup([target("RETIREES", 2, "9")])).toBeNull();
  });
});
