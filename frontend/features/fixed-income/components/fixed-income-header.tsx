import { displayPercent } from "@/shared/lib/utils/display";
import { FixedIncomeAsset } from "../models/FixedIncomeAsset";

interface FixedIncomeHeaderProps {
  asset: FixedIncomeAsset;
}

export function FixedIncomeHeader({ asset }: FixedIncomeHeaderProps) {
  return (
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
            Retorno esperado: {displayPercent(asset.grossReturn)} no período
          </span>
        </div>
      </div>
    </div>
  );
}
