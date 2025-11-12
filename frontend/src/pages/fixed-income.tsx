import FixedIncomeCard from "@/components/cards/fixed-income-card";
import type { FixedIncomeAsset } from "@/types";

export default function FixedIncomePage() {
  const assets: FixedIncomeAsset[] = [
    {
      name: "LCI Imobiliária XP",
      issuer: "Banco XP",
      interestRate: 0.94,
      rateIndex: "CDI",
      investmentType: "LCI",
      maturityDate: "2026-11-01",
      incomeTax: "Isento",
      daysToMaturity: 720,
    },
    {
      name: "LCA Agro BTG",
      issuer: "Banco BTG Pactual",
      interestRate: 0.92,
      rateIndex: "CDI",
      investmentType: "LCA",
      maturityDate: "2027-11-01",
      incomeTax: "Isento",
      daysToMaturity: 1080,
    },
    {
      name: "CDB Prefixado Inter",
      issuer: "Banco Inter",
      interestRate: 11.5,
      rateIndex: "PREFIXADO",
      investmentType: "CDB",
      maturityDate: "2027-11-01",
      incomeTax: "15%",
      daysToMaturity: 1080,
    },
    {
      name: "Tesouro IPCA+ 2035",
      issuer: "Tesouro Nacional",
      interestRate: 5.8,
      rateIndex: "IPCA",
      investmentType: "TESOURO",
      maturityDate: "2035-05-15",
      incomeTax: "15% (reduz)",
      daysToMaturity: 3450,
    },
    {
      name: "Tesouro Selic 2029",
      issuer: "Tesouro Nacional",
      interestRate: 0.1,
      rateIndex: "SELIC",
      investmentType: "TESOURO",
      maturityDate: "2029-03-01",
      incomeTax: "15% (reduz)",
      daysToMaturity: 1580,
    },
    {
      name: "CDB Pós CDI Nubank",
      issuer: "NuFinanceira",
      interestRate: 1.1,
      rateIndex: "CDI",
      investmentType: "CDB",
      maturityDate: "2028-06-01",
      incomeTax: "15%",
      daysToMaturity: 930,
    },
  ];

  return (
    <section className="p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {assets.map((asset) => (
          <FixedIncomeCard key={asset.name} asset={asset} />
        ))}
      </div>
    </section>
  );
}
