import { User } from "lucide-react";
import { useAuth } from "@/shared/hooks/useAuth";
import { stringToColor } from "@/shared/lib/utils";
import { useLobbyPlayers } from "../hooks/queries/useLobbyPlayers";

interface LobbyPlayersListProps {
  maxPlayers: number;
}

export function LobbyPlayersList({ maxPlayers }: LobbyPlayersListProps) {
  const { user } = useAuth();
  const { data: players } = useLobbyPlayers();

  const playersList = [...(players ?? [])].sort((a, b) => a.nickname.localeCompare(b.nickname));
  return (
    <div>
      <h2 className="text-lg font-semibold mb-4">Lobby</h2>

      <h3 className="font-medium mb-3">
        Jogadores{" "}
        <span className="text-sm text-gray-500">
          ({playersList.length}/{maxPlayers})
        </span>
      </h3>

      <div className="border rounded-lg overflow-hidden">
        <div className="divide-y">
          {playersList.map((player) => {
            const isYou = player.nickname === user?.nickname;
            const color = stringToColor(player.nickname);

            return (
              <div key={player.nickname} className={`p-3 flex items-center ${isYou ? "bg-green-50" : ""}`}>
                <User className="w-4 h-4 mr-2 flex-shrink-0 " style={{ color }} />
                <span className={isYou ? "font-medium" : ""}>
                  {player.nickname}
                  {isYou && " (você)"}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
