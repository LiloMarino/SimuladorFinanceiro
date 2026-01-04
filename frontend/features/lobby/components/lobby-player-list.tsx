import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser } from "@fortawesome/free-solid-svg-icons";
import { useAuth } from "@/shared/hooks/useAuth";
import { stringToColor } from "@/shared/lib/utils";

type LobbyPlayer = {
  nickname: string;
  client_id: string;
};

interface LobbyPlayersListProps {
  players: LobbyPlayer[];
  maxPlayers: number;
}

export function LobbyPlayersList({ players, maxPlayers }: LobbyPlayersListProps) {
  const { getUser } = useAuth();
  const user = getUser();

  return (
    <div>
      <h2 className="text-lg font-semibold mb-4">Lobby</h2>

      <h3 className="font-medium mb-3">
        Jogadores{" "}
        <span className="text-sm text-gray-500">
          ({players.length}/{maxPlayers})
        </span>
      </h3>

      <div className="border rounded-lg overflow-hidden">
        <div className="divide-y">
          {players.map((player) => {
            const isYou = player.client_id === user?.client_id;
            const color = stringToColor(player.nickname);

            return (
              <div key={player.client_id} className={`p-3 flex items-center ${isYou ? "bg-green-50" : ""}`}>
                <FontAwesomeIcon icon={faUser} className="mr-2" style={{ color }} />
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
