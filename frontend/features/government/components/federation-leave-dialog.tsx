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
import { displayShortDate } from "@/shared/lib/utils/display";
import type { Federation } from "@/types";
import { useLeaveFederation } from "../hooks/mutations/useLeaveFederation";

type FederationLeaveDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  federation: Federation;
};

/** Sair da federação a desfaz na hora para os dois, e quem sai fica impedido de se federar na eleição seguinte. */
export function FederationLeaveDialog({ open, onOpenChange, federation }: FederationLeaveDialogProps) {
  const leave = useLeaveFederation();

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Sair da {federation.name}?</AlertDialogTitle>
          <AlertDialogDescription>
            A federação vale até {displayShortDate(federation.ends_on)}. Sair antes a desfaz na hora para os dois
            partidos, e o seu fica impedido de se federar na eleição seguinte. O jornal noticia a saída.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Ficar</AlertDialogCancel>
          <Button
            variant="destructive"
            disabled={leave.isPending}
            onClick={() => leave.mutate(undefined, { onSuccess: () => onOpenChange(false) })}
          >
            Sair da federação
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
