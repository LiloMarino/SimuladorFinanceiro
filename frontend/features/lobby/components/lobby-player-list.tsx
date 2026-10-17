import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Status } from "@/shared/components/ui/status";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { MAX_PLAYERS } from "@/shared/lib/player-colors";
import { cn } from "@/shared/lib/utils";
import type { RoomPlayer } from "@/types";
import { useApplyColorPreference } from "../hooks/useApplyColorPreference";
import { LobbyColorPicker } from "./lobby-color-picker";

type LobbyPlayersListProps = {
  hostNickname: string;
  /** Quem jogou a partida salva selecionada, com a cor guardada */
  savedPlayers: RoomPlayer[];
};

/** Jogadores da sala em cartões, com as vagas livres à vista. */
export function LobbyPlayersList({ hostNickname, savedPlayers }: LobbyPlayersListProps) {
  const { user } = useAuth();
  const { data: players } = useRoomPlayers();

  // Host primeiro, depois quem joga, em ordem alfabética
  const sorted = [...(players ?? [])].sort(
    (a, b) =>
      Number(b.nickname === hostNickname) - Number(a.nickname === hostNickname) || a.nickname.localeCompare(b.nickname),
  );

  // Quem jogou a partida selecionada e não está na sala segue dono da vaga e da cor
  const absent = savedPlayers.filter((saved) => !sorted.some((p) => p.nickname === saved.nickname));
  const occupied = sorted.length + absent.length;
  const freeSlots = Math.max(MAX_PLAYERS - occupied, 0);
  const alone = sorted.length <= 1 && absent.length === 0;
  const full = occupied >= MAX_PLAYERS;

  const me = sorted.find((p) => p.nickname === user?.nickname);
  useApplyColorPreference(
    me,
    savedPlayers.some((p) => p.nickname === me?.nickname),
  );

  return (
    <Card>
      <CardHeader>
        <div className="grid gap-1">
          <CardTitle>Jogadores</CardTitle>
          {absent.length > 0 && (
            <span className="text-xs text-muted-foreground">
              {sorted.length} na sala · {absent.length} offline da partida selecionada
            </span>
          )}
        </div>
        <CardAction>
          <span className="flex items-center gap-2">
            {full && <Badge variant="warning">Sala cheia</Badge>}
            <span className="font-mono text-muted-foreground">
              {occupied} / {MAX_PLAYERS}
            </span>
          </span>
        </CardAction>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-2 gap-2.5">
          {sorted.map((player) => {
            const isYou = player.nickname === user?.nickname;
            const isHost = player.nickname === hostNickname;
            const isNew = savedPlayers.length > 0 && !savedPlayers.some((p) => p.nickname === player.nickname);
            return (
              <div
                key={player.nickname}
                className={cn(
                  "flex items-center gap-3 rounded-[10px] border p-3",
                  isYou ? "border-info-border bg-info-soft" : "border-border bg-card",
                )}
              >
                <PlayerAvatar nickname={player.nickname} color={player.color} size="lg" />
                <div className="grid min-w-0 flex-1">
                  <span className="truncate font-semibold">
                    {player.nickname}
                    {isYou && <span className="font-normal text-secondary-foreground"> (você)</span>}
                    {isNew && (
                      <Badge variant="info" size="sm" className="ml-1.5 align-[1px]">
                        Novo
                      </Badge>
                    )}
                  </span>
                  {isHost ? (
                    <span className="text-xs font-medium text-info">Host</span>
                  ) : (
                    <Status status="online">Online</Status>
                  )}
                </div>
                {isYou && <LobbyColorPicker nickname={player.nickname} players={sorted} savedPlayers={savedPlayers} />}
              </div>
            );
          })}

          {/* Ausentes da partida selecionada: a cor e a vaga ficam reservadas */}
          {absent.map((player) => (
            <div
              key={player.nickname}
              className="flex items-center gap-3 rounded-[10px] border border-dashed border-input p-3"
            >
              <span className="opacity-45">
                <PlayerAvatar nickname={player.nickname} color={player.color} size="lg" />
              </span>
              <div className="grid min-w-0 flex-1">
                <span className="truncate font-semibold text-muted-foreground">{player.nickname}</span>
                <Status status="offline">Offline</Status>
              </div>
            </div>
          ))}

          {/* Sozinho na sala: o convite ocupa a coluna ao lado do host, antes das vagas livres */}
          {alone && (
            <div className="grid content-center gap-1 rounded-[10px] border border-dashed border-info-border bg-info-soft/40 p-3">
              <span className="font-semibold">Só você por aqui</span>
              <span className="text-[13px] text-muted-foreground">
                Mande o link acima pra quem vai jogar. Também dá pra jogar sozinho.
              </span>
            </div>
          )}

          {Array.from({ length: freeSlots }, (_, i) => (
            <div
              key={i}
              className="flex h-14.5 items-center justify-center rounded-[10px] border border-dashed border-input text-[13px] text-faint-foreground"
            >
              Vaga livre
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
