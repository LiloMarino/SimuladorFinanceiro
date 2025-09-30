import { useState } from "react";
import clsx from "clsx";

interface TopbarProps {
  pageLabel: string;
  simulationTime: string;
}

const SPEED_OPTIONS = [0, 1, 2, 4, 10];

export default function Topbar({ pageLabel, simulationTime }: TopbarProps) {
  const [speed, setSpeed] = useState(0);

  const handleSpeedChange = (newSpeed: number) => {
    setSpeed(newSpeed);
    console.log("Velocidade selecionada:", newSpeed);

    // Aqui você pode adicionar fetch ou socket
    // fetch("/api/set_speed", { ... })
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
                className={clsx(
                  "px-3 py-1 text-sm transition-colors duration-200",
                  speed === option
                    ? "bg-blue-700 text-white"
                    : "bg-gray-200 text-gray-800 hover:bg-gray-300"
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
