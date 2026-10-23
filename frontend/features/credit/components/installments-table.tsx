import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayNumber, displayShortDate } from "@/shared/lib/utils/display";
import type { LoanQuote } from "@/types";

type InstallmentsTableProps = { schedule: LoanQuote["schedule"] };

/** Cronograma da Tabela Price: o juro cai e a dívida paga sobe a cada parcela. */
export function InstallmentsTable({ schedule }: InstallmentsTableProps) {
  return (
    <div className="max-h-60 overflow-auto rounded-[10px] border">
      <Table>
        <TableHeader className="sticky top-0">
          <TableRow>
            <TableHead>Parcela</TableHead>
            <TableHead numeric>Juro</TableHead>
            <TableHead numeric>Dívida paga</TableHead>
            <TableHead numeric>Saldo</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {schedule.map((row) => (
            <TableRow key={row.number}>
              <TableCell>
                <span className="font-mono">
                  {row.number} · {displayShortDate(row.due_date)}
                </span>
              </TableCell>
              <TableCell numeric>{displayNumber(row.interest)}</TableCell>
              <TableCell numeric>{displayNumber(row.principal)}</TableCell>
              <TableCell numeric>{displayNumber(row.balance)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
