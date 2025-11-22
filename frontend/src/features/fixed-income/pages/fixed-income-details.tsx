import { useMemo, useState } from "react";
import { FixedIncomeAsset } from "@/features/fixed-income/models/fixed-income-asset";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { Spinner } from "@/shared/components/ui/spinner";
import { useParams } from "react-router-dom";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { EconomicIndicators, FixedIncomeAssetApi, SimulationState } from "@/types";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Button } from "@/shared/components/ui/button";
import { Table } from "lucide-react";
import { TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";

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
      <div className="mx-auto max-w-6xl">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Header Section */}
          <div className="border-b border-slate-200 p-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
              <div>
                <h2 className="text-2xl md:text-3xl font-bold text-slate-900">{asset.name}</h2>
                <p className="text-slate-600 mt-1">
                  {getInvestmentTypeLabel(asset.investment_type)} - {asset.issuer}
                </p>
              </div>
              <div className="text-right">
                <h3 className="text-3xl md:text-4xl font-bold text-slate-800">
                  {getRateLabel(asset.rate_index, asset.interest_rate)}
                </h3>
                <span className="text-green-600 font-medium inline-block mt-2">
                  Retorno esperado: {calculations.grossReturnPct.toFixed(2)}% no período
                </span>
              </div>
            </div>
          </div>

          {/* Basic Info Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 border-b border-slate-200">
            {/* Informações Gerais */}
            <div className="border border-slate-200 rounded-lg p-4">
              <h3 className="font-semibold text-slate-900 mb-4">Informações Gerais</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-600">Tipo de Investimento</span>
                  <span className="font-medium text-slate-900">{getInvestmentTypeLabel(asset.investment_type)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Tipo de Rentabilidade</span>
                  <span className="font-medium text-slate-900">{getReturnType(asset.rate_index)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Vencimento</span>
                  <span className="font-medium text-slate-900">{formattedMaturity}</span>
                </div>
                <div className="flex justify-between pt-2 border-t border-slate-100">
                  <span className="text-slate-600">Taxa {asset.rate_index} Atual</span>
                  <span className="font-medium text-slate-900">
                    {asset.rate_index === "CDI"
                      ? `${(rates.CDI * 100).toFixed(2)}% a.a.`
                      : asset.rate_index === "IPCA"
                      ? `${(rates.IPCA * 100).toFixed(2)}% a.a.`
                      : `${(rates.SELIC * 100).toFixed(2)}% a.a.`}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Taxa</span>
                  <span className="font-medium text-slate-900">
                    {getRateLabel(asset.rate_index, asset.interest_rate)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Alíquota de IR</span>
                  <span className="font-medium text-slate-900">{getTaxInfo(asset.investment_type)}</span>
                </div>
              </div>
            </div>

            {/* Rentabilidade */}
            <div className="border border-slate-200 rounded-lg p-4">
              <h3 className="font-semibold text-slate-900 mb-4">Rentabilidade</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-600">Retorno Anual Esperado (% a.a.)</span>
                  <span className="font-medium text-slate-900">
                    {asset.rate_index === "CDI"
                      ? `${(rates.CDI * asset.interest_rate * 100).toFixed(2)}%`
                      : asset.rate_index === "IPCA"
                      ? `${((rates.IPCA + asset.interest_rate) * 100).toFixed(2)}%`
                      : `${((rates.SELIC + asset.interest_rate) * 100).toFixed(2)}%`}
                  </span>
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
                  <span className="font-medium text-slate-900">{daysToMaturity} dias</span>
                </div>
              </div>
            </div>
          </div>

          {/* Investment Section */}
          <div className="p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-6">Investir neste ativo</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
              {/* Input Section - Smaller column */}
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
                    placeholder="0,00"
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

              {/* Summary Section - Larger column spanning 2 */}
              <div className="lg:col-span-2 bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg p-6 border border-slate-200">
                <h4 className="font-semibold text-slate-900 mb-6">Resumo da Operação</h4>
                <div className="grid grid-cols-2 md:grid-cols-2 gap-6">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">Valor investido</p>
                    <p className="text-2xl font-bold text-slate-900">R$ {Number(investmentAmount || 0).toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">
                      Rendimento Bruto
                    </p>
                    <p className="text-2xl font-bold text-green-600">R$ {calculations.grossReturn.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">Imposto (IR)</p>
                    <p className="text-2xl font-bold text-red-600">- R$ {calculations.tax.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">
                      Valor de resgate
                    </p>
                    <p className="text-2xl font-bold text-green-700">R$ {calculations.netAmount.toFixed(2)}</p>
                  </div>
                </div>
                <p className="text-xs text-slate-500 mt-6 pt-4 border-t border-slate-300">
                  * Valores projetados considerando taxa atual e vencimento em {formattedMaturity}
                </p>
              </div>
            </div>

            {/* Detalhamento Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
              {/* Detalhamento Section - 2 columns */}
              <div className="lg:col-span-2">
                <h4 className="font-semibold text-slate-900 mb-4">Detalhamento dos Cálculos</h4>
                <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-slate-100 hover:bg-slate-100">
                        <TableHead className="text-slate-900 font-semibold">Descrição</TableHead>
                        <TableHead className="text-right text-slate-900 font-semibold">Valor</TableHead>
                        <TableHead className="text-right text-slate-900 font-semibold">Percentual</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow className="border-b border-slate-200">
                        <TableCell className="text-slate-700 font-medium">Valor Aplicado</TableCell>
                        <TableCell className="text-right font-medium text-slate-900">
                          R$ {calculations.amount.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right font-medium text-slate-900">100,00%</TableCell>
                      </TableRow>
                      <TableRow className="border-b border-slate-200">
                        <TableCell className="text-slate-700 font-medium">Resultado Bruto (R$)</TableCell>
                        <TableCell className="text-right font-bold text-green-700">
                          R$ {calculations.grossAmount.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right font-bold text-green-700">
                          {calculations.grossReturnPct.toFixed(2)}%
                        </TableCell>
                      </TableRow>
                      <TableRow className="border-b border-slate-200">
                        <TableCell className="text-slate-700">Rendimento Bruto (R$)</TableCell>
                        <TableCell className="text-right font-medium text-slate-900">
                          R$ {calculations.grossReturn.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right font-medium text-slate-900">
                          {calculations.grossReturnPct.toFixed(2)}%
                        </TableCell>
                      </TableRow>
                      <TableRow className="border-b border-slate-200">
                        <TableCell className="text-slate-700 font-medium">Imposto sobre Rendimento (R$)</TableCell>
                        <TableCell className="text-right font-bold text-red-600">
                          - R$ {calculations.tax.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right font-bold text-red-600">
                          {calculations.taxRate > 0 ? `${(calculations.taxRate * 100).toFixed(1)}%` : "0%"}
                        </TableCell>
                      </TableRow>
                      <TableRow className="border-b border-slate-200">
                        <TableCell className="text-slate-700 font-medium">Resultado Líquido (R$)</TableCell>
                        <TableCell className="text-right font-bold text-green-600">
                          R$ {calculations.netAmount.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right font-bold text-green-600">
                          {((calculations.netAmount / calculations.amount) * 100).toFixed(2)}%
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell className="text-slate-700 font-medium">Rendimento Líquido (R$)</TableCell>
                        <TableCell className="text-right font-medium text-slate-900">
                          R$ {calculations.netReturn.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right font-medium text-slate-900">
                          {calculations.netReturnPct.toFixed(2)}%
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </div>
              </div>

              {/* Tax Table Section - 1 column */}
              {asset.investment_type !== "LCI" && asset.investment_type !== "LCA" && (
                <div className="lg:col-span-1">
                  <h4 className="font-semibold text-slate-900 mb-4">Tabela Regressiva de IR</h4>
                  <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                    <Table className="text-sm">
                      <TableHeader>
                        <TableRow className="bg-slate-100 hover:bg-slate-100">
                          <TableHead className="text-slate-900 font-semibold">Prazo (dias)</TableHead>
                          <TableHead className="text-right text-slate-900 font-semibold">Alíquota</TableHead>
                          <TableHead className="text-center text-slate-900 font-semibold">Status</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {TAX_TABLE.map((row, idx) => {
                          const isActive = daysToMaturity >= row.days;
                          return (
                            <TableRow
                              key={idx}
                              className={
                                isActive ? "bg-green-50 border-b border-slate-200" : "border-b border-slate-200"
                              }
                            >
                              <TableCell className="text-slate-700 font-medium">
                                {row.days === 0 ? "Até 180" : `Acima de ${row.days}`}
                              </TableCell>
                              <TableCell className="text-right font-semibold text-slate-900">
                                {(row.rate * 100).toFixed(1)}%
                              </TableCell>
                              <TableCell className="text-center">
                                {isActive ? (
                                  <span className="inline-block px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded">
                                    Aplicável
                                  </span>
                                ) : (
                                  <span className="inline-block px-2 py-1 bg-slate-100 text-slate-600 text-xs font-semibold rounded">
                                    -
                                  </span>
                                )}
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
