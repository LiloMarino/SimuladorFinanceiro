import { displayPercent } from "@/shared/lib/utils/display";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { TAX_TABLE, FixedIncomeAsset } from "../models/FixedIncomeAsset";

interface FixedIncomeTaxTableProps {
  asset: FixedIncomeAsset;
}

export function FixedIncomeTaxTable({ asset }: FixedIncomeTaxTableProps) {
  return (
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

                  <TableCell className="text-right font-semibold text-slate-900">{displayPercent(row.rate)}</TableCell>

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
  );
}
