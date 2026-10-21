import { useState } from "react";
import { ChevronDown, Lock, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Popover, PopoverContent, PopoverDescription, PopoverHeader, PopoverTitle, PopoverTrigger } from "@/shared/components/ui/popover";
import { PlayerColorGrid } from "@/shared/components/player-color-grid";
import { playerColorName, playerColorStyle } from "@/shared/lib/player-colors";
import type { RoomPlayer } from "@/types";
import { useChooseColor } from "../hooks/mutations/useChooseColor";

type LobbyColorPickerProps = {
  nickname: string;
  /** Quem está na sala agora, com a cor de cada um */
  players: RoomPlayer[];
  /** Quem jogou a partida salva selecionada: as cores deles ficam reservadas */
  savedPlayers: RoomPlayer[];
  /** Nome da partida salva selecionada, quando há */
  simulationName?: string;
};

/** "Sua cor na partida": 10 cores, as que já têm dono ficam apagadas com a sigla de quem as tem. */
export function LobbyColorPicker({ nickname, players, savedPlayers, simulationName }: LobbyColorPickerProps) {
  const [refusal, setRefusal] = useState<string | null>(null);

  const mine = players.find((p) => p.nickname === nickname)?.color;
  // Quem jogou a partida selecionada volta com a cor dela
  const locked = savedPlayers.some((p) => p.nickname === nickname);
  // Quem nunca jogou a partida selecionada escolhe só entre as cores que sobraram
  const joiningNew = savedPlayers.length > 0 && !locked;

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
        {locked ? <Lock className="text-muted-foreground" /> : <ChevronDown />}
      </PopoverTrigger>
      <PopoverContent align="end" className="w-88">
        <PopoverHeader>
          <PopoverTitle>{locked && simulationName ? `Sua cor em ${simulationName}` : "Sua cor na partida"}</PopoverTitle>
          <PopoverDescription>
            {locked
              ? "É a cor que você teve nessa partida: não dá pra trocar."
              : joiningNew && simulationName
                ? `Você entra em ${simulationName} como jogador novo. As cores de quem já jogou ficam reservadas.`
                : "É como os outros te reconhecem no ranking e nos gráficos."}
          </PopoverDescription>
        </PopoverHeader>

        <PlayerColorGrid
          owners={[...players, ...savedPlayers]}
          selected={mine}
          disabled={locked || isPending}
          onSelect={chooseColor}
        />

        {refusal && (
          <Alert variant="warning">
            <TriangleAlert />
            <AlertTitle>{refusal}</AlertTitle>
            {mine && <AlertDescription>Você continua com o {playerColorName(mine).toLowerCase()}. Escolha outra cor livre.</AlertDescription>}
          </Alert>
        )}

        <p className="text-xs text-muted-foreground">
          {locked
            ? "As apagadas são de quem já jogou, estando na sala ou não."
            : "Fica guardada neste navegador pra próxima sala."}
        </p>
      </PopoverContent>
    </Popover>
  );
}
