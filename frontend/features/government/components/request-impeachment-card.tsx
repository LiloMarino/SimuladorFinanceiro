import { Siren } from "lucide-react";
import { useState } from "react";
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
import type { GovernmentPanel } from "@/types";
import { useRequestImpeachment } from "../hooks/mutations/useRequestImpeachment";

type RequestImpeachmentCardProps = {
  canRequest: GovernmentPanel["congress"]["can_request_impeachment"];
  block: GovernmentPanel["congress"]["impeachment_block"];
};

/** O líder do partido abre o pedido de impeachment; o diálogo explica o custo antes de confirmar. */
export function RequestImpeachmentCard({ canRequest, block }: RequestImpeachmentCardProps) {
  const [open, setOpen] = useState(false);
  const request = useRequestImpeachment();

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg border p-3">
      <Siren className="size-4 text-muted-foreground" />
      <div className="grid flex-1 gap-0.5 text-sm">
        <span className="font-medium">Pedir o impeachment do presidente</span>
        <span className="text-muted-foreground">
          {block ?? "A casa vota no próximo dia de votação; 68 das 101 cadeiras precisam votar Sim."}
        </span>
      </div>
      <Button size="sm" variant="outline" disabled={!canRequest} onClick={() => setOpen(true)}>
        Pedir impeachment
      </Button>
      <AlertDialog open={open} onOpenChange={setOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Pedir o impeachment?</AlertDialogTitle>
            <AlertDialogDescription>
              A sala inteira vê a manchete e o presidente recebe o aviso com o nome do seu partido. Se a casa rejeitar,
              o seu partido ganha 5 pontos de rejeição (a escala vai de 0 a 100 e tira apoio do partido) entre os
              eleitores que ainda aprovam o presidente, e ele não pode pedir de novo neste mandato.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Voltar</AlertDialogCancel>
            <Button
              variant="destructive"
              disabled={request.isPending}
              onClick={() => request.mutate(undefined, { onSuccess: () => setOpen(false) })}
            >
              Pedir impeachment
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
