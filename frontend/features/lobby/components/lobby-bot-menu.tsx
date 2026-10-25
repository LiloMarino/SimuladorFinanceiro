import { Ellipsis, Settings2, Trash2 } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/shared/components/ui/dropdown-menu";
import type { RoomPlayer } from "@/types";
import { useRemoveBot } from "../hooks/mutations/useRemoveBot";

type LobbyBotMenuProps = {
  player: RoomPlayer;
  onConfigure: () => void;
};

/** O ⋯ do cartão do bot: Configurar abre o diálogo e Remover da sala tira o bot, com Desfazer. */
export function LobbyBotMenu({ player, onConfigure }: LobbyBotMenuProps) {
  const remove = useRemoveBot();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <Button variant="ghost" size="icon-sm" className="size-7" aria-label={`Opções de ${player.nickname}`} />
        }
      >
        <Ellipsis className="size-4" />
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={onConfigure}>
          <Settings2 />
          Configurar
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem variant="destructive" onClick={() => remove.mutate(player)}>
          <Trash2 />
          Remover da sala
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
