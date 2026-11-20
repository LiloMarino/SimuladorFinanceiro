import { describe, expect, it } from "vitest";
import type { FundDetails } from "@/types";
import { issuanceRows } from "./fund-issuances";

const fund = (overrides: Partial<FundDetails>): FundDetails =>
  ({
    listed_on: "2004-03-02",
    offer_closed_on: "2004-03-08",
    offer_sold: "400",
    offer_raised: "40000",
    offer_buyers_count: 3,
    offer_buyers: null,
    issuance: null,
    movements: [],
    ...overrides,
  }) as FundDetails;

describe("issuanceRows", () => {
  it("a oferta encerrada vira uma linha com o preço médio e os investidores", () => {
    const [row] = issuanceRows(fund({}));

    expect(row).toMatchObject({ how: "Oferta pública", price: "100", buyers: "3 investidores", inProgress: false });
    expect(row?.day).toBe("2004-03-08");
  });

  it("a oferta aberta fica em andamento e conta no singular com um investidor", () => {
    const [row] = issuanceRows(fund({ offer_closed_on: null, offer_buyers_count: 1 }));

    expect(row).toMatchObject({ inProgress: true, buyers: "1 investidor", day: "2004-03-02" });
  });

  it("a gestora fechada não tem linhas", () => {
    expect(issuanceRows(fund({ listed_on: null }))).toEqual([]);
  });

  it("emissões fechadas e dirigidas entram dos movimentos, da mais nova para a mais antiga", () => {
    const rows = issuanceRows(
      fund({
        movements: [
          { day: "2004-06-01", type: "directed_issuance", quotas: "50", price: "120", amount: "6000", nickname: "ana" },
          { day: "2004-05-01", type: "issuance_closed", quotas: "100", price: "110", amount: "11000" },
          { day: "2004-05-01", type: "offer_closed", quotas: "400", price: "100", amount: "40000" },
        ] as FundDetails["movements"],
      }),
    );

    expect(rows.map((row) => row.how)).toEqual(["Emissão dirigida", "Emissão pública", "Oferta pública"]);
    expect(rows[0]?.buyers).toBe("ana");
  });

  it("só a emissão fechada sem cota vendida traz o motivo", () => {
    const rows = issuanceRows(
      fund({
        movements: [
          { day: "2004-06-01", type: "issuance_closed", quotas: "0", price: "110", amount: "0" },
          { day: "2004-05-01", type: "issuance_closed", quotas: "100", price: "110", amount: "11000" },
        ] as FundDetails["movements"],
      }),
    );

    expect(rows.map((row) => row.unsoldReason !== null)).toEqual([true, false, false]);
  });
});
