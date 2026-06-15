import { User } from "lucide-react";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { stringToColor } from "@/shared/lib/utils";
import { useQueryApi } from "@/shared/hooks/useQueryApi";

interface LobbyPlayersListProps {
  maxPlayers: number;
}

export function LobbyPlayersList({ maxPlayers }: LobbyPlayersListProps) {
  const { user } = useAuth();
  const { data: players, setData: setPlayers } = useQueryApi<{ nickname: string }[]>("/api/simulation/players");

  // 🔹 Player entrou
  useRealtime("player_join", ({ nickname }) => {
    setPlayers((prev) => {
      if (!prev) return [{ nickname }];

      if (prev.some((p) => p.nickname === nickname)) {
        return prev;
      }

      return [...prev, { nickname }];
    });
  });

  // 🔹 Player saiu
  useRealtime("player_exit", ({ nickname }) => {
    setPlayers((prev) => {
      if (!prev) return prev;
      return prev.filter((p) => p.nickname !== nickname);
    });
  });

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
