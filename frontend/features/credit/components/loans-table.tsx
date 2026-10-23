import { Button } from "@/shared/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import {
  displayDayMonth,
  displayMoney,
  displayPercent,
  displayShortDate,
} from "@/shared/lib/utils/display";
import type { CreditLoan } from "@/types";
import type { PrepayChoice } from "./prepay-dialog";

type LoansTableProps = {
  loans: CreditLoan[];
  onPrepay: (loan: CreditLoan, choice: PrepayChoice) => void;
  onPayOverdue: (loan: CreditLoan) => void;
};

const sum = (values: string[]) => values.reduce((total, value) => total + Number(value), 0);

/** "Seus empréstimos": uma linha por contrato, com o total das parcelas e da dívida no fim. */
export function LoansTable({ loans, onPrepay, onPayOverdue }: LoansTableProps) {
  const { data: state } = useSimulationState();
  const todayYear = state?.current_date?.slice(0, 4);
  const charges = sum(loans.map((loan) => loan.overdue_charges));

  // O ano só aparece quando a data cai fora do ano da partida
  const dueDate = (isoDate: string) =>
    isoDate.slice(0, 4) === todayYear ? displayDayMonth(isoDate) : displayShortDate(isoDate);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Seus empréstimos</CardTitle>
        <CardDescription>
          Parcelas fixas, debitadas do caixa na data. Pagar antes abate os juros que faltam.
        </CardDescription>
      </CardHeader>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Empréstimo</TableHead>
            <TableHead>Contratado</TableHead>
            <TableHead numeric>Juro travado</TableHead>
            <TableHead numeric>Parcela</TableHead>
            <TableHead numeric>Pagas</TableHead>
            <TableHead numeric>Saldo devedor</TableHead>
            <TableHead>Próxima</TableHead>
            <TableHead>
              <span className="sr-only">Ações</span>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {loans.map((loan) => {
            const late = loan.overdue.length > 0;
            return (
              <TableRow key={loan.id} variant={late ? "warning" : "default"}>
                <TableCell>
                  <div className="grid">
                    <b className="font-semibold">Empréstimo {loan.number}</b>
                    <span className="text-xs text-muted-foreground">
                      {displayMoney(loan.principal)} em {loan.term_months} parcelas
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <span className="font-mono text-muted-foreground">{displayShortDate(loan.contract_date)}</span>
                </TableCell>
                <TableCell numeric>
                  {displayPercent(loan.annual_rate)}{" "}
                  <span className="font-sans text-muted-foreground">· {loan.grade}</span>
                </TableCell>
                <TableCell numeric>{displayMoney(loan.installment)}</TableCell>
                <TableCell numeric>
                  {loan.paid_installments} de {loan.total_installments}
                </TableCell>
                <TableCell numeric>{displayMoney(loan.balance)}</TableCell>
                <TableCell>
                  {late ? (
                    <span className="font-semibold text-destructive">
                      {displayDayMonth(loan.overdue[0].due_date)} · {loan.overdue[0].days_late}{" "}
                      {loan.overdue[0].days_late === 1 ? "dia" : "dias"}
                    </span>
                  ) : loan.next_due ? (
                    dueDate(loan.next_due)
                  ) : (
                    "—"
                  )}
                </TableCell>
                <TableCell>
                  <span className="flex justify-end gap-1.5">
                    {late ? (
                      <Button variant="destructive" size="sm" onClick={() => onPayOverdue(loan)}>
                        Pagar {displayMoney(sum(loan.overdue.map((item) => item.total)))}
                      </Button>
                    ) : (
                      <>
                        <Button variant="outline" size="xs" onClick={() => onPrepay(loan, "part")}>
                          Amortizar
                        </Button>
                        <Button variant="outline" size="xs" onClick={() => onPrepay(loan, "all")}>
                          Quitar
                        </Button>
                      </>
                    )}
                  </span>
                </TableCell>
              </TableRow>
            );
          })}

          {/* Total */}
          <TableRow variant="group">
            <TableCell colSpan={3}>
              <b className="font-semibold">Total</b>{" "}
              <span className="text-muted-foreground">· parcelas por mês e dívida de hoje</span>
            </TableCell>
            <TableCell numeric>
              <b className="font-semibold">{displayMoney(sum(loans.map((loan) => loan.installment)))}</b>
            </TableCell>
            <TableCell />
            <TableCell numeric>
              <b className="font-semibold">{displayMoney(sum(loans.map((loan) => loan.balance)))}</b>
              {charges > 0 && (
                <div className="font-sans text-xs font-normal text-destructive">
                  + {displayMoney(charges)} de multa e mora
                </div>
              )}
            </TableCell>
            <TableCell colSpan={2} />
          </TableRow>
        </TableBody>
      </Table>
    </Card>
  );
}
