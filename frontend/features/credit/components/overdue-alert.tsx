import { TriangleAlert } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { displayDayMonth, displayMoney } from "@/shared/lib/utils/display";
import type { CreditLoan } from "@/types";

type OverdueAlertProps = {
  loans: CreditLoan[];
  onPay: (loan: CreditLoan) => void;
};

const sum = (values: string[]) => values.reduce((total, value) => total + Number(value), 0);

const pluralDays = (count: number) => `${count} ${count === 1 ? "dia" : "dias"}`;

/** Aviso do topo: a parcela atrasada mais antiga, o que o atraso já custou e o botão para pagar. */
export function OverdueAlert({ loans, onPay }: OverdueAlertProps) {
  const late = loans
    .filter((loan) => loan.overdue.length > 0)
    .map((loan) => ({ loan, oldest: loan.overdue[0] }))
    .sort((a, b) => (a.oldest?.due_date ?? "").localeCompare(b.oldest?.due_date ?? ""));
  const first = late[0];
  if (!first?.oldest) return null;

  const { loan, oldest } = first;
  const count = late.reduce((total, item) => total + item.loan.overdue.length, 0);
  const cost = late.reduce(
    (total, item) =>
      total + sum(item.loan.overdue.map((row) => row.fee)) + sum(item.loan.overdue.map((row) => row.interest)),
    0,
  );

  return (
    <Alert variant="destructive">
      <TriangleAlert />
      <AlertTitle>
        {count === 1
          ? `Parcela ${oldest.installment_number} do empréstimo ${loan.number} atrasada há ${pluralDays(oldest.days_late)}`
          : `${count} parcelas em atraso, a mais antiga há ${pluralDays(oldest.days_late)}`}
      </AlertTitle>
      <AlertDescription>
        Venceu em {displayDayMonth(oldest.due_date)} e já custou {displayMoney(cost)} de multa e mora.
      </AlertDescription>
      <AlertAction>
        <Button variant="destructive" size="sm" onClick={() => onPay(loan)}>
          Pagar {displayMoney(sum(loan.overdue.map((row) => row.total)))}
        </Button>
      </AlertAction>
    </Alert>
  );
}
