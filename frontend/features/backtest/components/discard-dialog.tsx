import { Trash2 } from "lucide-react";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/shared/components/ui/alert-dialog";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { displayMonthSlashYear } from "@/shared/lib/utils/display";
import type { BacktestProgress } from "@/types";

type DiscardDialogProps = {
  progress: BacktestProgress;
  pending: boolean;
  onDiscard: () => void;
};

/** Descartar apaga o que o backtest gravou; guardar até aqui é o "Parar e ver o resultado". */
export function DiscardDialog({ progress, pending, onDiscard }: DiscardDialogProps) {
  const percent = progress.total_days > 0 ? Math.floor((progress.done_days / progress.total_days) * 100) : 0;
  const reached = progress.current_date ? displayMonthSlashYear(progress.current_date) : displayMonthSlashYear(progress.start_date);

  return (
    <AlertDialog>
      <AlertDialogTrigger render={<Button type="button" variant="outline-destructive" disabled={pending} />}>
        <Trash2 />
        Descartar
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Descartar este backtest?</AlertDialogTitle>
          <AlertDialogDescription>
            Rodou até {reached} ({percent}%). Nada fica salvo e você volta ao lobby. Para guardar até aqui, use Parar e ver
            o resultado.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Continuar rodando</AlertDialogCancel>
          <Button type="button" variant="destructive" onClick={onDiscard}>
            {pending && <Spinner />}
            Descartar
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
