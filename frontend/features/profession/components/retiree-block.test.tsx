import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import type { ProfessionMechanic } from "@/types";
import { RetireeBlock } from "./retiree-block";

vi.mock("../hooks/mutations/useConvertPension", () => ({
  useConvertPension: () => ({ mutate: vi.fn(), isPending: false }),
}));
vi.mock("../hooks/mutations/useRedeemPension", () => ({
  useRedeemPension: () => ({ mutate: vi.fn(), isPending: false }),
}));

type Retiree = Extract<ProfessionMechanic, { kind: "retiree" }>;

const mechanic = (partial: Partial<Retiree>): Retiree => ({
  kind: "retiree",
  status: "ACTIVE",
  balance: "40000.00",
  annual_rate: "0.1",
  cdi: "0.11",
  converted_income: "0.00",
  converted_amount: "0.00",
  converted_real_rate: null,
  real_rate: "0.081",
  selic: "0.1125",
  expected_ipca: "0.0313",
  expected_ipca_from_focus: true,
  income_rate: "0.0065405",
  inflation_indexed: true,
  redeem_rate: "0.30",
  months_in_plan: 40,
  next_rate: "0.25",
  next_rate_months: 8,
  next_rate_on: "2012-11-01",
  brackets: [
    { label: "até 2 anos", rate: "0.35", current: false },
    { label: "2 a 4 anos", rate: "0.30", current: true },
    { label: "4 a 6 anos", rate: "0.25", current: false },
    { label: "6 a 8 anos", rate: "0.20", current: false },
    { label: "8 a 10 anos", rate: "0.15", current: false },
    { label: "mais de 10 anos", rate: "0.10", current: false },
  ],
  ...partial,
});

function render(retiree: Retiree) {
  // O formatador de moeda separa o R$ do valor com espaço sem quebra
  return renderToStaticMarkup(
    <MemoryRouter>
      <RetireeBlock mechanic={retiree} />
    </MemoryRouter>,
  ).replaceAll(" ", " ");
}

describe("RetireeBlock", () => {
  it("sem conversão, mostra o saldo, o IR de hoje e as duas saídas sobre metade do saldo", () => {
    const html = render(mechanic({}));
    expect(html).toContain("Sua mecânica: previdência");
    expect(html).toContain("Saldo da previdência");
    expect(html).toContain("R$ 40.000,00");
    expect(html).toContain("nenhuma ainda");
    expect(html).toContain("3 anos e 4 meses no plano");
    expect(html).toContain("Converter em renda");
    expect(html).toContain("para sempre, corrigida pelo IPCA");
    expect(html).toContain("Converter R$ 20.000,00");
    expect(html).toContain("Resgatar agora");
    expect(html).toContain("R$ 14.000,00 líquido");
    expect(html).toContain("IR de 30%: R$ 6.000,00 ficam com a Receita");
    expect(html).toContain("Em 8 meses o IR cai para 25%");
    expect(html).toContain("Converter é para sempre");
    expect(html).toContain("Carteira, linha Previdência");
    expect(html).toContain("Histórico da profissão");
  });

  it("com renda convertida, mostra a renda e de quanto ela veio", () => {
    const html = render(
      mechanic({ converted_income: "130.81", converted_amount: "20000.00", converted_real_rate: "0.081" }),
    );
    expect(html).toContain("R$ 130,81");
    expect(html).toContain("por mês, de R$ 20.000,00 a juro real de 8,1%");
    expect(html).not.toContain("nenhuma ainda");
  });

  it("na sala sem correção, a renda não diz que é corrigida pelo IPCA", () => {
    const html = render(mechanic({ inflation_indexed: false }));
    expect(html).toContain("para sempre · juro real de hoje");
    expect(html).not.toContain("corrigida pelo IPCA");
  });

  it("com juro real zerado, avisa e desabilita a conversão", () => {
    const html = render(mechanic({ real_rate: "-0.01" }));
    expect(html).toContain("O juro real de hoje está zerado ou negativo");
  });

  it("na última faixa, não fala de próxima faixa", () => {
    const html = render(mechanic({ redeem_rate: "0.10", next_rate: null, next_rate_months: null, next_rate_on: null }));
    expect(html).not.toContain("o IR cai para");
  });
});
