import { describe, expect, it } from "vitest";
import {
  exchangeText,
  exitPaymentNote,
  mergeBlockReason,
  mergeDescription,
  mergeChoices,
  exitVoteNote,
  partnerFavor,
  partnerNote,
  ratioFormula,
  rejectionNote,
  shortfallText,
  type AssemblyMerge,
  type MergeSide,
} from "./fund-merge";
import type { AssemblyOption } from "./fund-assembly";
import type { FundDetails } from "@/types";

// O dinheiro formatado separa "R$" do valor com espaço não separável
const plain = (text: string | null) => text?.replaceAll(" ", " ") ?? null;

const side = (over: Partial<MergeSide> = {}): MergeSide => ({
  fund_id: 1,
  ticker: "AURO11",
  name: "Aurora Gestão",
  nav: "110.44",
  cash: "42000",
  ...over,
});

const merge = (over: Partial<AssemblyMerge> = {}): AssemblyMerge => ({
  mother: side(),
  daughter: side({ fund_id: 2, ticker: "BORE11", name: "Boreal Renda", nav: "55.22" }),
  is_mother: true,
  ratio: "0.5",
  partner_tally: { in_favor: "0", against: "0", abstention: "0", total: "0", missing_to_win: "0" },
  partner_voted_share: "0.52",
  partner_in_favor_share: "0.71",
  exit_quotas: "0",
  exit_amount: "0",
  shortfall: "0",
  ...over,
});

describe("exchangeText", () => {
  it("a incorporada que vale menos por cota entrega várias cotas por uma", () => {
    expect(exchangeText("BORE11", "AURO11", "0.5")).toBe("2 BORE11 = 1 AURO11");
  });

  it("a incorporada que vale mais por cota entrega uma por várias", () => {
    expect(exchangeText("BORE11", "AURO11", "2.5")).toBe("1 BORE11 = 2,5 AURO11");
  });

  it("arredonda a razão em 4 casas", () => {
    expect(exchangeText("BORE11", "AURO11", "0.55")).toBe("1,8182 BORE11 = 1 AURO11");
  });
});

describe("ratioFormula", () => {
  it("mostra a conta do patrimônio por cota", () => {
    expect(plain(ratioFormula(side({ nav: "55.22" }), side(), "0.5"))).toBe("hoje R$ 55,22 ÷ R$ 110,44 = 0,5");
  });

  it("sem patrimônio por cota não há conta", () => {
    expect(ratioFormula(side({ nav: null }), side(), null)).toBeNull();
  });
});

describe("exitPaymentNote", () => {
  it("o caixa da incorporada paga primeiro e a incorporadora completa", () => {
    expect(plain(exitPaymentNote(side({ name: "Boreal Renda" }), side()))).toBe(
      "Pago pelo caixa da Boreal Renda (hoje R$ 42.000,00) e pela renda fixa de liquidez diária dela; o que faltar, a Aurora Gestão paga do próprio caixa e da própria renda fixa logo após a incorporação",
    );
  });
});

describe("exitVoteNote", () => {
  it("a incorporada paga antes da incorporação", () => {
    expect(exitVoteNote({ name: "Boreal Renda" })).toBe("Pago pela Boreal Renda antes da incorporação");
  });
});

describe("partnerNote e partnerFavor", () => {
  it("dizem a participação e o lado que vence na outra assembleia", () => {
    expect(partnerNote(merge())).toBe("Sai se as duas aprovarem; lá votaram 52% das cotas");
    expect(partnerFavor(merge())).toBe("71,0% a favor");
  });

  it("sem votos não há lado", () => {
    expect(partnerFavor(merge({ partner_in_favor_share: null }))).toBe("sem votos");
  });
});

describe("mergeChoices", () => {
  it("na incorporadora o voto contra mantém as duas separadas", () => {
    expect(mergeChoices(merge())).toEqual({
      favor: "A Aurora Gestão incorpora a Boreal Renda",
      against: "As duas seguem separadas",
    });
  });

  it("na incorporada o voto contra avisa da saída pelo patrimônio por cota", () => {
    const choices = mergeChoices(merge({ is_mother: false }));
    expect(choices.favor).toBe("A Aurora Gestão incorpora esta gestora");
    expect(choices.against).toContain("você sai pelo patrimônio por cota");
  });
});

describe("shortfallText", () => {
  it("com falta diz quanto falta", () => {
    expect(plain(shortfallText("3000"))).toContain("faltam R$ 3.000,00");
  });

  it("com falta diz que a fusão cai no fechamento", () => {
    expect(shortfallText("3000")).toContain("Se ainda faltar no fechamento, a fusão é rejeitada.");
  });

  it("sem falta não há aviso", () => {
    expect(shortfallText("0")).toBeNull();
  });
});

describe("rejectionNote", () => {
  it("a fusão rejeitada por falta de caixa diz quanto faltou", () => {
    expect(plain(rejectionNote({ merge_shortfall: "1250.5" }))).toBe(
      "Rejeitada: o caixa e a renda fixa de liquidez diária das duas gestoras não cobriam a saída de quem votou contra (faltavam R$ 1.250,50).",
    );
  });

  it("a votação decidida pelo voto não tem nota", () => {
    expect(rejectionNote({ merge_shortfall: null })).toBeNull();
  });
});

describe("mergeBlockReason", () => {
  const panel: FundDetails["assembly"] = {
    current: [],
    history: [],
    options: [],
    merge_partners: [],
    convene_quotas: "100",
    my_quotas: "40",
    blocked_founding_until: null,
  };

  const option = (over: Partial<AssemblyOption> = {}): AssemblyOption => ({
    agenda: "MERGE",
    can_convene: false,
    block: null,
    next_allowed_on: null,
    ...over,
  });

  it("a fusão em votação é das duas gestoras", () => {
    expect(mergeBlockReason(option({ block: "pending", next_allowed_on: "2026-11-24" }), panel)).toBe(
      "Já há uma fusão das duas em votação, até 24/11.",
    );
  });

  it("os demais motivos seguem o texto geral", () => {
    expect(mergeBlockReason(option({ block: "manager_only" }), panel)).toBe("Só o gestor propõe a fusão.");
    expect(mergeBlockReason(undefined, panel)).toBeNull();
  });
});

describe("mergeDescription", () => {
  it("nomeia a outra gestora quando é uma só", () => {
    expect(mergeDescription([side({ name: "Boreal Renda", ticker: "BORE11" })])).toBe(
      "Você gere também a Boreal Renda (BORE11): a fusão junta as duas numa só e vai à assembleia de cada uma",
    );
  });

  it("conta as outras quando são várias", () => {
    expect(mergeDescription([side(), side()])).toBe(
      "Você gere outras 2 gestoras: a fusão junta duas delas numa só e vai à assembleia de cada uma",
    );
  });

  it("sem parceiro listado diz o que a fusão faz", () => {
    expect(mergeDescription([])).toBe("Junta duas gestoras que você gere numa só, e as duas assembleias votam");
  });
});
