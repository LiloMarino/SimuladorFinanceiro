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
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { LoanQuote } from "@/types";
import { InstallmentsTable } from "./installments-table";

type InstallmentsDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  quote: LoanQuote;
};

/** "As N parcelas": o cronograma completo do empréstimo simulado. */
export function InstallmentsDialog({ open, onOpenChange, quote }: InstallmentsDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-130">
        <DialogHeader variant="divided">
          <DialogTitle>As {quote.term_months} parcelas</DialogTitle>
          <DialogDescription>
            {displayMoney(quote.amount)} a {displayPercent(quote.annual_rate)} ao ano, com {quote.term_months} parcelas
            de {displayMoney(quote.installment)}.
          </DialogDescription>
        </DialogHeader>
        <DialogBody>
          <InstallmentsTable schedule={quote.schedule} />
        </DialogBody>
        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Fechar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
