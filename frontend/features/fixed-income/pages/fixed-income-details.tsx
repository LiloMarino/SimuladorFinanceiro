import { useMemo } from "react";
import { FixedIncomeAsset, TAX_TABLE } from "@/features/fixed-income/models/FixedIncomeAsset";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useParams } from "react-router-dom";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { EconomicIndicators, FixedIncomeAssetApi, SimulationState } from "@/types";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { Input } from "@/shared/components/ui/input";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/shared/components/ui/form";

import { Button } from "@/shared/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { formatDate, formatMoney, formatPercent } from "@/shared/lib/utils/formatting";
import { parse } from "date-fns";
import { useForm } from "react-hook-form";
import { investmentFormSchema, type InvestmentFormSchema } from "../schemas/investment-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { toast } from "sonner";
import { ErrorPage } from "@/pages/error";
import { LoadingPage } from "@/pages/loading";

export default function FixedIncomeDetailPage() {
  usePageLabel("Detalhes Renda Fixa");
  const { id } = useParams<{ id: string }>();
  const { data: assetData, loading: isAssetLoading } = useQueryApi<FixedIncomeAssetApi>(`/api/fixed-income/${id}`);
  const { data: rates, loading: isRatesLoading } = useQueryApi<EconomicIndicators>("/api/economic-indicators");
  const {
    data: simData,
    setData: setSimData,
    loading: isSimLoading,
  } = useQueryApi<SimulationState>("/api/get-simulation-state");
  const form = useForm<InvestmentFormSchema>({
    resolver: zodResolver(investmentFormSchema),
    defaultValues: {
      amount: "1000",
    },
  });

  useRealtime("simulation_update", (update) => {
    setSimData((prev) => ({ ...prev, ...update }));
  });

  const buyMutation = useMutationApi<{ quantity: number }>(`/api/fixed-income/${id}/buy`, {
    onSuccess: () => {
      toast.success("Investido com sucesso!");
    },
    onError: (err) => {
      toast.error(`Erro ao investir: ${err.message}`);
    },
  });

  const asset = useMemo(() => {
    if (!assetData || !simData?.currentDate || !rates) return null;
    return new FixedIncomeAsset(assetData, parse(simData.currentDate, "dd/MM/yyyy", new Date()), rates);
  }, [assetData, simData?.currentDate, rates]);

  if (isAssetLoading || isRatesLoading || isSimLoading) {
    return <LoadingPage />;
  }

  const onSubmit = async (values: InvestmentFormSchema) => {
    const quantity = Number(values.amount);

    await buyMutation.mutate({
      quantity,
    });
  };

  if (!asset) {
    return (
      <ErrorPage
        code="404"
        title="Ativo de renda fixa não encontrado"
        actionHref="/fixed-income"
        actionLabel="Voltar para a Renda Fixa"
      />
    );
  }

  const amount = form.watch("amount");
  const simulation = asset.getSimulation(Number(amount));
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
                  {asset.investmentType} - {asset.issuer}
                </p>
              </div>
              <div className="text-right">
                <h3 className="text-3xl md:text-4xl font-bold text-slate-800">{asset.rateLabel}</h3>
                <span className="text-green-600 font-medium inline-block mt-2">
                  Retorno esperado: {formatPercent(asset.grossReturn)} no período
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
                  <span className="font-medium text-slate-900">{asset.investmentType}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Tipo de Rentabilidade</span>
                  <span className="font-medium text-slate-900">{asset.indexTypeLabel}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Vencimento</span>
                  <span className="font-medium text-slate-900">{formatDate(asset.maturityDate)}</span>
                </div>
                {asset.rateIndex !== "Prefixado" && (
                  <div className="flex justify-between pt-2 border-t border-slate-100">
                    <span className="text-slate-600">Taxa {asset.rateIndex} Atual</span>
                    <span className="font-medium text-slate-900">{asset.currentRateLabel}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-slate-600">Taxa</span>
                  <span className="font-medium text-slate-900">{asset.rateLabel}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Alíquota de IR</span>
                  <span className="font-medium text-slate-900">{asset.incomeTaxLabel}</span>
                </div>
              </div>
            </div>

            {/* Rentabilidade */}
            <div className="border border-slate-200 rounded-lg p-4">
              <h3 className="font-semibold text-slate-900 mb-4">Rentabilidade</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-600">Retorno Anual Esperado (% a.a.)</span>
                  <span className="font-medium text-slate-900">{formatPercent(asset.annualRate)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Rendimento Bruto Total (%)</span>
                  <span className="font-medium text-green-700">{formatPercent(asset.grossReturn)}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-slate-600">Rendimento Líquido Total (%)</span>
                  <span className="font-medium text-green-700">{formatPercent(asset.netReturn)}</span>
                </div>

                <div className="flex justify-between pt-2 border-t border-slate-100">
                  <span className="text-slate-600">Alíquota de IR no período</span>
                  <span className="font-medium text-slate-900">{formatPercent(asset.incomeTaxRate)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Dias até vencimento</span>
                  <span className="font-medium text-slate-900">{asset.daysToMaturity} dias</span>
                </div>
              </div>
            </div>
          </div>

          {/* Investment Section */}
          <div className="p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-6">Investir neste ativo</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="amount"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Valor do investimento</FormLabel>
                        <div className="relative ">
                          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600 font-medium">
                            R$
                          </span>

                          <FormControl>
                            <Input type="number" min="0" step="100" className="pl-10" placeholder="0,00" {...field} />
                          </FormControl>
                        </div>

                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <Button
                    type="submit"
                    className="w-full bg-green-600 hover:bg-green-700 text-white py-6 text-base font-semibold rounded-lg"
                  >
                    Investir agora
                  </Button>
                </form>
              </Form>

              {/* Summary Section - Larger column spanning 2 */}
              <div className="lg:col-span-2 bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg p-6 border border-slate-200">
                <h4 className="font-semibold text-slate-900 mb-6">Resumo da Operação</h4>
                <div className="grid grid-cols-2 md:grid-cols-2 gap-6">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">
                      Valor a ser investido
                    </p>
                    <p className="text-2xl font-bold text-slate-900">{formatMoney(simulation.amount)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">
                      Rendimento Bruto
                    </p>
                    <p className="text-2xl font-bold text-green-600">{formatMoney(simulation.grossReturn)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">Imposto (IR)</p>
                    <p className="text-2xl font-bold text-red-600">{formatMoney(simulation.tax)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">
                      Valor de resgate
                    </p>
                    <p className="text-2xl font-bold text-green-700">{formatMoney(simulation.netAmount)}</p>
                  </div>
                </div>
                <p className="text-xs text-slate-500 mt-6 pt-4 border-t border-slate-300">
                  * Valores projetados considerando taxa atual e vencimento em {asset.formattedMaturity}.
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
                          {formatMoney(simulation.amount)}
                        </TableCell>
                        <TableCell className="text-right font-medium text-slate-900">{formatPercent(1)}</TableCell>
                      </TableRow>
                      <TableRow className="border-b border-slate-200">
                        <TableCell className="text-slate-700 font-medium">Resultado Bruto (R$)</TableCell>
                        <TableCell className="text-right font-bold text-green-700">
                          {formatMoney(simulation.grossAmount)}
                        </TableCell>
                        <TableCell className="text-right font-bold text-green-700">
                          {formatPercent(simulation.grossReturnPct)}
                        </TableCell>
                      </TableRow>
                      <TableRow className="border-b border-slate-200">
                        <TableCell className="text-slate-700 font-medium">Rendimento Bruto (R$)</TableCell>
                        <TableCell className="text-right font-medium text-slate-900">
                          {formatMoney(simulation.grossReturn)}
                        </TableCell>
                        <TableCell className="text-right font-medium text-slate-900">
                          {formatPercent(simulation.grossReturnPct)}
                        </TableCell>
                      </TableRow>
                      <TableRow className="border-b border-slate-200">
                        <TableCell className="text-slate-700 font-medium">Imposto sobre Rendimento (R$)</TableCell>
                        <TableCell className="text-right font-bold text-red-600">
                          - {formatMoney(simulation.tax)}
                        </TableCell>
                        <TableCell className="text-right font-bold text-red-600">
                          {formatPercent(simulation.taxPct)}
                        </TableCell>
                      </TableRow>
                      <TableRow className="border-b border-slate-200">
                        <TableCell className="text-slate-700 font-medium">Resultado Líquido (R$)</TableCell>
                        <TableCell className="text-right font-bold text-green-600">
                          {formatMoney(simulation.netAmount)}
                        </TableCell>
                        <TableCell className="text-right font-bold text-green-600">
                          {formatPercent(simulation.netReturnPct)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell className="text-slate-700 font-medium">Rendimento Líquido (R$)</TableCell>
                        <TableCell className="text-right font-medium text-slate-900">
                          {formatMoney(simulation.netReturn)}
                        </TableCell>
                        <TableCell className="text-right font-medium text-slate-900">
                          {formatPercent(simulation.netReturnPct)}
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </div>
              </div>

              {/* Tax Table Section - 1 column */}
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
                        const isActive = asset.incomeTaxRate === row.rate;

                        return (
                          <TableRow
                            key={idx}
                            className={isActive ? "bg-green-50 border-b border-slate-200" : "border-b border-slate-200"}
                          >
                            <TableCell className="text-slate-700 font-medium">{row.label}</TableCell>

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
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
