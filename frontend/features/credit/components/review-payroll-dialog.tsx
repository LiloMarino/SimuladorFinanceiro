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
import { KeyValueRow } from "@/shared/components/key-value-row";
import { displayLeverage } from "@/shared/lib/credit-metrics";
import { displayDate, displayMoney, displayPercent, parseLocalDate } from "@/shared/lib/utils/display";
import type { PayrollQuote } from "@/types";
import { useContractPayroll } from "../hooks/mutations/useContractPayroll";

type ReviewPayrollDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  quote: PayrollQuote;
};

/** "Assinar o consignado": o custo e o efeito na margem e na dívida à vista antes da assinatura. */
export function ReviewPayrollDialog({ open, onOpenChange, quote }: ReviewPayrollDialogProps) {
  const contract = useContractPayroll();

  const sign = () =>
    contract.mutate({ amount: quote.amount, term_months: quote.term_months }, { onSuccess: () => onOpenChange(false) });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-130">
        <DialogHeader variant="divided">
          <DialogTitle>Assinar o consignado</DialogTitle>
          <DialogDescription>Confira antes: o juro fica travado até o fim.</DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-4">
            <div>
              <KeyValueRow label="Cai no caixa hoje" value={displayMoney(quote.amount)} />
              <KeyValueRow
                label="Parcela"
                note={`sai do salário a partir de ${displayDate(parseLocalDate(quote.first_installment_date))}`}
                value={`${quote.term_months} × ${displayMoney(quote.installment)}`}
              />
              <KeyValueRow label="Juro travado" value={`${displayPercent(quote.annual_rate)} ao ano`} />
              <KeyValueRow label="Juro no prazo todo" value={displayMoney(quote.total_interest)} />
              <KeyValueRow total label="Total a pagar" value={displayMoney(quote.total_paid)} />
            </div>

            <div>
              <KeyValueRow
                label="Margem livre depois"
                note={`de ${displayMoney(quote.margin)} por mês`}
                value={displayMoney(quote.margin_free_after)}
              />
              <KeyValueRow
                label="Dívida depois"
                note={
                  quote.leverage_after === null ? undefined : `alavancagem ${displayLeverage(quote.leverage_after)}`
                }
                value={displayMoney(quote.debt_after)}
              />
            </div>
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button onClick={sign} disabled={contract.isPending}>
            Assinar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
