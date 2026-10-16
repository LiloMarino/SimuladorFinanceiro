import { useState } from "react";
import { Check, ChevronDown, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Popover, PopoverContent, PopoverDescription, PopoverHeader, PopoverTitle, PopoverTrigger } from "@/shared/components/ui/popover";
import { PLAYER_COLORS, playerColorName, playerColorStyle } from "@/shared/lib/player-colors";
import { playerInitials } from "@/shared/lib/player-initials";
import { cn } from "@/shared/lib/utils";
import type { RoomPlayer } from "@/types";
import { useChooseColor } from "../hooks/useChooseColor";

type LobbyColorPickerProps = {
  nickname: string;
  /** Quem está na sala agora, com a cor de cada um */
  players: RoomPlayer[];
  /** Quem jogou a partida salva selecionada: as cores deles ficam reservadas */
  savedPlayers: RoomPlayer[];
};

/** "Sua cor na partida": 10 cores, as que já têm dono ficam apagadas com a sigla de quem as tem. */
export function LobbyColorPicker({ nickname, players, savedPlayers }: LobbyColorPickerProps) {
  const [refusal, setRefusal] = useState<string | null>(null);

  const mine = players.find((p) => p.nickname === nickname)?.color;
  // Quem jogou a partida selecionada volta com a cor dela
  const locked = savedPlayers.some((p) => p.nickname === nickname);

  const { mutate, isPending } = useChooseColor();
  const chooseColor = (color: string) =>
    mutate(color, { onSuccess: () => setRefusal(null), onError: (err) => setRefusal(err.message) });

  return (
    <Popover onOpenChange={() => setRefusal(null)}>
      <PopoverTrigger render={<Button variant="outline" size="sm" />}>
        <span
          className="size-3 rounded-[3px]"
          style={{ backgroundColor: playerColorStyle(mine).background }}
          aria-hidden="true"
        />
        Sua cor
        <ChevronDown />
      </PopoverTrigger>
      <PopoverContent align="end" className="w-88">
        <PopoverHeader>
          <PopoverTitle>Sua cor na partida</PopoverTitle>
          <PopoverDescription>
            {locked
              ? "É a cor que você teve nessa partida: não dá pra trocar."
              : "É como os outros te reconhecem no ranking e nos gráficos."}
          </PopoverDescription>
        </PopoverHeader>

        <div className="grid grid-cols-5 gap-x-1.5 gap-y-2.5">
          {PLAYER_COLORS.map((color) => {
            const owner = players.find((p) => p.color === color.key) ?? savedPlayers.find((p) => p.color === color.key);
            const isMine = color.key === mine;
            const taken = owner !== undefined && !isMine;
            return (
              <button
                key={color.key}
                type="button"
                disabled={taken || locked || isPending}
                aria-pressed={isMine}
                aria-label={taken ? `${color.name}, de ${owner.nickname}` : color.name}
                onClick={() => chooseColor(color.key)}
                className="grid cursor-pointer justify-items-center gap-1 rounded-lg outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-default"
              >
                <span
                  className={cn(
                    "grid size-10 place-content-center rounded-[10px] text-xs font-semibold",
                    taken && "opacity-45",
                    isMine && "ring-2 ring-foreground ring-offset-2 ring-offset-popover",
                  )}
                  style={{ backgroundColor: `var(--${color.key})`, color: color.foreground }}
                >
                  {taken && playerInitials(owner.nickname)}
                  {isMine && <Check className="size-4.5" />}
                </span>
                <span className={cn("text-[11px]", isMine ? "font-semibold" : "text-muted-foreground")}>
                  {color.name}
                </span>
              </button>
            );
          })}
        </div>

        {refusal && (
          <Alert variant="warning">
            <TriangleAlert />
            <AlertTitle>{refusal}</AlertTitle>
            {mine && <AlertDescription>Você continua com o {playerColorName(mine).toLowerCase()}. Escolha outra cor livre.</AlertDescription>}
          </Alert>
        )}

        <p className="text-xs text-muted-foreground">Fica guardada neste navegador pra próxima sala.</p>
      </PopoverContent>
    </Popover>
  );
}
