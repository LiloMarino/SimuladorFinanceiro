import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCopy, faUser, faPlay } from "@fortawesome/free-solid-svg-icons";

type Player = {
  name: string;
  status: string;
  color: string;
  isYou?: boolean;
};

interface LobbyHostProps {
  maxPlayers?: number;
  players?: Player[];
}

export function LobbyPage({
  maxPlayers = 8,
  players = [
    { name: "Você", status: "Pronto", color: "green", isYou: true },
    { name: "TraderPro", status: "Conectado", color: "blue" },
    { name: "InvestAnjo", status: "Conectado", color: "purple" },
  ],
}: LobbyHostProps) {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const hostIP = "192.168.1.100:3000";

  const copyHostIP = () => {
    navigator.clipboard.writeText(hostIP);
    alert("IP copiado!");
  };

  const startGame = () => {
    alert("Iniciando partida...");
  };

  return (
    <section className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow p-6 max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* COLUNA 1 - LOBBY */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Lobby</h2>

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

        {/* COLUNA 2 — CONFIGURAÇÕES */}
        <div className="space-y-6 border-t md:border-l md:border-t-0 border-gray-300 pt-6 md:pt-0 md:pl-6">
          <h2 className="text-lg font-semibold mb-4">Configurações da Simulação</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Data Inicial</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full p-2 border rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Data Final</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full p-2 border rounded-md"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">IP do Host</label>
            <div className="flex">
              <input type="text" value={hostIP} readOnly className="flex-1 p-2 border rounded-l-md bg-white" />
              <button onClick={copyHostIP} className="bg-gray-200 hover:bg-gray-300 px-3 rounded-r-md">
                <FontAwesomeIcon icon={faCopy} />
              </button>
            </div>
          </div>

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
