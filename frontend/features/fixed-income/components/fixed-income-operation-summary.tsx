import { displayMoney } from "@/shared/lib/utils/display";
import { FixedIncomeAsset } from "../models/FixedIncomeAsset";

interface FixedIncomeOperationSummaryProps {
  asset: FixedIncomeAsset;
  simulation: ReturnType<FixedIncomeAsset["getSimulation"]>;
}

export function FixedIncomeOperationSummary({ asset, simulation }: FixedIncomeOperationSummaryProps) {
  return (
    <div className="lg:col-span-2 bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg p-6 border border-slate-200">
      <h4 className="font-semibold text-slate-900 mb-6">Resumo da Operação</h4>
      <div className="grid grid-cols-2 md:grid-cols-2 gap-6">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">Valor a ser investido</p>
          <p className="text-2xl font-bold text-slate-900">{displayMoney(simulation.amount)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">Rendimento Bruto</p>
          <p className="text-2xl font-bold text-green-600">{displayMoney(simulation.grossReturn)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">Imposto (IR)</p>
          <p className="text-2xl font-bold text-red-600">{displayMoney(simulation.tax)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-600 font-semibold mb-1">Valor de resgate</p>
          <p className="text-2xl font-bold text-green-700">{displayMoney(simulation.netAmount)}</p>
        </div>
      </div>
      <p className="text-xs text-slate-500 mt-6 pt-4 border-t border-slate-300">
        * Valores projetados considerando taxa atual e vencimento em {asset.formattedMaturity}.
      </p>
    </div>
  );
}
