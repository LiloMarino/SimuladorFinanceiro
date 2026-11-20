import { Lock } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { EXPANSIONS, type ExpansionKey } from "@/shared/lib/expansions";
import { GAME_TYPES } from "@/shared/lib/game-types";
import type { GameType } from "@/types";

type ExpansionLockNoteProps = {
  expansion: ExpansionKey;
  gameType: GameType;
};

/** O motivo de a chave da expansão estar travada ligada: o tipo de partida escolhido depende dela. */
export function ExpansionLockNote({ expansion, gameType }: ExpansionLockNoteProps) {
  const type = GAME_TYPES[gameType];
  return (
    <div className="px-4 pb-3.5">
      <Alert variant="muted">
        <Lock />
        <AlertDescription>
          {type?.label} usa a expansão {EXPANSIONS[expansion].label}: ela fica ligada enquanto esse for o tipo de
          partida. Escolha outro tipo para poder desligar.
        </AlertDescription>
      </Alert>
    </div>
  );
}
