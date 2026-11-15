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
import { Spinner } from "@/shared/components/ui/spinner";
import { useRemoveComanager } from "../hooks/mutations/useRemoveComanager";
import { isInvited, type Comanager } from "../lib/fund-comanagers";

type ComanagerRemoveDialogProps = {
  /** O co-gestor ou o convite que sai; nulo com o diálogo fechado */
  comanager: Comanager | null;
  onClose: () => void;
  fundId: number;
};

/** Tirar o co-gestor ou retirar o convite: o acesso acaba no mesmo pregão e a parte volta ao principal. */
export function ComanagerRemoveDialog({ comanager, onClose, fundId }: ComanagerRemoveDialogProps) {
  const remove = useRemoveComanager(fundId);
  const invited = comanager !== null && isInvited(comanager);

  return (
    <AlertDialog open={comanager !== null} onOpenChange={(open) => !open && onClose()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            {invited ? `Retirar o convite de ${comanager.nickname}?` : `Tirar ${comanager?.nickname} da gestão?`}
          </AlertDialogTitle>
          <AlertDialogDescription>
            {invited
              ? "A parte reservada volta a ficar livre."
              : "O acesso à carteira da gestora acaba no mesmo pregão, e a parte dele volta para você na próxima divisão de taxa."}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Manter</AlertDialogCancel>
          <Button
            variant="destructive"
            disabled={remove.isPending}
            onClick={() => comanager && remove.mutate(comanager.user_id, { onSuccess: onClose })}
          >
            {remove.isPending && <Spinner />}
            {invited ? "Retirar o convite" : "Tirar da gestão"}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
