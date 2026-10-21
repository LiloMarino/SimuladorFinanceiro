import { useState } from "react";
import { Trash2 } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/shared/components/ui/alert-dialog";
import { Button } from "@/shared/components/ui/button";
import { displayMonthSlashYear } from "@/shared/lib/utils/display";
import type { SimulationListItem } from "@/types";
import { useDeleteSimulation } from "../hooks/mutations/useDeleteSimulation";

type DeleteSimulationButtonProps = {
  simulation: SimulationListItem;
  disabled: boolean;
};

export function DeleteSimulationButton({ simulation, disabled }: DeleteSimulationButtonProps) {
  const [confirming, setConfirming] = useState(false);
  const { mutate: deleteSimulation, isPending } = useDeleteSimulation();

  const players = simulation.players_count <= 1 ? "Solo" : `${simulation.players_count} jogadores`;

  return (
    <>
      <Button
        variant="destructive"
        size="icon"
        aria-label={`Excluir ${simulation.name}`}
        disabled={disabled}
        onClick={() => setConfirming(true)}
      >
        <Trash2 />
      </Button>

      <AlertDialog open={confirming} onOpenChange={setConfirming}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir a partida {simulation.name}?</AlertDialogTitle>
            <AlertDialogDescription>
              {displayMonthSlashYear(simulation.start_date)} → {displayMonthSlashYear(simulation.end_date)} · {players}.
              A partida e tudo o que ela guarda somem da lista. Isso não pode ser desfeito.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel variant="outline">Cancelar</AlertDialogCancel>
            <AlertDialogAction
              variant="destructive"
              disabled={isPending}
              onClick={() => deleteSimulation(simulation.id, { onSuccess: () => setConfirming(false) })}
            >
              Excluir partida
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
