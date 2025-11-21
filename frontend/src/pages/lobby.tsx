import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCopy, faShareAlt, faUser, faPlay } from "@fortawesome/free-solid-svg-icons";

interface Player {
  name: string;
  status: string;
  color: string;
  isYou?: boolean;
}

interface LobbyProps {
  maxPlayers?: number;
  players?: Player[];
}

export default function LobbyPage({
  maxPlayers = 8,
  players = [
    { name: "Você", status: "Pronto", color: "green", isYou: true },
    { name: "TraderPro", status: "Conectado", color: "blue" },
    { name: "InvestAnjo", status: "Conectado", color: "purple" },
  ],
}: LobbyProps) {
  const [nickname, setNickname] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const hostIP = "192.168.1.100:3000";

  const copyHostIP = () => {
    navigator.clipboard.writeText(hostIP);
    alert("IP copiado para a área de transferência!");
  };

  const shareHostIP = () => {
    // Placeholder: implementar compartilhamento real
    alert(`Compartilhar IP: ${hostIP}`);
  };

  const startGame = () => {
    // Placeholder: lógica para iniciar partida
    alert(`Iniciando partida como ${nickname || "anônimo"}`);
  };

  return (
    <section id="lobby" className="section-content p-4">
      <div className="bg-white rounded-lg shadow p-6 max-w-3xl mx-auto">
        <h2 className="text-2xl font-semibold mb-6 text-center">Entrar na Partida</h2>

        <div className="space-y-6">
          {/* Nickname Input */}
          <div>
            <label htmlFor="nickname" className="block text-sm font-medium text-gray-700 mb-1">
              Seu Nickname
            </label>
            <input
              type="text"
              id="nickname"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              className="w-full p-2 border rounded-md"
              placeholder="Ex: TraderPro2023"
            />
          </div>

          {/* Simulation Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-1">
                Data Inicial
              </label>
              <input
                type="date"
                id="start-date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full p-2 border rounded-md"
              />
            </div>
            <div>
              <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 mb-1">
                Data Final
              </label>
              <input
                type="date"
                id="end-date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full p-2 border rounded-md"
              />
            </div>
          </div>

          {/* Multiplayer Options */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-medium mb-2">Opções Multiplayer</h3>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <label className="block text-sm text-gray-600 mb-1">IP do Host</label>
                <div className="flex">
                  <input type="text" value={hostIP} className="flex-1 p-2 border rounded-l-md bg-white" readOnly />
                  <button onClick={copyHostIP} className="bg-gray-200 hover:bg-gray-300 px-3 rounded-r-md">
                    <FontAwesomeIcon icon={faCopy} />
                  </button>
                </div>
              </div>
              <button
                onClick={shareHostIP}
                className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md whitespace-nowrap flex items-center gap-1"
              >
                <FontAwesomeIcon icon={faShareAlt} /> Compartilhar
              </button>
            </div>
          </div>

          {/* Players List */}
          <div>
            <h3 className="font-medium mb-3">
              Jogadores na Sala{" "}
              <span className="text-sm text-gray-500">
                ({players.length}/{maxPlayers})
              </span>
            </h3>
            <div className="border rounded-lg overflow-hidden">
              <div className="divide-y divide-gray-200">
                {players.map((p) => (
                  <div key={p.name} className={`p-3 flex items-center justify-between ${p.isYou ? "bg-green-50" : ""}`}>
                    <div className="flex items-center">
                      <FontAwesomeIcon icon={faUser} className={`mr-2 text-${p.color}-600`} />
                      <span className={p.isYou ? "font-medium" : ""}>{p.name}</span>
                    </div>
                    <span className="text-sm text-gray-500">{p.status}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Start Button */}
          <button
            onClick={startGame}
            className="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-md font-medium flex items-center justify-center gap-2"
          >
            <FontAwesomeIcon icon={faPlay} /> Iniciar Partida
          </button>
        </div>
      </div>
    </section>
  );
}
