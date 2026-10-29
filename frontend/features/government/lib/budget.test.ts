import { describe, expect, it } from "vitest";
import type { BudgetMonth, BudgetTax } from "@/types";
import {
  accountBars,
  amountLabel,
  debtChangeNote,
  debtSeries,
  debtTone,
  effectHeadline,
  spendingHeadline,
  rateChangeLabel,
  relativeChange,
  defaultRateLabel,
  premiumNote,
  resultTone,
  shareLabel,
  signedShareLabel,
  todayRateLabel,
} from "./budget";

const month = (debt: string, premium = "0", closed = true): BudgetMonth => ({
  month_end: "2020-03-31",
  revenue: "0.1838",
  spending: "0.184",
  primary: "-0.0002",
  interest: "0.044",
  result: "-0.0442",
  debt,
  premium,
  gdp: "7400000000000",
  closed,
});

describe("shareLabel", () => {
  it("usa duas casas e, abaixo de 0,1%, três", () => {
    expect(shareLabel("0.0009")).toBe("0,09%");
    expect(shareLabel("0.1838")).toBe("18,38%");
    expect(shareLabel("0.00003")).toBe("0,003%");
  });

  it("escreve o negativo com o menos tipográfico", () => {
    expect(shareLabel("-0.0442")).toBe("−4,42%");
  });
});

describe("signedShareLabel", () => {
  it("põe o sinal e deixa o zero como traço", () => {
    expect(signedShareLabel("0.00003")).toBe("+0,003%");
    expect(signedShareLabel("-0.0002")).toBe("−0,02%");
    expect(signedShareLabel("0")).toBe("—");
  });
});

describe("amountLabel", () => {
  it("no mês mostra reais e no ano a fração do PIB", () => {
    expect(amountLabel("month", "0.1838", "113300000000")).toBe("R$ 113 bi");
    expect(amountLabel("year", "0.1838", "113300000000")).toBe("18,38%");
  });
});

describe("accountBars", () => {
  it("no déficit a barra de cima soma a receita e o déficit e fecha com a de baixo", () => {
    const bars = accountBars(month("0.7"));

    expect(bars.in.revenue + bars.in.deficit).toBeCloseTo(bars.out.spending + bars.out.interest, 6);
    expect(bars.out.surplus).toBe(0);
  });

  it("no superávit a sobra fecha a barra de baixo", () => {
    const bars = accountBars({ revenue: "0.2", spending: "0.15", interest: "0.03", result: "0.02" });

    expect(bars.in.deficit).toBe(0);
    expect(bars.in.revenue).toBe(1);
    expect(bars.out.spending + bars.out.interest + bars.out.surplus).toBeCloseTo(1, 6);
  });
});

describe("resultTone", () => {
  it("negativo é vermelho, positivo é verde e zero é neutro", () => {
    expect(resultTone("-0.01")).toBe("destructive");
    expect(resultTone("0.01")).toBe("success");
    expect(resultTone("0")).toBe("default");
  });
});

describe("debtChangeNote", () => {
  const history = Array.from({ length: 13 }, (_, i) => month(String(0.78 - i * 0.001)));

  it("compara com o fechamento de 12 meses atrás", () => {
    const now = month("0.769");
    const old = [month("0.778"), ...history.slice(1)];

    expect(debtChangeNote([...old.slice(0, 12), now].reverse().reverse(), now)).toBe("▼ 0,9 ponto em 12 meses");
  });

  it("sem um ano de contas não diz nada", () => {
    expect(debtChangeNote([month("0.7")], month("0.7"))).toBeNull();
  });
});

describe("premiumNote", () => {
  it("com prêmio, diz os pontos", () => {
    expect(premiumNote(month("0.778", "0.0187"), "0.5")).toBe("prêmio de 1,87 ponto");
  });

  it("sem prêmio, diz quanto falta para o piso", () => {
    expect(premiumNote(month("0.462"), "0.5")).toBe("sem prêmio · faltam 3,8 pontos para o prêmio");
  });
});

describe("debtTone", () => {
  it("prêmio pede atenção e dívida acima do PIB, alerta", () => {
    expect(debtTone(month("0.4"))).toBe("default");
    expect(debtTone(month("0.8", "0.01"))).toBe("warning");
    expect(debtTone(month("1.2", "0.09"))).toBe("destructive");
  });
});

