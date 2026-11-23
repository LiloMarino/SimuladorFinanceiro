import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/shared/components/ui/alert-dialog";
import { Button } from "@/shared/components/ui/button";
import { displayMoney, displayMonthYear, displayPercent } from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { useLeaveHome } from "../hooks/mutations/useLeaveHome";

type LeaveHomeDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mechanic: Extract<ProfessionMechanic, { kind: "graduate" }>;
};

/** "Sair de casa": a despesa que volta ao valor cheio e o prazo do desconto que se perde. */
export function LeaveHomeDialog({ open, onOpenChange, mechanic }: LeaveHomeDialogProps) {
  const leave = useLeaveHome();

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Sair da casa dos pais?</AlertDialogTitle>
          <AlertDialogDescription>
            A despesa deixa de ter o desconto de {displayPercent(mechanic.home_discount_rate, 0)} e volta a{" "}
            {displayMoney(mechanic.full_expense)} por mês, {displayMoney(mechanic.home_discount)} a mais do que hoje. O
            desconto iria até {displayMonthYear(mechanic.home_until)}. Não dá para voltar.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Agora não</AlertDialogCancel>
          <Button
            variant="outline"
            disabled={leave.isPending}
            onClick={() => leave.mutate(undefined, { onSuccess: () => onOpenChange(false) })}
          >
            Sair de casa
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
