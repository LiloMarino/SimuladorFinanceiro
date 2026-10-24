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
import { useExpelMember } from "../hooks/mutations/useExpelMember";

type ExpelDialogProps = {
  /** Apelido de quem seria expulso; nulo mantém o diálogo fechado */
  nickname: string | null;
  onClose: () => void;
  party: ElectionParty;
};

/** Expulsar um filiado: pública, e abre a vaga quando ele era candidato ou vice. */
export function ExpelDialog({ nickname, onClose, party }: ExpelDialogProps) {
  const expel = useExpelMember();

  return (
    <AlertDialog open={nickname !== null} onOpenChange={(open) => !open && onClose()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Expulsar {nickname} do {party.abbr}?</AlertDialogTitle>
          <AlertDialogDescription>
            A expulsão é pública: a sala vê o aviso. Se {nickname} era candidato ou vice, a vaga abre e a chapa
            concorre sem ele até você indicar outro filiado.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancelar</AlertDialogCancel>
          <Button
            variant="destructive"
            disabled={expel.isPending || nickname === null}
            onClick={() => nickname && expel.mutate({ nickname }, { onSuccess: onClose })}
          >
            Expulsar
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
