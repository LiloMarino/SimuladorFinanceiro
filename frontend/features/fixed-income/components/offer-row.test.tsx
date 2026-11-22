import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import type { FixedIncomeOffer } from "@/types";
import { OfferRow } from "./offer-row";

const offer: FixedIncomeOffer = {
  asset_uuid: "0b9d6f0e-6a53-5f55-a1b6-1c1f6a0f8a11",
  name: "CDB da casa 3 anos",
  issuer: "Banco da casa",
  investment_type: "CDB",
  rate_index: "Prefixado",
  interest_rate: "0.1245",
  maturity_date: "2033-11-01",
  daily_liquidity: false,
  tax_exempt: false,
  income_tax_rate_at_maturity: "0.15",
  risk_premium: null,
  index_rate: "0",
  effective_annual_rate: "0.1245",
  offered_until: "2030-11-30",
  player_cap: "8000.00",
  fx_rate: null,
  fx_iof_rate: null,
  profession_offer: true,
};

function render(value: FixedIncomeOffer) {
  return renderToStaticMarkup(
    <MemoryRouter>
      <table>
        <tbody>
          <OfferRow offer={value} position={undefined} showApplied={false} showRate topRate={0.2} today="2030-11-01" />
        </tbody>
      </table>
    </MemoryRouter>,
  );
}

describe("OfferRow", () => {
  it("marca com o selo da profissão o CDB que só o Bancário recebe", () => {
    expect(render(offer)).toContain("da sua profissão");
  });

  it("não põe o selo na oferta do catálogo público", () => {
    expect(render({ ...offer, name: "CDB 110% CDI", profession_offer: false })).not.toContain("da sua profissão");
  });
});
