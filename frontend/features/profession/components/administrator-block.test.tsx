import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import type { ProfessionMechanic } from "@/types";
import { AdministratorBlock } from "./administrator-block";

vi.mock("../hooks/mutations/useSwitchSector", () => ({
  useSwitchSector: () => ({ mutate: vi.fn(), isPending: false }),
}));
vi.mock("../hooks/mutations/useEnrollExam", () => ({
  useEnrollExam: () => ({ mutate: vi.fn(), isPending: false }),
}));

type Administrator = Extract<ProfessionMechanic, { kind: "administrator" }>;

const mechanic = (partial: Partial<Administrator>): Administrator => ({
  kind: "administrator",
  status: "ACTIVE",
  sector: "CLT",
  senior_months: 12,
  sectors: [
    { sector: "CLT", months: 14, level: "1.00", senior: true, income: "5100.00", current: true },
    { sector: "EXPORTER", months: 9, level: "0.96", senior: false, income: "5890.00", current: false },
    { sector: "ENTREPRENEUR", months: 3, level: "0.89", senior: false, income: "6230.00", current: false },
    { sector: "BANKER", months: 0, level: "0.85", senior: false, income: "5270.00", current: false },
    { sector: "FREELANCER", months: 1, level: "0.86", senior: false, income: "4380.00", current: false },
    { sector: "BROKER", months: 0, level: "0.85", senior: false, income: "4920.00", current: false },
  ],
  switching_to: null,
  switch_entry_on: null,
  switch_month_income: "2550.00",
  switch_income_factor: "0.5",
  exam_status: "open",
  exam_open_until: "2012-04-30",
  exam_next_on: null,
  exam_extra_possible: false,
  exam_result_on: null,
  exam_income: "4080.00",
  exam_study_months: 6,
  exam_income_cut: "0.2",
  exam_pass_chance: "0.18",
  ...partial,
});

function render(administrator: Administrator) {
  // O formatador de moeda separa o R$ do valor com espaço sem quebra
  return renderToStaticMarkup(
    <MemoryRouter>
      <AdministratorBlock mechanic={administrator} />
    </MemoryRouter>,
  ).replaceAll(" ", " ");
}

describe("AdministratorBlock", () => {
  it("no setor CLT sênior com edital aberto, mostra a tabela de setores, a troca e a inscrição", () => {
    const html = render(mechanic({}));
    expect(html).toContain("Sua mecânica: setores e concurso");
    expect(html).toContain("Ativo");
    expect(html).toContain(
      "Você leva a renda do setor onde trabalha. A experiência em cada um sobe em 12 meses e não se perde ao sair.",
    );
    expect(html).toContain("Renda hoje");
    expect(html).toContain("atual");
    expect(html).toContain("14 meses · sênior");
    expect(html).toContain("9 meses · júnior");
    expect(html).toContain("0 meses · júnior");
    expect(html).toContain("1 mês · júnior");
    expect(html).toContain("0,96×");
    expect(html).toContain("R$ 5.890,00");
    expect(html).toContain(
      "A troca leva 1 mês com a renda pela metade. Leva só a renda do setor: sem a mecânica dele.",
    );
    expect(html).toContain("Trocar para…");
    expect(html).toContain("Edital aberto");
    expect(html).toContain(
      "Inscrições até 30 abr 2012. 6 meses de estudo com a renda 20% menor; chance de aprovação de 18%.",
    );
    expect(html).toContain("Aprovado, você vira Servidor com estabilidade, e a perde se sair.");
    expect(html).toContain("Inscrever");
    expect(html).not.toContain("Troca em andamento.");
  });

  it("trocando de setor, avisa a data de entrada e a renda pela metade, sem a tabela", () => {
    const html = render(
      mechanic({
        status: "LOCKED",
        switching_to: "EXPORTER",
        switch_entry_on: "2012-04-14",
        exam_status: "closed",
        exam_open_until: null,
        exam_next_on: "2012-07-01",
        exam_extra_possible: true,
      }),
    );
    expect(html).toContain("Travado");
    expect(html).toContain("Mudando para o Exportador.");
    expect(html).toContain("Troca em andamento.");
    expect(html).toContain("Você entra no Exportador em 14 abr 2012. Até lá a renda é a metade: R$ 2.550,00.");
    expect(html).toContain("Sem edital");
    expect(html).toContain("O próximo abre em jul 2012.");
    expect(html).toContain("Com o gasto do governo acima do normal, sai um edital a mais em julho.");
    expect(html).not.toContain("Renda hoje");
    expect(html).not.toContain("Trocar para…");
  });

  it("sem edital e sem gasto alto do governo, não promete o edital de julho", () => {
    const html = render(mechanic({ exam_status: "closed", exam_open_until: null, exam_next_on: "2012-10-01" }));
    expect(html).toContain("O próximo abre em out 2012.");
    expect(html).not.toContain("edital a mais em julho");
    expect(html).not.toContain("Inscrever");
  });

  it("estudando para o concurso, mostra o mês do resultado e a renda menor", () => {
    const html = render(mechanic({ exam_status: "studying", exam_open_until: null, exam_result_on: "2012-11-01" }));
    expect(html).toContain("Estudando");
    expect(html).toContain(
      "Resultado em nov 2012. Até lá a renda é 20% menor: R$ 4.080,00. Chance de aprovação de 18%.",
    );
    expect(html).not.toContain("Inscrições até");
  });
});
