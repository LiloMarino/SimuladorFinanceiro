import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import type { ProfessionMechanic } from "@/types";
import { GraduateBlock } from "./graduate-block";

vi.mock("../hooks/mutations/useEnrollStep", () => ({
  useEnrollStep: () => ({ mutate: vi.fn(), isPending: false }),
}));
vi.mock("../hooks/mutations/useLeaveHome", () => ({
  useLeaveHome: () => ({ mutate: vi.fn(), isPending: false }),
}));

type Graduate = Extract<ProfessionMechanic, { kind: "graduate" }>;
type Row = Graduate["steps"][number];

const row = (partial: Partial<Row>): Row => ({
  step: "SPECIALIZATION",
  status: "later",
  months: 12,
  months_done: null,
  concluded_on: null,
  ends_on: null,
  final_multiple: "1.6",
  tuition: null,
  stipend: null,
  unemployment_discount: false,
  ...partial,
});

const mechanic = (partial: Partial<Graduate>): Graduate => ({
  kind: "graduate",
  status: "AVAILABLE",
  salary: "2900.00",
  stipend_income: null,
  career_year: 3,
  final_multiple: "1.3",
  next_final_multiple: "1.6",
  next_step: "SPECIALIZATION",
  steps: [
    row({ step: "GRADUATION", status: "done", months: 0, concluded_on: "2009-12-01", final_multiple: "1.3" }),
    row({ status: "next", tuition: "450.00" }),
    row({ step: "MASTERS", months: 24, final_multiple: "2.2", stipend: "1500.00" }),
    row({ step: "DOCTORATE", months: 48, final_multiple: "3.0", stipend: "2200.00" }),
  ],
  next_opens_on: null,
  months_left: null,
  unemployment: "0.055",
  neutral_unemployment: "0.09",
  unemployment_discount: false,
  tuition_discount_rate: "0.3",
  stipend_bonus_rate: "0.2",
  home: "with_parents",
  home_discount_rate: "0.4",
  home_discount: "640.00",
  home_until: "2013-03-01",
  full_expense: "1600.00",
  ...partial,
});

function render(graduate: Graduate) {
  // O formatador de moeda separa o R$ do valor com espaço sem quebra
  return renderToStaticMarkup(
    <MemoryRouter>
      <GraduateBlock mechanic={graduate} />
    </MemoryRouter>,
  ).replaceAll(" ", " ");
}

describe("GraduateBlock", () => {
  it("no estado padrão, mostra os números, a escada com a matrícula e a saída de casa", () => {
    const html = render(mechanic({}));
    expect(html).toContain("Sua mecânica: escada acadêmica e mora com os pais");
    expect(html).toContain("Salário hoje");
    expect(html).toContain("R$ 2.900,00");
    expect(html).toContain("ano 3 da carreira");
    expect(html).toContain("1,3× → 1,6×");
    expect(html).toContain("ao concluir a especialização");
    expect(html).toContain("−R$ 640,00 por mês");
    expect(html).toContain("despesa 40% menor até mar 2013");
    expect(html).toContain("concluída em dez 2009");
    expect(html).toContain("mensalidade de R$ 450,00 · trabalha junto");
    expect(html).toContain("bolsa de R$ 1.500,00 no lugar do salário");
    expect(html).toContain(
      "Matricular com o desemprego acima do neutro de 9% dá desconto na mensalidade e bolsa maior.",
    );
    expect(html).toContain("Hoje: 5,5%, sem desconto.");
    expect(html).toContain("A despesa volta ao normal, R$ 1.600,00 por mês, e não dá para voltar.");
    expect(html).toContain("Histórico da profissão");
    expect(html).not.toContain("Um degrau por vez.");
  });

  it("com um degrau em curso, trava o próximo e avisa quando ele abre", () => {
    const html = render(
      mechanic({
        status: "ACTIVE",
        next_step: "MASTERS",
        final_multiple: "1.3",
        next_final_multiple: "2.2",
        next_opens_on: "2012-08-01",
        months_left: 5,
        steps: [
          row({ step: "GRADUATION", status: "done", months: 0, concluded_on: "2009-12-01", final_multiple: "1.3" }),
          row({
            status: "current",
            months_done: 7,
            ends_on: "2012-08-01",
            tuition: "450.00",
          }),
          row({ step: "MASTERS", months: 24, final_multiple: "2.2", stipend: "1500.00" }),
          row({ step: "DOCTORATE", months: 48, final_multiple: "3.0", stipend: "2200.00" }),
        ],
      }),
    );
    expect(html).toContain("Especialização em curso: o próximo degrau abre ao concluir.");
    expect(html).toContain("Especialização · 7 de 12 meses");
    expect(html).toContain("conclui em ago 2012");
    expect(html).toContain("O mestrado abre em ago 2012, quando a especialização acabar.");
    expect(html).toContain("Faltam 5 meses.");
    expect(html).toContain("Um degrau por vez.");
    expect(html).toContain("até mar 2013");
    expect(html).not.toContain("Matricular com o desemprego");
  });

  it("depois de sair de casa, mostra o estado sem desconto e esconde o botão", () => {
    const html = render(mechanic({ home: "left", home_discount: "0.00" }));
    expect(html).toContain("Saiu de casa");
    expect(html).toContain("despesa cheia de R$ 1.600,00 por mês");
    expect(html).not.toContain("A despesa volta ao normal");
  });
});
