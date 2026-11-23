import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import type { ProfessionMechanic } from "@/types";
import { WelfareBlock } from "./welfare-block";

vi.mock("../hooks/mutations/useEnrollCourse", () => ({
  useEnrollCourse: () => ({ mutate: vi.fn(), isPending: false }),
}));

type Welfare = Extract<ProfessionMechanic, { kind: "welfare" }>;

const mechanic = (partial: Partial<Welfare>): Welfare => ({
  kind: "welfare",
  status: "ACTIVE",
  balance: "1840.00",
  next_release_on: "2014-01-02",
  cash_was_negative: false,
  deposit: "120.00",
  surplus: "600.00",
  deposit_rate: "0.2",
  deposit_cap: "140.00",
  deposit_factor: "1",
  full_expense: "1600.00",
  paid_expense: "1360.00",
  discount: "240.00",
  gig_income: "1400.00",
  gig_income_in_course: "700.00",
  clt_salary: "2300.00",
  in_course: false,
  course_months: 12,
  course_months_done: null,
  course_ends_on: null,
  ...partial,
});

function render(welfare: Welfare) {
  // O formatador de moeda separa o R$ do valor com espaço sem quebra
  return renderToStaticMarkup(
    <MemoryRouter>
      <WelfareBlock mechanic={welfare} />
    </MemoryRouter>,
  ).replaceAll(" ", " ");
}

describe("WelfareBlock", () => {
  it("poupando, mostra o saldo, o depósito do mês, a tarifa social e a matrícula no curso", () => {
    const html = render(mechanic({}));
    expect(html).toContain("Sua mecânica: Pé-de-Meia, tarifa social e curso técnico");
    expect(html).toContain("Ativo");
    expect(html).toContain("R$ 1.840,00");
    expect(html).toContain("travado · libera em jan 2014");
    expect(html).toContain("caixa nunca negativo no período");
    expect(html).toContain("Depósito deste mês");
    expect(html).toContain("R$ 120,00");
    expect(html).toContain("20% da sobra de R$ 600,00 · teto de R$ 140,00");
    expect(html).toContain("−R$ 240,00 por mês");
    expect(html).toContain("despesa de R$ 1.360,00 no lugar de R$ 1.600,00");
    expect(html).toContain("O depósito acompanha o gasto do governo com auxílio: hoje 1,0×.");
    expect(html).toContain("O saldo libera a cada 2 anos, se o caixa não ficou negativo no período.");
    expect(html).toContain("12 meses com a renda do bico pela metade (R$ 700,00 em vez de R$ 1.400,00).");
    expect(html).toContain("salário de R$ 2.300,00");
    expect(html).toContain("O saldo de R$ 1.840,00 cai no seu caixa.");
    expect(html).toContain("Matricular");
    expect(html).toContain("Carteira, linha Pé-de-Meia");
    expect(html).toContain("Histórico da profissão");
    expect(html).not.toContain("Curso técnico em andamento.");
  });

  it("com o caixa negativo no período, avisa que a liberação pula para a data seguinte", () => {
    const html = render(mechanic({ cash_was_negative: true }));
    expect(html).toContain("caixa negativo no período: a liberação pula para a data seguinte");
    expect(html).not.toContain("caixa nunca negativo no período");
  });

  it("sem sobra no mês, o depósito diz que não há sobra e mantém o teto", () => {
    const html = render(mechanic({ surplus: "-300.00", deposit: "0.00" }));
    expect(html).toContain("sem sobra no mês até agora · teto de R$ 140,00");
    expect(html).not.toContain("da sobra de");
  });

  it("no curso técnico, mostra o andamento, a conclusão e o que o CLT muda", () => {
    const html = render(mechanic({ in_course: true, course_months_done: 7, course_ends_on: "2012-08-02" }));
    expect(html).toContain("Curso técnico em andamento.");
    expect(html).toContain("7");
    expect(html).toContain("de 12 meses");
    expect(html).toContain("Conclui em ago 2012 · renda do bico pela metade até lá: R$ 700,00");
    expect(html).toContain("Em ago 2012 você");
    expect(html).toContain("salário de R$ 2.300,00, FGTS e hora extra");
    expect(html).toContain("Pé-de-Meia R$ 1.840,00 e tarifa social seguem até a conclusão.");
    expect(html).not.toContain("Matricular");
    expect(html).toContain("Carteira, linha Pé-de-Meia");
  });
});
