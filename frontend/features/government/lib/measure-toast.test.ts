import { describe, expect, it } from "vitest";
import type { GovernmentNotice } from "@/types";
import { inForceToast, monthClosedToast, votedToast, warningToast } from "./measure-toast";

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
};

const notice = (partial: Partial<GovernmentNotice>): GovernmentNotice => ({
  ...EMPTY_NOTICE,
  kind: "MEASURE_VOTED",
  ...partial,
});

describe("votedToast", () => {
  it("conta a rejeição com a chance que a medida tinha", () => {
    const toast = votedToast(
      notice({ accepted: false, measure_title: "Renda fixa: tabela única de 15%", chance: 59 }),
      [],
    );
    expect(toast.title).toBe("Congresso rejeitou: Renda fixa: tabela única de 15%");
    expect(toast.description).toBe("Tinha 59% de chance. Nada muda.");
  });

  it("liga a aprovação à carteira de quem tem os ativos", () => {
    const toast = votedToast(
      notice({
        accepted: true,
        measure_title: "Bancos: +5 pontos",
        effective: "2020-05-29",
        tickers: ["ITUB4", "BBDC4", "SANB11"],
      }),
      ["ITUB4", "BBDC4", "VALE3"],
    );
    expect(toast.tone).toBe("success");
    expect(toast.description).toContain("Vale em 29 mai");
    expect(toast.description).toContain("Você tem ITUB4 e BBDC4");
  });

  it("não fala da carteira de quem não tem os ativos", () => {
    const toast = votedToast(notice({ accepted: true, effective: "2020-05-29", tickers: ["ITUB4"] }), ["VALE3"]);
    expect(toast.description).not.toContain("Você tem");
  });
});

describe("inForceToast", () => {
  it("resume os ativos da medida de setor", () => {
    const toast = inForceToast(
      notice({ measure_title: "IR de bancos", tickers: ["ITUB4", "BBDC4", "A", "B", "C", "D"] }),
    );
    expect(toast.description).toBe("Vale para todas as vendas com lucro de ITUB4, BBDC4 e mais 4 ativos.");
  });

  it("diz que a medida geral vale para todos", () => {
    expect(inForceToast(notice({ measure_title: "IR em 20%", tickers: [] })).description).toBe(
      "Vale para todos os jogadores.",
    );
  });
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
