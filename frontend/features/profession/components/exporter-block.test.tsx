import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import type { ProfessionMechanic } from "@/types";
import { ExporterBlock } from "./exporter-block";

vi.mock("../hooks/mutations/useLockExchange", () => ({
  useLockExchange: () => ({ mutate: vi.fn(), isPending: false }),
}));
vi.mock("../hooks/mutations/useSetExportMix", () => ({
  useSetExportMix: () => ({ mutate: vi.fn(), isPending: false }),
}));

type Exporter = Extract<ProfessionMechanic, { kind: "exporter" }>;

const mechanic = (partial: Partial<Exporter>): Exporter => ({
  kind: "exporter",
  status: "AVAILABLE",
  dollar: "1.79",
  dollar_change: "0.061",
  growth: "0.014",
  export_share: "0.6",
  exported_factor: "1.05",
  domestic_factor: "0.98",
  mix_factor: "1.02",
  exported_revenue: "6000",
  can_change_mix: false,
  next_mix_change: "2012-04-01",
  lock_options: [
    { months: 6, locked_dollar: "1.906" },
    { months: 12, locked_dollar: "2.0294" },
  ],
  lock: null,
  ...partial,
});

const lock = (partial: Partial<NonNullable<Exporter["lock"]>>): NonNullable<Exporter["lock"]> => ({
  locked_dollar: "1.985",
  share: "0.5",
  months: 12,
  paid_months: 2,
  expires_on: "2013-01-05",
  dollar_gap: "0.195",
  gain: "653.63",
  ...partial,
});

function render(exporter: Exporter) {
  return renderToStaticMarkup(
    <MemoryRouter>
      <ExporterBlock mechanic={exporter} />
    </MemoryRouter>,
  );
}

describe("ExporterBlock", () => {
  it("com a trava ganhando, mostra o ganho, a validade e o link do dólar futuro", () => {
    const html = render(mechanic({ status: "ACTIVE", lock: lock({}) }));
    expect(html).toContain("Trava ativa");
    expect(html).toContain("Histórico da profissão");
    expect(html).toContain("Ganho da trava até agora");
    expect(html).toContain("+R$");
    expect(html).toContain("a trava paga R$ 0,1950 a mais por dólar");
    expect(html).toContain("2 de 12 meses");
    expect(html).toContain("Ver o dólar futuro");
    expect(html).toContain("próxima mudança em");
  });

  it("sem trava, oferece contratar com o dólar de cada prazo", () => {
    const html = render(mechanic({ next_mix_change: null, can_change_mix: true }));
    expect(html).toContain("Nenhuma trava agora");
    expect(html).toContain("Travar 50% por 12 meses");
    expect(html).toContain("R$ 1,9060");
    expect(html).toContain("R$ 2,0294");
    expect(html).toContain("na metade da receita");
    expect(html).toContain("uma mudança por trimestre");
  });

  it("com a trava perdendo, mostra o resultado negativo e a explicação da alta", () => {
    const html = render(
      mechanic({ status: "ACTIVE", dollar: "2.14", lock: lock({ dollar_gap: "-0.155", gain: "-1521.03" }) }),
    );
    expect(html).toContain("O dólar subiu depois da trava.");
    expect(html).toContain("Resultado da trava até agora");
    expect(html).toContain("−R$");
    expect(html).toContain("a trava paga R$ 0,1550 a menos por dólar");
    expect(html).toContain("é o preço da previsibilidade");
  });
});
