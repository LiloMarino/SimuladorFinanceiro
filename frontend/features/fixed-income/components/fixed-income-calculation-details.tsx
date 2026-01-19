import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { FixedIncomeAsset } from "../models/FixedIncomeAsset";

interface FixedIncomeCalculationDetailsProps {
  simulation: ReturnType<FixedIncomeAsset["getSimulation"]>;
}

export function FixedIncomeCalculationDetails({ simulation }: FixedIncomeCalculationDetailsProps) {
  return (
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
              <TableCell className="text-right font-medium text-slate-900">{displayMoney(simulation.amount)}</TableCell>
              <TableCell className="text-right font-medium text-slate-900">{displayPercent(1)}</TableCell>
            </TableRow>
            <TableRow className="border-b border-slate-200">
              <TableCell className="text-slate-700 font-medium">Resultado Bruto (R$)</TableCell>
              <TableCell className="text-right font-bold text-green-700">
                {displayMoney(simulation.grossAmount)}
              </TableCell>
              <TableCell className="text-right font-bold text-green-700">
                {displayPercent(simulation.grossReturnPct)}
              </TableCell>
            </TableRow>
            <TableRow className="border-b border-slate-200">
              <TableCell className="text-slate-700 font-medium">Rendimento Bruto (R$)</TableCell>
              <TableCell className="text-right font-medium text-slate-900">
                {displayMoney(simulation.grossReturn)}
              </TableCell>
              <TableCell className="text-right font-medium text-slate-900">
                {displayPercent(simulation.grossReturnPct)}
              </TableCell>
            </TableRow>
            <TableRow className="border-b border-slate-200">
              <TableCell className="text-slate-700 font-medium">Imposto sobre Rendimento (R$)</TableCell>
              <TableCell className="text-right font-bold text-red-600">- {displayMoney(simulation.tax)}</TableCell>
              <TableCell className="text-right font-bold text-red-600">{displayPercent(simulation.taxPct)}</TableCell>
            </TableRow>
            <TableRow className="border-b border-slate-200">
              <TableCell className="text-slate-700 font-medium">Resultado Líquido (R$)</TableCell>
              <TableCell className="text-right font-bold text-green-600">
                {displayMoney(simulation.netAmount)}
              </TableCell>
              <TableCell className="text-right font-bold text-green-600">
                {displayPercent(simulation.netReturnPct)}
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="text-slate-700 font-medium">Rendimento Líquido (R$)</TableCell>
              <TableCell className="text-right font-medium text-slate-900">
                {displayMoney(simulation.netReturn)}
              </TableCell>
              <TableCell className="text-right font-medium text-slate-900">
                {displayPercent(simulation.netReturnPct)}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
