import { useMemo, useState } from "react";
import { FixedIncomeAsset } from "@/models/fixed-income-asset";
import { useQueryApi } from "@/hooks/useQueryApi";
import { Spinner } from "@/components/ui/spinner";
import { useParams } from "react-router-dom";
import { useRealtime } from "@/hooks/useRealtime";
import type { EconomicIndicators, FixedIncomeAssetApi, SimulationState } from "@/types";
import usePageLabel from "@/hooks/usePageLabel";

export default function FixedIncomeDetailPage() {
  usePageLabel("Detalhes Renda Fixa");
  const { id } = useParams<{ id: string }>();
  const { data: assetData, loading: isAssetLoading } = useQueryApi<FixedIncomeAssetApi>(`/api/fixed-income/${id}`);
  const {
    data: simData,
    setData: setSimData,
    loading: isSimLoading,
  } = useQueryApi<SimulationState>("/api/get-simulation-state");
  const { data: rates, loading: isRatesLoading } = useQueryApi<EconomicIndicators>("/api/economic-indicators");
  const [investmentAmount, setInvestmentAmount] = useState<string>("1000");

  useRealtime("simulation_update", (update) => {
    setSimData((prev) => ({ ...prev, ...update }));
  });

  const asset = useMemo(() => {
    if (!assetData || !simData?.currentDate) return null;
    return new FixedIncomeAsset(assetData, new Date(simData.currentDate));
  }, [assetData, simData?.currentDate]);

  const calculations = useMemo(() => {
    if (!asset) return null;
    const amount = Number.parseFloat(investmentAmount) || 0;
    return asset.calculateInvestment(amount);
  }, [asset, investmentAmount]);

  if (isAssetLoading || isRatesLoading || isSimLoading) {
    return (
      <section className="flex min-h-[80vh] items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </section>
    );
  }

  if (!assetData) {
    return <div className="p-6 text-center text-gray-500">Ativo não encontrado.</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="mx-auto max-w-6xl bg-white rounded-lg shadow-md overflow-hidden">
        {/* Header Section */}
        <div className="border-b border-slate-200 p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <h2 className="text-3xl font-bold text-slate-900">{asset.name}</h2>
            <p className="text-slate-600 mt-1">
              {asset.investmentTypeLabel} - {asset.issuer}
            </p>
          </div>
          <div className="text-right">
            <h3 className="text-4xl font-bold text-slate-800">{asset.rateLabel}</h3>
            <span className="text-green-600 font-medium inline-block mt-2">
              Retorno esperado: {calculations.grossReturnPct.toFixed(2)}% no período
            </span>
          </div>
        </div>

        {/* Basic Info Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 border-b border-slate-200">
          <div className="border border-slate-200 rounded-lg p-4">
            <h3 className="font-semibold text-slate-900 mb-4">Informações Gerais</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600">Tipo de Investimento</span>
                <span className="font-medium text-slate-900">{asset.investmentTypeLabel}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Tipo de Rentabilidade</span>
                <span className="font-medium text-slate-900">{asset.returnType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Vencimento</span>
                <span className="font-medium text-slate-900">{asset.formattedMaturity}</span>
              </div>
              <div className="flex justify-between pt-2 border-t border-slate-100">
                <span className="text-slate-600">Taxa {asset.rateIndex} Atual</span>
                <span className="font-medium text-slate-900">{asset.currentRateLabel}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Taxa</span>
                <span className="font-medium text-slate-900">{asset.rateLabel}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Alíquota de IR</span>
                <span className="font-medium text-slate-900">{asset.incomeTax}</span>
              </div>
            </div>
          </div>

          <div className="border border-slate-200 rounded-lg p-4">
            <h3 className="font-semibold text-slate-900 mb-4">Rentabilidade</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600">Retorno Anual Esperado (% a.a.)</span>
                <span className="font-medium text-slate-900">{asset.annualRateLabel}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Rendimento Bruto Total (%)</span>
                <span className="font-medium text-green-700">{calculations.grossReturnPct.toFixed(2)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Rendimento Líquido Total (%)</span>
                <span className="font-medium text-green-700">{calculations.netReturnPct.toFixed(2)}%</span>
              </div>
              <div className="flex justify-between pt-2 border-t border-slate-100">
                <span className="text-slate-600">Alíquota de IR no período</span>
                <span className="font-medium text-slate-900">
                  {calculations.taxRate > 0 ? `${(calculations.taxRate * 100).toFixed(1)}%` : "Isento"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Dias até vencimento</span>
                <span className="font-medium text-slate-900">{asset.daysToMaturity} dias</span>
              </div>
            </div>
          </div>
        </div>

        {/* Invest Section */}
        <div className="p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-6">Investir neste ativo</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div className="lg:col-span-1">
              <Label htmlFor="investment-value" className="block text-sm font-medium text-slate-700 mb-2">
                Valor do Investimento
              </Label>
              <div className="relative mb-6">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-600 font-medium">
                  R$
                </span>
                <Input
                  id="investment-value"
                  type="number"
                  value={investmentAmount}
                  onChange={(e) => setInvestmentAmount(e.target.value)}
                  className="pl-10"
                  min="0"
                  step="100"
                />
              </div>
              <Button className="w-full bg-green-600 hover:bg-green-700 text-white py-6 text-base font-semibold rounded-lg">
                Investir agora
              </Button>
            </div>

            <div className="lg:col-span-2 bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg p-6 border border-slate-200">
              <h4 className="font-semibold text-slate-900 mb-6">Resumo da Operação</h4>
              <div className="grid grid-cols-2 md:grid-cols-2 gap-6">
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">Valor investido</p>
                  <p className="text-2xl font-bold text-slate-900">R$ {Number(investmentAmount || 0).toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">Rendimento Bruto</p>
                  <p className="text-2xl font-bold text-green-600">R$ {calculations.grossReturn.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">Imposto (IR)</p>
                  <p className="text-2xl font-bold text-red-600">- R$ {calculations.tax.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">Valor de resgate</p>
                  <p className="text-2xl font-bold text-green-700">R$ {calculations.netAmount.toFixed(2)}</p>
                </div>
              </div>
              <p className="text-xs text-slate-500 mt-6 pt-4 border-t border-slate-300">
                * Valores projetados considerando taxa atual e vencimento em {asset.formattedMaturity}
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
