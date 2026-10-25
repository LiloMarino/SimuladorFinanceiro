import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { displayDayMonth, displayMoney } from "@/shared/lib/utils/display";
import type { CreditLoan, CreditRating } from "@/types";
import { usePayOverdue } from "../hooks/mutations/usePayOverdue";
import { KeyValueRow } from "@/shared/components/key-value-row";

type PayOverdueDialogProps = {
  loan: CreditLoan;
  rating: CreditRating;
  /** Caixa de hoje, em reais */
  cash: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

const sum = (values: string[]) => values.reduce((total, value) => total + Number(value), 0);

/** "Pagar a parcela em atraso": parcela, multa e mora do dia, tudo de uma vez. */
export function PayOverdueDialog({ loan, rating, cash, open, onOpenChange }: PayOverdueDialogProps) {
  const pay = usePayOverdue(loan.id);
  const overdue = loan.overdue;
  const total = sum(overdue.map((item) => item.total));
  const daysLate = Math.max(...overdue.map((item) => item.days_late), 0);
  const covered = Number(cash) >= total;
  const gradeFell = rating.previous_grade !== null && rating.previous_grade !== rating.grade;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-130">
        <DialogHeader variant="divided">
          <DialogTitle>Pagar a parcela em atraso</DialogTitle>
          <DialogDescription>
            Empréstimo {loan.number} · {daysLate} {daysLate === 1 ? "dia" : "dias"} de atraso
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-4">
            <div>
              <KeyValueRow
                label={
                  overdue.length === 1
                    ? `Parcela de ${displayDayMonth(overdue[0].due_date)}`
                    : `${overdue.length} parcelas em atraso`
                }
                value={displayMoney(sum(overdue.map((item) => item.installment)))}
              />
              <KeyValueRow label="Multa de 2%" value={displayMoney(sum(overdue.map((item) => item.fee)))} />
              <KeyValueRow
                label={`Mora · ${daysLate} ${daysLate === 1 ? "dia" : "dias"} a 1% ao mês`}
                value={displayMoney(sum(overdue.map((item) => item.interest)))}
              />
              <KeyValueRow total label="Para pagar hoje" value={displayMoney(total)} />
            </div>

            <span className="text-xs text-muted-foreground">
              A mora corre por dia até você pagar; a multa entra uma vez. Caixa hoje:{" "}
              <span className="font-mono">{displayMoney(cash)}</span>.
            </span>

            {!covered && (
              <Alert variant="warning">
                <TriangleAlert />
                <AlertTitle>Falta {displayMoney(total - Number(cash))} no caixa</AlertTitle>
                <AlertDescription>Venda algo antes de pagar.</AlertDescription>
              </Alert>
            )}

            <Alert variant="destructive">
              <TriangleAlert />
              <AlertTitle>
                {gradeFell
                  ? `A nota já caiu de ${rating.previous_grade} para ${rating.grade}`
                  : "O atraso pesa na nota"}
              </AlertTitle>
              <AlertDescription>Pagar agora para a mora; o atraso pesa na nota por 12 meses.</AlertDescription>
            </Alert>
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Agora não
          </Button>
          <Button
            variant="destructive"
            disabled={!covered || pay.isPending}
            onClick={() => pay.mutate(undefined, { onSuccess: () => onOpenChange(false) })}
          >
            Pagar {displayMoney(total)}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
