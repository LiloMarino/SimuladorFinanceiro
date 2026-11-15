import { describe, expect, it } from "vitest";
import type {
  GovernmentMeasure,
  StateCompany,
  StateMovement,
  StateOffer,
  StateOrderPreview,
  StateRules,
} from "@/types";
import {
  capBreakdown,
  capLabel,
  capUsage,
  commandChip,
  companyValue,
  controlLabel,
  heldCompanies,
  leverEffect,
  leverOwnedNote,
  movementText,
  offerDaysLabel,
  offerPremium,
  premiumLabel,
  privatizeChip,
  reservationCost,
  reservedShare,
  rowControlEffect,
  signedSince,
  sinceFounding,
  stakeNote,
  stepEffect,
  stepLabel,
  votesOnLabel,
} from "./state-companies";

const company = (partial: Partial<StateCompany>): StateCompany => ({
  ticker: "LUZN3",
  name: "Luz Nacional",
  origin: "FOUNDED",
  status: "ACTIVE",
  lever: "ENERGY",
  size: "SMALL",
  government_share: "0.51",
  shares: 1_000_000_000,
  price: "30",
  government_value: "15300000000",
  invested: "15300000000",
  fair_price: "30",
  order: { control: "NONE", dividend_policy: "NORMAL" },
  in_force: { control: "NONE", dividend_policy: "NORMAL" },
  held_points: "0",
  treasury_dividend_12m: "0",
  can_command: true,
  privatization_measure_id: null,
  founded_on: "2016-05-02",
  privatized_on: null,
  proceeds: null,
  ...partial,
});

const queued = (id: number, voteDate: string) =>
  ({ id, status: "QUEUED", vote_date: voteDate, effective: null, chance: null }) as unknown as GovernmentMeasure;

const offer = (partial: Partial<StateOffer>): StateOffer => ({
  ticker: "CRDP3",
  name: "Crédito Público",
  opened_on: "2016-10-17",
  ends_on: "2016-10-21",
  shares: 1000,
  price: "10",
  market_price: "9.35",
  reserved: "500",
  your_reservation: null,
  your_cash: "50000",
  ...partial,
});

describe("rótulos do controle", () => {
  it("o degrau sem controle e com controle", () => {
    expect(stepLabel("NONE")).toBe("Sem controle");
    expect(stepLabel("P10")).toBe("10%");
    expect(controlLabel("NONE")).toBe("Sem controle");
    expect(controlLabel("P20")).toBe("Segurando 20%");
  });
});

describe("stepEffect", () => {
  const step = (partial: Partial<StateOrderPreview["steps"][number]>): StateOrderPreview["steps"][number] => ({
    control: "P10",
    percent: 10,
    held_points: "0.5",
    credit_points: "0.25",
    profit_cut: "0.1",
    price_factor: "0.9",
    dividend_factor: "0.8",
    monthly_treasury_dividend: null,
    blocked_reason: null,
    ...partial,
  });

  it("combustível e energia mostram o IPCA e o corte no dividendo", () => {
    expect(stepEffect(step({}), "FUEL")).toEqual({ main: "IPCA −0,5", dividend: "div. −20%" });
  });

  it("o banco mostra o juro do crédito, em duas casas quando precisa", () => {
    expect(stepEffect(step({}), "BANK")).toEqual({ main: "juro −0,25", dividend: "div. −20%" });
  });

  it("sem controle não há efeito", () => {
    expect(stepEffect(step({ control: "NONE" }), "FUEL")).toBeNull();
  });
});

describe("rowControlEffect", () => {
  it("diz o ponto de IPCA segurado, ou o juro no banco", () => {
    expect(
      rowControlEffect(company({ in_force: { control: "P10", dividend_policy: "NORMAL" }, held_points: "0.5" })),
    ).toBe("IPCA −0,5 ponto");
    expect(rowControlEffect(company({ lever: "BANK", in_force: { control: "P10", dividend_policy: "NORMAL" } }))).toBe(
      "Juro do crédito menor",
    );
    expect(rowControlEffect(company({}))).toBeNull();
  });
});

describe("teto do controle", () => {
  const summary = {
    government_value: "0",
    treasury_dividends_12m: "0",
    backlog_points: "0",
    held_points: "0.75",
    cap_points: "1.5",
  };

  it("a barra é a razão entre o em uso e o teto", () => {
    expect(capUsage(summary)).toBeCloseTo(0.5);
    expect(capUsage({ ...summary, held_points: "3" })).toBe(1);
  });

  it("o rótulo traz o em uso e o teto", () => {
    expect(capLabel("0.7", "1.5")).toBe("0,7 de 1,5 ponto");
    expect(capLabel("1.5", "1.5")).toBe("1,5 de 1,5 ponto");
  });

  it("a divisão lista só quem segura, pelo primeiro nome", () => {
    const rows = [
      company({ name: "Petrobras Nacional", held_points: "0.5" }),
      company({ name: "Luz Nacional", held_points: "0.2" }),
      company({ name: "Banco Público", held_points: "0" }),
    ];
    expect(capBreakdown(rows)).toBe("Petrobras 0,5 · Luz 0,2");
  });
});

