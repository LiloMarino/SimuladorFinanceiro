import { displayDate, displayPercent } from "@/shared/lib/utils/display";
import { FixedIncomeAsset } from "../models/FixedIncomeAsset";
import type { FixedIncomeProjection } from "@/types";

interface FixedIncomeBasicInfoGridProps {
  asset: FixedIncomeAsset;
  projection: FixedIncomeProjection;
}

export function FixedIncomeBasicInfoGrid({ asset, projection }: FixedIncomeBasicInfoGridProps) {
  return (
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
            <span className="font-medium text-slate-900">{displayDate(asset.maturityDate)}</span>
          </div>
          {asset.rateIndex !== "Prefixado" && (
            <div className="flex justify-between pt-2 border-t border-slate-100">
              <span className="text-slate-600">Taxa {asset.rateIndex} Atual</span>
              <span className="font-medium text-slate-900">{displayPercent(projection.index_rate)} a.a.</span>
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
            <span className="font-medium text-slate-900">{displayPercent(projection.effective_annual_rate)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-600">Rendimento Bruto Total (%)</span>
            <span className="font-medium text-success">{displayPercent(projection.gross_return_pct)}</span>
          </div>

          <div className="flex justify-between">
            <span className="text-slate-600">Rendimento Líquido Total (%)</span>
            <span className="font-medium text-success">{displayPercent(projection.net_return_pct)}</span>
          </div>

          <div className="flex justify-between pt-2 border-t border-slate-100">
            <span className="text-slate-600">Alíquota de IR no período</span>
            <span className="font-medium text-slate-900">{displayPercent(projection.income_tax_rate)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-600">Dias até vencimento</span>
            <span className="font-medium text-slate-900">{asset.daysToMaturity} dias</span>
          </div>
        </div>
      </div>
    </div>
  );
}
