import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faShoppingCart } from "@fortawesome/free-solid-svg-icons";

interface FixedIncomeDetailProps {
  title: string;
  subtitle: string;
  rate: string;
  expectedReturn: string;
  basicInfo: {
    issuer: string;
    indexer: string;
    rate: string;
    maturity: string;
  };
  projections: {
    annualReturn: string;
    periodReturn: string;
    ir: string;
  };
  liquidity: {
    liquidity: string;
    fgcGuarantee: string;
    minInvestment: string;
  };
}

export default function FixedIncomeDetailPage({
  title = "CDB 110% CDI",
  subtitle = "Certificado de Depósito Bancário - Banco XYZ",
  rate = "110% CDI",
  expectedReturn = "12,81% a.a.",
  basicInfo = { issuer: "Banco XYZ", indexer: "CDI", rate: "110% CDI", maturity: "3 anos" },
  projections = { annualReturn: "12.81%", periodReturn: "+46.9%", ir: "15% (reduz)" },
  liquidity = { liquidity: "D+1", fgcGuarantee: "R$ 250.000,00", minInvestment: "R$ 1.000,00" },
}: FixedIncomeDetailProps) {
  const [investment, setInvestment] = useState<number | "">("");
  
  const expectedValue = investment ? investment * 1.4689 : 0; // Exemplo de cálculo simplificado de retorno
  const redemptionValue = expectedValue;

  return (
    <section id="fixed-income-detail" className="section-content p-4">
      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold">{title}</h2>
            <p className="text-gray-600">{subtitle}</p>
          </div>
          <div className="text-right">
            <h3 className="text-3xl font-bold text-gray-800">{rate}</h3>
            <span className="text-green-500 font-medium">Retorno esperado: {expectedReturn}</span>
          </div>
        </div>

        {/* Info Grids */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Basic Info */}
          <div className="border rounded-lg p-4 space-y-2">
            <h3 className="font-medium mb-2">Informações Básicas</h3>
            <div className="space-y-2">
              <div className="flex justify-between"><span className="text-gray-600">Emissor</span><span className="font-medium">{basicInfo.issuer}</span></div>
              <div className="flex justify-between"><span className="text-gray-600">Indexador</span><span className="font-medium">{basicInfo.indexer}</span></div>
              <div className="flex justify-between"><span className="text-gray-600">Taxa</span><span className="font-medium">{basicInfo.rate}</span></div>
              <div className="flex justify-between"><span className="text-gray-600">Vencimento</span><span className="font-medium">{basicInfo.maturity}</span></div>
            </div>
          </div>

          {/* Projections */}
          <div className="border rounded-lg p-4 space-y-2">
            <h3 className="font-medium mb-2">Projeções</h3>
            <div className="space-y-2">
              <div className="flex justify-between"><span className="text-gray-600">Retorno Anual</span><span className="font-medium">{projections.annualReturn}</span></div>
              <div className="flex justify-between"><span className="text-gray-600">Rentabilidade no período</span><span className="font-medium">{projections.periodReturn}</span></div>
              <div className="flex justify-between"><span className="text-gray-600">IR</span><span className="font-medium">{projections.ir}</span></div>
            </div>
          </div>

          {/* Liquidity */}
          <div className="border rounded-lg p-4 space-y-2">
            <h3 className="font-medium mb-2">Liquidez</h3>
            <div className="space-y-2">
              <div className="flex justify-between"><span className="text-gray-600">Liquidez</span><span className="font-medium">{liquidity.liquidity}</span></div>
              <div className="flex justify-between"><span className="text-gray-600">Garantia FGC</span><span className="font-medium">{liquidity.fgcGuarantee}</span></div>
              <div className="flex justify-between"><span className="text-gray-600">Aplicação mínima</span><span className="font-medium">{liquidity.minInvestment}</span></div>
            </div>
          </div>
        </div>

        {/* Buy Section */}
        <div className="bg-blue-50 p-6 rounded-lg">
          <h3 className="font-medium mb-4 text-lg">Investir neste ativo</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Investment Input */}
            <div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Valor do Investimento</label>
                <div className="relative">
                  <span className="absolute left-3 top-2">R$</span>
                  <input
                    type="number"
                    className="w-full pl-8 p-2 border rounded-md bg-white"
                    placeholder="0,00"
                    value={investment}
                    onChange={(e) => setInvestment(e.target.value ? parseFloat(e.target.value) : "")}
                  />
                </div>
              </div>
              <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-md flex items-center justify-center gap-2">
                <FontAwesomeIcon icon={faShoppingCart} /> Investir agora
              </button>
            </div>

            {/* Operation Summary */}
            <div className="bg-white p-4 rounded-lg space-y-2">
              <h4 className="font-medium mb-2">Resumo da Operação</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-gray-600">Valor investido</span><span className="font-medium">R$ {investment ? investment.toFixed(2) : "0,00"}</span></div>
                <div className="flex justify-between"><span className="text-gray-600">Expectativa de retorno</span><span className="font-medium">R$ {expectedValue.toFixed(2)}*</span></div>
                <div className="flex justify-between border-t pt-2"><span className="text-gray-600">Valor de resgate</span><span className="font-medium text-green-600">R$ {redemptionValue.toFixed(2)}*</span></div>
                <p className="text-xs text-gray-500 mt-2">* Valores projetados considerando taxa atual do CDI e vencimento em 3 anos</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
