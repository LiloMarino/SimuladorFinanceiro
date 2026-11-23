import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import type { ProfessionMechanic } from "@/types";
import { LandlordBlock } from "./landlord-block";

vi.mock("../hooks/mutations/useBuyProperty", () => ({
  useBuyProperty: () => ({ mutate: vi.fn(), isPending: false }),
}));
vi.mock("../hooks/mutations/useSellProperty", () => ({
  useSellProperty: () => ({ mutate: vi.fn(), isPending: false }),
}));

type Landlord = Extract<ProfessionMechanic, { kind: "landlord" }>;
type Property = Landlord["properties"][number];

const property = (partial: Partial<Property>): Property => ({
  id: 1,
  name: "Apartamento 1 quarto",
  size: "STUDIO",
  value: "150000.00",
  status: "RENTED",
  rent: "750.00",
  next_readjustment: "2013-03-01",
  vacant_months: null,
  rerent: null,
  sale_due: null,
  ...partial,
});

const offers: Landlord["offers"] = [
  { size: "STUDIO", price: "160000.00", rent: "800.00", cost: "8000.00", bought: false },
  { size: "TWO_BEDROOM", price: "310000.00", rent: "1550.00", cost: "15500.00", bought: true },
  { size: "HOUSE", price: "520000.00", rent: "2600.00", cost: "26000.00", bought: false },
];

const mechanic = (partial: Partial<Landlord>): Landlord => ({
  kind: "landlord",
  status: "ACTIVE",
  income: "1750.00",
  rented: 2,
  total: 3,
  annual_yield: "0.0420",
  full_yield: "0.0600",
  cdi: "0.1000",
  vacancy_chance: "0.0500",
  properties: [
    property({}),
    property({ id: 2, name: "Apartamento 2 quartos", size: "TWO_BEDROOM", rent: "1000.00" }),
    property({
      id: 3,
      name: "Casa 3 quartos",
      size: "HOUSE",
      status: "VACANT",
      rent: null,
      next_readjustment: null,
      vacant_months: 2,
      rerent: "2500.00",
    }),
  ],
  total_value: "900000.00",
  offers_month: "2012-03-01",
  next_offers_on: "2012-04-01",
  offers,
  rent_rate: "0.005",
  cost_rate: "0.05",
  sale_months: 1,
  ...partial,
});

function render(landlord: Landlord) {
  // O formatador de moeda separa o R$ do valor com espaço sem quebra
  return renderToStaticMarkup(
    <MemoryRouter>
      <LandlordBlock mechanic={landlord} />
    </MemoryRouter>,
  ).replaceAll(String.fromCharCode(160), " ");
}

describe("LandlordBlock", () => {
  it("com imóveis, mostra o aluguel, o rendimento contra o CDI, a vacância e a tabela", () => {
    const html = render(mechanic({}));
    expect(html).toContain("Sua mecânica: imóveis");
    expect(html).toContain("R$ 1.750,00");
    expect(html).toContain("2 de 3 imóveis alugados");
    expect(html).toContain("4,2%");
    expect(html).toContain("cheio daria 6,0%");
    expect(html).toContain("5% por imóvel no mês");
    expect(html).toContain("Seus imóveis");
    expect(html).toContain("Casa 3 quartos");
    expect(html).toContain("R$ 900.000,00");
  });

  it("o imóvel vago mostra há quantos meses e com que aluguel volta", () => {
    const html = render(mechanic({}));
    expect(html).toContain("Vago há 2 meses");
    expect(html).toContain("volta com aluguel de R$ 2.500,00");
  });

  it("o imóvel à venda mostra o prazo e perde o botão de vender", () => {
    const selling = mechanic({
      properties: [property({ status: "SELLING", sale_due: "2012-04-02" })],
      total: 1,
      rented: 1,
    });
    const html = render(selling);
    expect(html).toContain("Vendendo");
    expect(html).toContain("conclui até");
    expect(html).not.toContain(">Vender<");
  });

  it("as ofertas trazem o preço, o aluguel inicial e o custo, e a já comprada fica marcada", () => {
    const html = render(mechanic({}));
    expect(html).toContain("Ofertas de março");
    expect(html).toContain("R$ 160.000,00");
    expect(html).toContain("aluguel inicial R$ 800,00");
    expect(html).toContain("custo de compra R$ 8.000,00");
    expect(html).toContain("Comprado este mês");
  });

  it("sem imóveis, avisa que a renda é zero e ainda oferece as compras do mês", () => {
    const html = render(mechanic({ total: 0, rented: 0, income: "0.00", properties: [], annual_yield: null }));
    expect(html).toContain("Nenhum imóvel agora.");
    expect(html).toContain("a renda do mês é zero");
    expect(html).not.toContain("Seus imóveis");
    expect(html).toContain("Comprar");
  });
});
