import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCopy, faPlay } from "@fortawesome/free-solid-svg-icons";
import { useState } from "react";

interface LobbySimulationFormProps {
  onStart: (startDate: string, endDate: string) => void;
  loading?: boolean;
}

export function LobbySimulationForm({ onStart, loading = false }: LobbySimulationFormProps) {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const hostIP = window.location.host;

  const copyHostIP = () => {
    navigator.clipboard.writeText(hostIP);
  };

  const handleStart = () => {
    if (!startDate || !endDate) return;
    onStart(startDate, endDate);
  };

  return (
    <div className="space-y-6 border-t md:border-l md:border-t-0 border-gray-300 pt-6 md:pt-0 md:pl-6">
      <h2 className="text-lg font-semibold">Configurações da Simulação</h2>

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
          <input type="text" value={hostIP} readOnly className="flex-1 p-2 border rounded-l-md bg-gray-50" />
          <button onClick={copyHostIP} className="bg-gray-200 hover:bg-gray-300 px-3 rounded-r-md">
            <FontAwesomeIcon icon={faCopy} />
          </button>
        </div>
      </div>

      <button
        onClick={handleStart}
        disabled={loading}
        className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white py-3 px-4 rounded-md font-medium flex items-center justify-center gap-2"
      >
        <FontAwesomeIcon icon={faPlay} />
        Iniciar Partida
      </button>
    </div>
  );
}
