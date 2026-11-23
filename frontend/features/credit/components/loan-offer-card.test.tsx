import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import type { CreditOverview } from "@/types";
import { LoanOfferCard } from "./loan-offer-card";

vi.mock("../hooks/queries/useLoanQuote", () => ({ useLoanQuote: () => ({ data: undefined }) }));
vi.mock("./payroll-offer", () => ({ PayrollOffer: () => null }));
vi.mock("./sign-impact", () => ({ SignImpact: () => null }));

const overview = {
  offer: { max_amount: "100000" },
  rating: { grade: "A", next_review: "2030-03-01" },
  portfolio_return_12m: null,
} as unknown as CreditOverview;

function render(payroll: boolean) {
  return renderToStaticMarkup(
    <LoanOfferCard overview={overview} spread="0.02" annualRate="0.15" currentDate="2030-01-02" payroll={payroll} />,
  );
}

describe("LoanOfferCard", () => {
  it("mostra a aba Consignado para o Servidor", () => {
    const html = render(true);
    expect(html).toContain("Consignado");
    expect(html).toContain("da sua profissão");
  });

  it("não mostra a aba Consignado para as outras profissões", () => {
    const html = render(false);
    expect(html).not.toContain("Consignado");
    expect(html).toContain("Nota A");
  });
});
