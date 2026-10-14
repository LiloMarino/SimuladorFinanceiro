import { Avatar, AvatarFallback } from "@/shared/components/ui/avatar";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { cn, stringToColor } from "@/shared/lib/utils";

type LobbyPlayersListProps = {
  maxPlayers: number;
  hostNickname: string;
};

/** Jogadores da sala em cartões, com as vagas livres à vista. */
export function LobbyPlayersList({ maxPlayers, hostNickname }: LobbyPlayersListProps) {
  const { user } = useAuth();
  const { data: players } = useRoomPlayers();

  // Host primeiro, depois quem joga, em ordem alfabética
  const sorted = [...(players ?? [])].sort(
    (a, b) =>
      Number(b.nickname === hostNickname) - Number(a.nickname === hostNickname) || a.nickname.localeCompare(b.nickname),
  );
  const freeSlots = Math.max(maxPlayers - sorted.length, 0);
  const alone = sorted.length <= 1;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Jogadores</CardTitle>
        <CardAction>
          <span className="font-mono text-muted-foreground">
            {sorted.length} / {maxPlayers}
          </span>
        </CardAction>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-2 gap-2.5">
          {sorted.map((player) => {
            const isYou = player.nickname === user?.nickname;
            const isHost = player.nickname === hostNickname;
            return (
              <div
                key={player.nickname}
                className={cn(
                  "flex items-center gap-3 rounded-[10px] border p-3",
                  isYou ? "border-info-border bg-info-soft" : "border-border bg-card",
                )}
              >
                <Avatar size="lg">
                  <AvatarFallback color={stringToColor(player.nickname)}>
                    {player.nickname.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="grid min-w-0">
                  <span className="truncate font-semibold">
                    {player.nickname}
                    {isYou && <span className="font-normal text-secondary-foreground"> (você)</span>}
                  </span>
                  <span className={cn("text-xs font-medium", isHost ? "text-info" : "text-success")}>
                    {isHost ? "Host" : "● Online"}
                  </span>
                </div>
              </div>
            );
          })}

          {/* Sala vazia: convite no lugar das vagas */}
          {alone ? (
            <div className="col-span-full grid gap-1 rounded-[10px] border border-dashed border-info-border bg-info-soft/40 p-4">
              <span className="font-semibold">Só você por aqui</span>
              <span className="text-[13px] text-muted-foreground">
                Mande o link acima pra quem vai jogar. Também dá pra jogar sozinho.
              </span>
            </div>
          ) : (
            Array.from({ length: freeSlots }, (_, i) => (
              <div
                key={i}
                className="flex h-14.5 items-center justify-center rounded-[10px] border border-dashed border-input text-[13px] text-faint-foreground"
              >
                Vaga livre
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
