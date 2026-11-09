import { useState } from "react";
import { ChevronDown, Lock, TriangleAlert } from "lucide-react";
import { Alert, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from "@/shared/components/ui/popover";
import { ProfessionGrid } from "@/shared/components/profession-grid";
import { PROFESSIONS } from "@/shared/lib/professions";
import type { RoomPlayer } from "@/types";
import { useChooseProfession } from "../hooks/mutations/useChooseProfession";

type LobbyProfessionPickerProps = {
  nickname: string;
  /** Quem está na sala agora, com a profissão de cada um */
  players: RoomPlayer[];
  /** Quem jogou a partida salva selecionada: a profissão deles fica guardada */
  savedPlayers: RoomPlayer[];
  /** Nome da partida salva selecionada, quando há */
  simulationName?: string | undefined;
};

/** "Sua profissão na partida": escolhe uma das 6; quem já jogou a partida salva volta com a dela. */
export function LobbyProfessionPicker({ nickname, players, savedPlayers, simulationName }: LobbyProfessionPickerProps) {
  const [refusal, setRefusal] = useState<string | null>(null);

  const mine = players.find((p) => p.nickname === nickname)?.profession;
  const locked = savedPlayers.some((p) => p.nickname === nickname);
  const joiningNew = savedPlayers.length > 0 && !locked;

  const { mutate, isPending } = useChooseProfession();

  return (
    <Popover onOpenChange={() => setRefusal(null)}>
      <PopoverTrigger render={<Button variant="outline" size="sm" />}>
        {mine ? PROFESSIONS[mine].name : "Escolher profissão"}
        {locked ? <Lock className="text-muted-foreground" /> : <ChevronDown />}
      </PopoverTrigger>
      <PopoverContent align="end" className="w-104">
        <PopoverHeader>
          <PopoverTitle>
            {locked && simulationName ? `Sua profissão em ${simulationName}` : "Sua profissão na partida"}
          </PopoverTitle>
          <PopoverDescription>
            {locked
              ? "A profissão fica com a partida salva, como a cor."
              : joiningNew && simulationName
                ? `Você entra em ${simulationName} como jogador novo. Escolha uma profissão antes de entrar.`
                : "Muda só o que entra por mês e o que o governo faz com a renda: a despesa e a meta são as mesmas para todos."}
          </PopoverDescription>
        </PopoverHeader>

        <ProfessionGrid
          selected={mine}
          disabled={locked || isPending}
          onSelect={(profession) =>
            mutate(profession, { onSuccess: () => setRefusal(null), onError: (err) => setRefusal(err.message) })
          }
        />

        {refusal && (
          <Alert variant="warning">
            <TriangleAlert />
            <AlertTitle>{refusal}</AlertTitle>
          </Alert>
        )}
      </PopoverContent>
    </Popover>
  );
}
