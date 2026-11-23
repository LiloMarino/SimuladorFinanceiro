import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import type { ProfessionMechanic } from "@/types";
import { FreelancerBlock } from "./freelancer-block";

vi.mock("../hooks/mutations/useSetPrice", () => ({
  useSetPrice: () => ({ mutate: vi.fn(), isPending: false }),
}));

type Freelancer = Extract<ProfessionMechanic, { kind: "freelancer" }>;

const mechanic = (partial: Partial<Freelancer>): Freelancer => ({
  kind: "freelancer",
  status: "ACTIVE",
  price: "180.00",
  price_since: "2012-03-01",
  deviation: "0.0909",
  reference: "165.00",
  reference_rise: "0.01",
  clients: "32",
  month_income: "5760.00",
  unemployment_note: "Com o desemprego em 5,5%, abaixo do neutro de 9%, a perda de clientes por cobrar caro é menor.",
  min_price: "132.00",
  max_price: "247.50",
  can_change_price: false,
  next_price_change: "2012-04-01",
  stalled_months: 0,
  stale: false,
  rows: [
    { price: "165.00", deviation: "0", clients: "34", income: "5610.00", empty_month_chance: "0.02" },
    { price: "180.00", deviation: "0.09", clients: "32", income: "5760.00", empty_month_chance: "0.03" },
    { price: "200.00", deviation: "0.21", clients: "27", income: "5400.00", empty_month_chance: "0.06" },
    { price: "220.00", deviation: "0.33", clients: "21", income: "4620.00", empty_month_chance: "0.11" },
  ],
  ...partial,
});

function render(freelancer: Freelancer) {
  return renderToStaticMarkup(
    <MemoryRouter>
      <FreelancerBlock mechanic={freelancer} />
    </MemoryRouter>,
  );
}

describe("FreelancerBlock", () => {
  it("com o preço salvo no mês, mostra os cartões, a tabela e o próximo ajuste", () => {
    const html = render(mechanic({}));
    expect(html).toContain("Sua mecânica: tabela de preços");
    expect(html).toContain("Referência do mercado");
    expect(html).toContain("sobe com o IPCA todo mês");
    expect(html).toContain("por atendimento, desde");
    expect(html).toContain("× 32 clientes");
    expect(html).toContain("Quanto cada preço daria este mês");
    expect(html).toContain("igual à referência");
    expect(html).toContain("33% acima");
    expect(html).toContain("próximo ajuste em 01 abr 2012");
    expect(html).toContain("abaixo do neutro de 9%");
    expect(html).toContain("Histórico da profissão");
    expect(html).not.toContain("A inflação está comendo a sua renda");
  });

  it("com o preço parado atrás da referência, avisa e mostra quanto a referência subiu", () => {
    const html = render(
      mechanic({
        status: "AVAILABLE",
        price: "150.00",
        price_since: "2011-01-01",
        deviation: "-0.0909",
        reference_rise: "0.1",
        stalled_months: 14,
        stale: true,
        can_change_price: true,
        next_price_change: null,
      }),
    );
    expect(html).toContain("O preço está parado há 14 meses.");
    expect(html).toContain("subiu 10% desde o seu último ajuste");
    expect(html).toContain("A inflação está comendo a sua renda.");
    expect(html).toContain("O preço ficou 9% atrás da referência");
    expect(html).toContain("uma mudança por mês");
  });
});
