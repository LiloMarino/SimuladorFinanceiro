import { useState } from "react";
import { Ellipsis, UserMinus } from "lucide-react";
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/shared/components/ui/dropdown-menu";
import type { RoomPlayer } from "@/types";
import { useRemovePlayer } from "../hooks/mutations/useRemovePlayer";

type LobbyPlayerMenuProps = {
  player: RoomPlayer;
};

/** O ⋯ do cartão de outra pessoa, só para o host: Remover da sala pede confirmação. */
export function LobbyPlayerMenu({ player }: LobbyPlayerMenuProps) {
  const [confirming, setConfirming] = useState(false);
  const remove = useRemovePlayer();

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger
          render={
            <Button variant="ghost" size="icon-sm" className="size-7" aria-label={`Opções de ${player.nickname}`} />
          }
        >
          <Ellipsis className="size-4" />
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuItem variant="destructive" onClick={() => setConfirming(true)}>
            <UserMinus />
            Remover da sala
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <AlertDialog open={confirming} onOpenChange={setConfirming}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remover {player.nickname} da sala?</AlertDialogTitle>
            <AlertDialogDescription>
              Sai da sala agora, com o aviso de que o host a removeu, e a vaga e a cor ficam livres. A conta continua:
              quem entrar de novo com o apelido ocupa uma vaga outra vez.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel variant="outline">Cancelar</AlertDialogCancel>
            <Button
              variant="destructive"
              disabled={remove.isPending}
              onClick={() => remove.mutate(player.nickname, { onSuccess: () => setConfirming(false) })}
            >
              Remover da sala
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
