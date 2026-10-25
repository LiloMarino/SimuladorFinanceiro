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
import type { SeriesCoverage } from "@/types";
import { useDeleteStock } from "../hooks/mutations/useDeleteStock";

type DeleteStockButtonProps = {
  stock: SeriesCoverage;
  disabled: boolean;
};

export function DeleteStockButton({ stock, disabled }: DeleteStockButtonProps) {
  const [confirming, setConfirming] = useState(false);
  const { mutate: deleteStock, isPending } = useDeleteStock();

  return (
    <>
      <Button
        variant="ghost"
        size="icon-sm"
        aria-label={`Apagar ${stock.key}`}
        disabled={disabled}
        onClick={() => setConfirming(true)}
      >
        <Trash2 />
      </Button>

      <AlertDialog open={confirming} onOpenChange={setConfirming}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Apagar {stock.key}?</AlertDialogTitle>
            <AlertDialogDescription>
              Os preços, o perfil e a classificação do ativo somem da base, e o futuro gerado passa a pedir recálculo.
              Isso não pode ser desfeito. Ativo negociado em partida salva não é apagado.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel variant="outline">Cancelar</AlertDialogCancel>
            <AlertDialogAction
              variant="destructive"
              disabled={isPending}
              onClick={() => deleteStock(stock.key, { onSuccess: () => setConfirming(false) })}
            >
              Apagar ativo
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