describe("valor da empresa e ganho desde a fundação", () => {
  it("o valor da empresa inteira sai da fatia do governo", () => {
    expect(companyValue(company({ government_value: "51000000000" }))).toBeCloseTo(100e9);
    expect(companyValue(company({ government_share: "0", government_value: "0" }))).toBe(0);
  });

  it("a fundada compara a fatia com o que o governo pagou por ela", () => {
    // 17,136 bi sobre os 15,3 bi pagos: +12%
    expect(sinceFounding(company({ government_value: "17136000000" }))).toBeCloseTo(0.12);
    // 12,24 bi sobre os 15,3 bi pagos: −20%
    expect(sinceFounding(company({ government_value: "12240000000" }))).toBeCloseTo(-0.2);
  });

  it("a importada não tem fundação para comparar", () => {
    expect(sinceFounding(company({ origin: "IMPORTED", size: null, invested: null }))).toBeNull();
  });

  it("o sinal usa o menos tipográfico", () => {
    expect(signedSince(0.12)).toBe("+12,0%");
    expect(signedSince(-0.2)).toBe("−20,0%");
  });
});

describe("heldCompanies", () => {
  it("tira a vendida", () => {
    const rows = [company({ ticker: "AAAA3" }), company({ ticker: "BBBB3", status: "PRIVATIZED" })];
    expect(heldCompanies(rows).map((row) => row.ticker)).toEqual(["AAAA3"]);
  });
});

describe("leverOwnedNote", () => {
  const rows = [
    company({ ticker: "AAAA3", name: "Luz Nacional", lever: "ENERGY" }),
    company({ ticker: "BBBB3", name: "Energia do Sul", lever: "ENERGY" }),
    company({ ticker: "CCCC3", name: "Terceira Luz", lever: "ENERGY" }),
    company({ ticker: "DDDD3", name: "Petro", lever: "FUEL", status: "PRIVATIZED" }),
  ];

  it("lista os nomes da alavanca, com o e antes do último", () => {
    expect(leverOwnedNote(rows, "ENERGY")).toBe("Já tem: Luz Nacional, Energia do Sul e Terceira Luz");
    expect(leverOwnedNote(rows.slice(0, 1), "ENERGY")).toBe("Já tem: Luz Nacional");
  });

  it("a vendida não conta e a alavanca vazia vira a primeira do setor", () => {
    expect(leverOwnedNote(rows, "FUEL")).toBe("Nenhuma estatal de combustíveis por enquanto");
  });
});

describe("leverEffect", () => {
  const rules = {
    founding_share: "0.51",
    offer_sessions: 5,
    sizes: [],
    levers: [
      { lever: "FUEL", ipca_weight: "0.05", credit_weight: "0" },
      { lever: "ENERGY", ipca_weight: "0.04", credit_weight: "0" },
      { lever: "BANK", ipca_weight: "0", credit_weight: "0.05" },
    ],
  } as StateRules;

  it("o texto lê o peso que o backend entrega: 5% do índice, 10% de controle tira 0,5 ponto", () => {
    expect(leverEffect(rules, "FUEL")).toBe(
      "Segurar a gasolina baixa o IPCA: pesa cerca de 5% do índice. 10% de controle tira cerca de 0,5 ponto.",
    );
    expect(leverEffect(rules, "ENERGY")).toContain("pesa cerca de 4% do índice");
    expect(leverEffect(rules, "ENERGY")).toContain("tira cerca de 0,4 ponto");
  });

  it("o banco lê o peso do crédito, em ponto de juro", () => {
    expect(leverEffect(rules, "BANK")).toContain("tira cerca de 0,5 ponto do juro");
  });
});

describe("stakeNote", () => {
  it("conta importadas e fundadas, sem a vendida", () => {
    const rows = [
      company({ ticker: "AAAA3", origin: "IMPORTED" }),
      company({ ticker: "BBBB3" }),
      company({ ticker: "CCCC3" }),
      company({ ticker: "DDDD3", status: "PRIVATIZED" }),
    ];
    expect(stakeNote(rows)).toBe("3 empresas: 1 importada e 2 fundadas");
  });

  it("no singular quando é uma só", () => {
    expect(stakeNote([company({})])).toBe("1 empresa: 0 importadas e 1 fundada");
  });
});

