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
import { displayIsoDate } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { FundPositionsTable } from "./fund-positions-table";

type FundReportDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fundName: string;
  report: NonNullable<FundDetails["last_report"]>;
};

/** O último relatório mensal: a carteira posição a posição, como a sala a vê. */
export function FundReportDialog({ open, onOpenChange, fundName, report }: FundReportDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-145">
        <DialogHeader variant="divided">
          <DialogTitle>Relatório de {displayIsoDate(report.day)}</DialogTitle>
          <DialogDescription>
            A carteira de {fundName} no dia em que o relatório saiu. A sala só vê a carteira posição a posição neste
            relatório mensal.
          </DialogDescription>
        </DialogHeader>
        <DialogBody>
          <FundPositionsTable positions={report.positions} />
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
