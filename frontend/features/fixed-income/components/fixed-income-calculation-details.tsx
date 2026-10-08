import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import type { FixedIncomeProjection } from "@/types";

interface FixedIncomeCalculationDetailsProps {
  projection: FixedIncomeProjection;
}

export function FixedIncomeCalculationDetails({ projection }: FixedIncomeCalculationDetailsProps) {
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
              <TableCell className="text-right font-medium text-slate-900">{displayMoney(projection.amount)}</TableCell>
              <TableCell className="text-right font-medium text-slate-900">{displayPercent("1")}</TableCell>
            </TableRow>
            <TableRow className="border-b border-slate-200">
              <TableCell className="text-slate-700 font-medium">Resultado Bruto (R$)</TableCell>
              <TableCell className="text-right font-bold text-green-700">
                {displayMoney(projection.gross_amount)}
              </TableCell>
              <TableCell className="text-right font-bold text-green-700">
                {displayPercent(projection.gross_return_pct)}
              </TableCell>
            </TableRow>
            <TableRow className="border-b border-slate-200">
              <TableCell className="text-slate-700 font-medium">Rendimento Bruto (R$)</TableCell>
              <TableCell className="text-right font-medium text-slate-900">
                {displayMoney(projection.gross_return)}
              </TableCell>
              <TableCell className="text-right font-medium text-slate-900">
                {displayPercent(projection.gross_return_pct)}
              </TableCell>
            </TableRow>
            <TableRow className="border-b border-slate-200">
              <TableCell className="text-slate-700 font-medium">Imposto sobre Rendimento (R$)</TableCell>
              <TableCell className="text-right font-bold text-red-600">- {displayMoney(projection.income_tax)}</TableCell>
              <TableCell className="text-right font-bold text-red-600">{displayPercent(projection.income_tax_pct)}</TableCell>
            </TableRow>
            <TableRow className="border-b border-slate-200">
              <TableCell className="text-slate-700 font-medium">Resultado Líquido (R$)</TableCell>
              <TableCell className="text-right font-bold text-green-600">
                {displayMoney(projection.net_amount)}
              </TableCell>
              <TableCell className="text-right font-bold text-green-600">
                {displayPercent(projection.net_return_pct)}
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="text-slate-700 font-medium">Rendimento Líquido (R$)</TableCell>
              <TableCell className="text-right font-medium text-slate-900">
                {displayMoney(projection.net_return)}
              </TableCell>
              <TableCell className="text-right font-medium text-slate-900">
                {displayPercent(projection.net_return_pct)}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