describe("alíquotas", () => {
  const fixedIncome: BudgetTax = {
    key: "FIXED_INCOME",
    name: "Renda fixa · tabela",
    rate: "0.175",
    default_rate: "0.175",
    revenue: "0.0046",
    difference: "0",
    top_rate: "0.225",
    floor_rate: "0.1",
    default_top_rate: "0.225",
    default_floor_rate: "0.15",
  };

  it("na renda fixa mostra a faixa de hoje e a padrão", () => {
    expect(todayRateLabel(fixedIncome)).toBe("22,5% → 10%");
    expect(defaultRateLabel(fixedIncome)).toBe("22,5% → 15%");
  });

  it("imposto isento aparece como isenta", () => {
    const exempt: BudgetTax = {
      ...fixedIncome,
      key: "SECTOR",
      rate: null,
      top_rate: null,
      floor_rate: null,
      default_top_rate: null,
      default_floor_rate: null,
    };

    expect(todayRateLabel(exempt)).toBe("isenta");
    expect(defaultRateLabel(exempt)).toBe("17,5%");
  });
});

describe("debtSeries", () => {
  it("liga a projeção ao último fechamento e depois segue só com ela", () => {
    const march = month("0.70");
    const rows = debtSeries({
      month: march,
      history: [month("0.69"), march],
      projection: [month("0.71"), month("0.72")],
    });

    expect(rows).toHaveLength(4);
    expect(rows[1]).toMatchObject({ history: 0.7, projection: 0.7 });
    expect(rows[2]).toEqual({ time: rows[2]?.time, projection: 0.71 });
  });

  it("antes do primeiro fechamento parte da conta inicial", () => {
    const start = month("0.698", "0", false);
    const rows = debtSeries({ month: start, history: [start], projection: [month("0.7")] });

    expect(rows[0]).toMatchObject({ projection: 0.698 });
    expect(rows[0]?.history).toBeUndefined();
  });
});

describe("effectHeadline", () => {
  it("destaca a mudança na receita, em % do PIB e em reais", () => {
    expect(effectHeadline({ revenue_change: "-0.0008", revenue_change_amount: "-5900000000" })).toEqual({
      value: "−0,08%",
      detail: "do PIB por ano · cerca de R$ 5,9 bi por ano",
      tone: "destructive",
    });
  });

  it("mudança pequena demais vira aproximadamente zero", () => {
    expect(effectHeadline({ revenue_change: "0.000001", revenue_change_amount: "7000000" }).value).toBe("≈ 0,00%");
  });
});

describe("relativeChange", () => {
  it("mostra a variação relativa com sinal", () => {
    expect(relativeChange("0.0046", "0.0038")).toBe("−17%");
    expect(relativeChange("0.15", "0.30")).toBe("+100%");
  });

  it("sem base ou sem mudança não mostra nada", () => {
    expect(relativeChange("0", "0.1")).toBeNull();
    expect(relativeChange("0.1", "0.1")).toBeNull();
  });
});

describe("rateChangeLabel", () => {
  it("escreve de onde e para onde, com isenta quando não há alíquota", () => {
    expect(rateChangeLabel("0.15", null)).toBe("15% → isenta");
    expect(rateChangeLabel("0.184", "0.15")).toBe("18,4% → 15%");
  });
});

describe("spendingHeadline", () => {
  it("gasto a mais piora o resultado e pesa em vermelho", () => {
    const headline = spendingHeadline({ spending_change: "0.005", spending_change_amount: "37000000000" });
    expect(headline.value).toBe("−0,50%");
    expect(headline.detail).toContain("a mais de gasto");
    expect(headline.tone).toBe("destructive");
  });

  it("corte de gasto melhora o resultado e pesa em verde", () => {
    const headline = spendingHeadline({ spending_change: "-0.005", spending_change_amount: "-37000000000" });
    expect(headline.value).toBe("+0,50%");
    expect(headline.detail).toContain("a menos de gasto");
    expect(headline.tone).toBe("success");
  });

  it("variação abaixo de R$ 50 mi não conta", () => {
    expect(spendingHeadline({ spending_change: "0.000001", spending_change_amount: "7000000" }).tone).toBe("default");
  });
});
