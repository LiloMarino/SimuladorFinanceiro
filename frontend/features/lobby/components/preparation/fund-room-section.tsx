import { TriangleAlert } from "lucide-react";
import { FundMark } from "@/shared/components/fund-mark";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import type { RoomPlayer } from "@/types";
import type { PreparedFund } from "../../lib/fund-preparation";
import { PreparationSection } from "./preparation-section";

type FundRoomSectionProps = {
  /** As gestoras dos outros jogadores da sala */
  rivals: PreparedFund[];
  humans: RoomPlayer[];
  /** O rascunho do jogador: o nome e a sigla que ele está montando */
  draft: { name: string; ticker: string };
};

/** "Nesta sala": a gestora que cada outro jogador preparou, com o aviso de nome ou sigla repetidos. */
export function FundRoomSection({ rivals, humans, draft }: FundRoomSectionProps) {
  const draftName = draft.name.trim().toLowerCase();
  return (
    <PreparationSection
      title="Nesta sala"
      hint={`${rivals.length} ${rivals.length === 1 ? "gestora preparada" : "gestoras preparadas"} por jogadores`}
    >
      {rivals.length === 0 ? (
        <span className="text-xs text-muted-foreground">Nenhum outro jogador preparou uma gestora ainda.</span>
      ) : (
        <ul className="grid">
          {rivals.map((fund) => {
            const sameTicker = fund.ticker === draft.ticker;
            const sameName = draftName !== "" && fund.name.trim().toLowerCase() === draftName;
            return (
              <li
                key={fund.nickname}
                className="grid grid-cols-[auto_auto_minmax(0,1fr)_auto] items-center gap-2.5 border-t border-muted py-2"
              >
                <FundMark name={fund.name} />
                <Badge variant="fund" numeric size="sm">
                  {fund.ticker}
                </Badge>
                <span className="grid min-w-0 gap-0.5">
                  <span className="truncate text-[12.5px]" title={fund.name}>
                    {fund.name}
                  </span>
                  {(sameTicker || sameName) && (
                    <span className="text-xs font-medium text-destructive">
                      {sameTicker && sameName ? "Mesma sigla e mesmo nome" : sameTicker ? "Mesma sigla" : "Mesmo nome"}
                    </span>
                  )}
                </span>
                <span className="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
                  <PlayerAvatar
                    nickname={fund.nickname}
                    color={humans.find((player) => player.nickname === fund.nickname)?.color}
                    size="sm"
                  />
                  {fund.nickname}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </PreparationSection>
  );
}

/** Os conflitos de gestora da sala, que travam o Iniciar; nada aparece sem conflito. */
export function FundConflictsAlert({ conflicts }: { conflicts: string[] }) {
  if (conflicts.length === 0) return null;
  return (
    <Alert variant="destructive">
      <TriangleAlert />
      <AlertTitle>Há gestoras em conflito: o host não consegue iniciar</AlertTitle>
      <AlertDescription>
        <ul className="list-disc pl-4">
          {conflicts.map((conflict) => (
            <li key={conflict}>{conflict}</li>
          ))}
        </ul>
        <span className="mt-1 block">
          Quem trocar primeiro libera o Iniciar. A troca vale para as próximas salas também.
        </span>
      </AlertDescription>
    </Alert>
  );
}