describe("privatização em votação", () => {
  const queue = [queued(7, "2016-10-14")];

  it("o dia da votação vem da fila pelo id da medida", () => {
    expect(votesOnLabel(company({ privatization_measure_id: 7 }), queue)).toBe("vota em 14 out");
  });

  it("sem medida na fila, ou com a oferta já aberta, não há voto", () => {
    expect(votesOnLabel(company({}), queue)).toBeNull();
    expect(votesOnLabel(company({ privatization_measure_id: 9 }), queue)).toBeNull();
    expect(votesOnLabel(company({ privatization_measure_id: 7, status: "PRIVATIZING" }), queue)).toBeNull();
    // A medida já aprovada não espera mais o plenário
    const approved = [{ ...queued(7, "2016-10-14"), status: "APPROVED" } as GovernmentMeasure];
    expect(votesOnLabel(company({ privatization_measure_id: 7 }), approved)).toBeNull();
  });

  it("o chip de Suas ações junta ticker e dia", () => {
    expect(privatizeChip([company({ ticker: "CRDP3", privatization_measure_id: 7 })], queue)).toBe(
      "CRDP3 vota em 14 out",
    );
    expect(privatizeChip([company({})], queue)).toBeUndefined();
  });
});

describe("commandChip", () => {
  const holding = (name: string, control: "P10" | "P5") =>
    company({ name, in_force: { control, dividend_policy: "NORMAL" } });

  it("uma empresa segurando diz qual e quanto", () => {
    expect(commandChip([holding("Petrobras Nacional", "P10"), company({})])).toBe("Petrobras segurando 10%");
  });

  it("duas ou mais viram uma contagem", () => {
    expect(commandChip([holding("Petrobras Nacional", "P10"), holding("Luz Nacional", "P5")])).toBe(
      "2 estatais segurando o preço",
    );
  });

  it("sem controle em vigor não há chip", () => {
    expect(commandChip([company({})])).toBeUndefined();
  });
});

describe("movementText", () => {
  const movement = (partial: Partial<StateMovement>): StateMovement => ({
    day: "2016-06-01",
    kind: "FOUNDED",
    ticker: "LUZN3",
    control: null,
    dividend_policy: null,
    amount: null,
    ...partial,
  });

  it("cada tipo de movimento tem a sua frase", () => {
    expect(movementText(movement({}))).toBe("LUZN3 fundada pelo governo");
    expect(movementText(movement({ kind: "PRIVATIZATION_OPENED" }))).toBe(
      "Oferta de privatização da LUZN3 aberta à sala",
    );
    expect(movementText(movement({ kind: "PRIVATIZED", amount: "12200000000" }))).toBe(
      "LUZN3 privatizada · R$ 12,2 bi ao Tesouro",
    );
    expect(movementText(movement({ kind: "CONTROL_SET", control: "P10" }))).toBe(
      "LUZN3 passou a segurar o preço em 10%",
    );
    expect(movementText(movement({ kind: "CONTROL_RELEASED" }))).toBe("LUZN3 saiu do controle de preço");
    expect(movementText(movement({ kind: "DIVIDEND_POLICY_SET", dividend_policy: "SQUEEZE" }))).toBe(
      "LUZN3 passou a pagar dividendos no modo Espremer",
    );
  });
});

describe("oferta de privatização", () => {
  it("o ágio é o preço da oferta sobre o da bolsa", () => {
    // 10 sobre 9,35: 6,95% acima
    expect(offerPremium(offer({}))).toBeCloseTo(10 / 9.35 - 1);
    expect(offerPremium(offer({ market_price: null }))).toBeNull();
  });

  it("o rótulo diz acima, abaixo ou nada quando empata", () => {
    expect(premiumLabel(0.07)).toBe("7% acima da bolsa");
    expect(premiumLabel(-0.05)).toBe("5% abaixo da bolsa");
    expect(premiumLabel(0.001)).toBeNull();
  });

  it("a reserva custa ações vezes o preço, e a sala pediu metade das ações", () => {
    expect(reservationCost(offer({}), 120)).toBe(1200);
    expect(reservedShare(offer({}))).toBeCloseTo(0.5);
  });

  it("os dias que faltam contam do relógio da partida", () => {
    expect(offerDaysLabel(offer({}), "2016-10-18")).toBe("faltam 3 dias");
    expect(offerDaysLabel(offer({}), "2016-10-20")).toBe("falta 1 dia");
    expect(offerDaysLabel(offer({}), "2016-10-21")).toBe("último dia");
  });
});
