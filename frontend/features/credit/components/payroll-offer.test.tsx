import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { CreditOverview, PayrollQuote } from "@/types";
import { PayrollOffer } from "./payroll-offer";

const quoteState = vi.hoisted(() => ({
  current: { data: undefined, error: null, refetch: () => Promise.resolve() } as {
    data: PayrollQuote | undefined;
    error: Error | null;
    refetch: () => Promise<unknown>;
  },
}));

vi.mock("../hooks/queries/usePayrollQuote", () => ({ usePayrollQuote: () => quoteState.current }));
vi.mock("./review-payroll-dialog", () => ({ ReviewPayrollDialog: () => null }));

const overview = { rating: { next_review: "2030-03-01" } } as unknown as CreditOverview;

const quote = (partial: Partial<PayrollQuote>): PayrollQuote => ({
  amount: "5000",
  term_months: 12,
  annual_rate: "0.15",
  monthly_rate: "0.0117",
  installment: "450",
  total_interest: "400",
  total_paid: "5400",
  net_salary: "4000",
  margin: "1400",
  margin_used: "0",
  margin_free: "1400",
  max_amount: "15000",
  fits_margin: true,
  max_by_term: [],
  margin_free_after: "950",
  debt_after: "5000",
  leverage_after: "0.5",
  schedule: [],
  debt_limit_room: "50000",
  fits_debt_limit: true,
  first_installment_date: "2030-02-01",
  common_annual_rate: "0.25",
  common_total_interest: "700",
  interest_saved: "300",
  ...partial,
});

function render() {
  return renderToStaticMarkup(<PayrollOffer overview={overview} currentDate="2030-01-02" />);
}

describe("PayrollOffer", () => {
  beforeEach(() => {
    quoteState.current = { data: undefined, error: null, refetch: () => Promise.resolve() };
  });

  it("mostra a parcela e o juro a menos quando o valor cabe na margem", () => {
    quoteState.current.data = quote({});
    const html = render();
    expect(html).toContain("Parcela mensal");
    expect(html).toContain("a menos que no comum");
    expect(html).not.toContain("Passa da margem");
  });

  it("lê do servidor a margem que sobra depois da parcela e oferece o cronograma", () => {
    quoteState.current.data = quote({ margin_free_after: "777" });
    const html = render();
    expect(html).toContain("777");
    expect(html).toContain("Ver as 12 parcelas");
  });

  it("oferece o máximo do prazo quando o valor passa da margem", () => {
    quoteState.current.data = quote({
      fits_margin: false,
      max_amount: "3000",
      margin_used: "400",
      margin_free: "1000",
    });
    const html = render();
    expect(html).toContain("Passa da margem");
    expect(html).toContain("Usar o máximo");
  });

  it("avisa quando a margem foi toda usada", () => {
    quoteState.current.data = quote({ fits_margin: false, margin_used: "1400", margin_free: "0", max_amount: "0" });
    const html = render();
    expect(html).toContain("Sem margem livre.");
    expect(html).not.toContain("Usar o máximo");
  });

  it("avisa quando o limite de dívida acabou", () => {
    quoteState.current.data = quote({ fits_debt_limit: false, debt_limit_room: "0" });
    expect(render()).toContain("Sem limite de dívida.");
  });

  it("oferece calcular de novo quando a simulação falha", () => {
    quoteState.current.error = new Error("falhou");
    expect(render()).toContain("Calcular de novo");
  });
});
