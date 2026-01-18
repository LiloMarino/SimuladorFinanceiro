import { useState } from "react";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { toast } from "sonner";
import { Button } from "@/shared/components/ui/button";
import {
    AlertDialog,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogAction,
    AlertDialogCancel,
} from "@/shared/components/ui/alert-dialog";

export function SimulationControl() {
  const [showStopConfirm, setShowStopConfirm] = useState(false);

  // Mutação para encerrar simulação
  const { mutate: stopSimulation, loading: stoppingSimulation } = useMutationApi(
    "/api/simulation/stop",
    {
      method: "POST",
      onSuccess: () => {
        toast.success("Simulação encerrada com sucesso!");
        setShowStopConfirm(false);
      },
      onError: (err) => {
        toast.error(err.message);
      },
    }
  );

  const handleStopSimulation = () => {
    stopSimulation({});
    setShowStopConfirm(false);
  };

  return (
    <AlertDialog open={showStopConfirm} onOpenChange={setShowStopConfirm}>
      <div className="max-w-sm space-y-4">
        <div>
          <Button
            onClick={() => setShowStopConfirm(true)}
            variant="destructive"
            className="w-full"
            disabled={stoppingSimulation}
          >
            Encerrar Simulação
          </Button>
          <p className="text-xs text-gray-500 mt-2">
            Encerra a simulação atual e retorna todos os jogadores ao lobby.
          </p>
        </div>
      </div>

      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Encerrar Simulação</AlertDialogTitle>
          <AlertDialogDescription>
            ⚠️ Todos os jogadores serão redirecionados para o lobby.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <AlertDialogFooter>
          <AlertDialogCancel asChild>
            <Button variant="outline">Cancelar</Button>
          </AlertDialogCancel>
          <AlertDialogAction asChild>
            <Button
              variant="destructive"
              onClick={handleStopSimulation}
              disabled={stoppingSimulation}
            >
              Confirmar Encerramento
            </Button>
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
