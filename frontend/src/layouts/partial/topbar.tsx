import { useState } from "react";
import clsx from "clsx";
import { useMutationApi } from "@/hooks/useMutationApi";

interface TopbarProps {
  pageLabel: string;
  simulationTime: string;
}

const SPEED_OPTIONS = [0, 1, 2, 4, 10];

export default function Topbar({ pageLabel, simulationTime }: TopbarProps) {
  const [speed, setSpeed] = useState(0);

  // Mutation para alterar a velocidade via REST API
  const { mutate: setSpeedApi, loading } = useMutationApi<{ speed: number }>("/api/set-speed", {
    onSuccess: (data) => {
      // Atualiza o estado local com a velocidade confirmada pelo servidor
      setSpeed(data.speed);
      console.log("Velocidade atualizada no servidor:", data.speed);
    },
    onError: (err) => {
      console.error("Erro ao alterar velocidade:", err);
    },
  });

  const handleSpeedChange = (newSpeed: number) => {
    // Evita enviar requisição duplicada
    if (newSpeed === speed) return;

    // Chama a mutation
    setSpeedApi({ speed: newSpeed });
  };

  return (
    <header className="bg-white shadow-sm">
      <div className="flex items-center justify-between p-4">
        <h1 className="text-xl font-semibold text-gray-800">{pageLabel}</h1>

        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600 hidden md:block">Velocidade:</span>

          <div className="flex divide-x divide-gray-300 rounded-md overflow-hidden">
            {SPEED_OPTIONS.map((option) => (
              <button
                key={option}
                onClick={() => handleSpeedChange(option)}
                disabled={loading}
                className={clsx(
                  "px-3 py-1 text-sm transition-colors duration-200",
                  speed === option ? "bg-blue-700 text-white" : "bg-gray-200 text-gray-800 hover:bg-gray-300",
                  loading && "opacity-70 cursor-not-allowed"
                )}
              >
                {option === 0 ? "Pausar" : `${option}x`}
              </button>
            ))}
          </div>

          <div className="ml-4 flex items-center">
            <span className="text-sm text-gray-600 mr-2">Simulação:</span>
            <span className="font-medium">{simulationTime}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
