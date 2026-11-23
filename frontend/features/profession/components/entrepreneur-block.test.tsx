import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import type { ProfessionMechanic } from "@/types";
import { EntrepreneurBlock } from "./entrepreneur-block";

vi.mock("../hooks/mutations/useSetReinvestShare", () => ({
  useSetReinvestShare: () => ({ mutate: vi.fn(), isPending: false }),
}));
vi.mock("../hooks/mutations/useSellCapital", () => ({
  useSellCapital: () => ({ mutate: vi.fn(), isPending: false }),
}));

type Entrepreneur = Extract<ProfessionMechanic, { kind: "entrepreneur" }>;

const mechanic = (partial: Partial<Entrepreneur>): Entrepreneur => ({
  kind: "entrepreneur",
  status: "ACTIVE",
  capital: "38000.00",
  capital_months_ago: "36000.00",
  income: "342.00",
  rate: "0.009",
  growth: "0.014",
  profit: "7200.00",
  reinvest_share: "0.3",
  reinvested: "2160.00",
  recession: false,
  negative_quarters: 0,
  sale_options: [
    { share: "0.1", part: "3800.00", proceeds: "3040.00" },
    { share: "0.25", part: "9500.00", proceeds: "7600.00" },
    { share: "0.5", part: "19000.00", proceeds: "15200.00" },
    { share: "1", part: "38000.00", proceeds: "30400.00" },
  ],
  ...partial,
});

function render(entrepreneur: Entrepreneur) {
  // O formatador de moeda separa o R$ do valor com espaço sem quebra
  return renderToStaticMarkup(
    <MemoryRouter>
      <EntrepreneurBlock mechanic={entrepreneur} />
    </MemoryRouter>,
  ).replaceAll(" ", " ");
}

describe("EntrepreneurBlock", () => {
  it("reinvestindo com o PIB positivo, mostra o capital, a renda, a régua e a venda", () => {
    const html = render(mechanic({}));
    expect(html).toContain("Sua mecânica: reinvestimento");
    expect(html).toContain("Capital da empresa");
    expect(html).toContain("Renda do capital no mês");
    expect(html).toContain("0,9% ao mês com o PIB 12 meses em 1,4%");
    expect(html).toContain("a sua renda antes do reinvestimento");
    expect(html).toContain("30%");
    expect(html).toContain("R$ 2.160,00");
    expect(html).toContain("R$ 5.040,00");
    expect(html).toContain("Vale a partir do próximo mês");
    expect(html).toContain("Vender parte da empresa");
    expect(html).toContain("25% do capital é R$ 9.500,00");
    expect(html).toContain("R$ 7.600,00");
    expect(html).toContain("Vender 25%");
    expect(html).toContain("Carteira, linha Capital da empresa");
    expect(html).toContain("Histórico da profissão");
    expect(html).not.toContain("Recessão");
    expect(html).not.toContain("Cada real reinvestido agora encolhe");
  });

  it("em recessão, avisa que o capital encolhe e mostra de quanto ele era", () => {
    const html = render(
      mechanic({
        capital: "35000.00",
        capital_months_ago: "38000.00",
        income: "-490.00",
        rate: "-0.014",
        growth: "-0.012",
        recession: true,
        negative_quarters: 2,
      }),
    );
    expect(html).toContain("Recessão: o capital está encolhendo.");
    expect(html).toContain("era R$ 38.000,00 há 3 meses");
    expect(html).toContain("O PIB está negativo há 2 trimestres.");
    expect(html).toContain("Cada real reinvestido agora encolhe");
    expect(html).toContain("text-destructive");
  });

  it("sem capital, deixa o botão de vender desligado", () => {
    const html = render(mechanic({ status: "AVAILABLE", capital: "0.00", capital_months_ago: null }));
    expect(html).toMatch(/<button[^>]*disabled[^>]*>Vender 25%/);
  });
});
