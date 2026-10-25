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
import type { ElectionParty } from "@/types";
import { useLeaveParty } from "../hooks/mutations/useLeaveParty";

type LeavePartyDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  party: ElectionParty;
  isFounder: boolean;
  isVice: boolean;
};

/** Sair do partido: a contribuição para na hora e o que já saiu do caixa não volta. */
export function LeavePartyDialog({ open, onOpenChange, party, isFounder, isVice }: LeavePartyDialogProps) {
  const leave = useLeaveParty();
  const alone = party.members.length === 1;

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Sair do {party.abbr}?</AlertDialogTitle>
          <AlertDialogDescription>
            A contribuição para na hora, e o que você já contribuiu não volta.
            {alone && ` Você é o único filiado: sair desfaz o ${party.abbr}.`}
            {!alone && isFounder && ` Como fundou o partido, ele passa ao filiado mais antigo.`}
            {isVice &&
              ` A vaga de vice do ${party.abbr} abre e a chapa concorre sem vice até a fundação indicar outro filiado.`}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Ficar</AlertDialogCancel>
          <Button
            variant="destructive"
            disabled={leave.isPending}
            onClick={() => leave.mutate(undefined, { onSuccess: () => onOpenChange(false) })}
          >
            Sair do partido
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
