import { describe, expect, it } from "vitest";
import type { FundDetails } from "@/types";
import { fundYield } from "./fund-yield";

const row = (paidOn: string | null, perQuota: string | null): FundDetails["distributions"][number] =>
  ({ data_com: "2004-01-30", paid_on: paidOn, paid_per_quota: perQuota }) as FundDetails["distributions"][number];

describe("fundYield", () => {
  it("soma o que a cota pagou e divide pelo preço de mercado", () => {
    const result = fundYield({
      distributions: [row("2004-03-02", "8.00"), row("2004-02-02", "8.77"), row(null, null)],
      price: "106.02",
      nav: "100.00",
    });

    expect(result.perQuota).toBeCloseTo(16.77);
    expect(result.rate).toBeCloseTo(16.77 / 106.02);
    expect(result.lastPerQuota).toBe(8);
    expect(result.lastPaidOn).toBe("2004-03-02");
  });

  it("sem negócio no mercado usa o patrimônio por cota", () => {
    const result = fundYield({ distributions: [row("2004-03-02", "5.00")], price: null, nav: "100.00" });

    expect(result.base).toBe(100);
    expect(result.rate).toBeCloseTo(0.05);
  });

  it("sem rendimento pago não há yield", () => {
    const result = fundYield({ distributions: [row(null, null)], price: "100.00", nav: "100.00" });

    expect(result.rate).toBeNull();
    expect(result.lastPaidOn).toBeNull();
  });

  it("conta só os 12 pagamentos mais novos", () => {
    const rows = Array.from({ length: 14 }, (_, index) =>
      row(`2003-${String((index % 12) + 1).padStart(2, "0")}-02`, "1.00"),
    );
    rows[0] = row("2004-05-02", "1.00");
    rows[1] = row("2004-04-02", "1.00");

    expect(fundYield({ distributions: rows, price: "100.00", nav: "100.00" }).perQuota).toBe(12);
  });
});
