import clsx from "clsx";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import type { SimulationState } from "@/types";
import { formatMoney } from "@/shared/lib/utils/formatting";

interface TopbarProps {
  pageLabel: string;
}

const SPEED_OPTIONS = [0, 1, 2, 4, 10, 100];

export default function Topbar({ pageLabel }: TopbarProps) {
  const { data: simData, setData: setSimData } = useQueryApi<SimulationState>("/api/get-simulation-state");

  // Realtime updates
  useRealtime("simulation_update", (update) => {
    setSimData((prev) => ({ ...prev, ...update }));
  });

  useRealtime("speed_update", (update) => {
    setSimData((prev) => ({ ...prev, ...update }));
  });

  useRealtime("cash_update", (update) => {
    setSimData((prev) => ({ ...prev, ...update }));
  });

  // Mutações para alterar velocidade
  const { mutate: setSpeedApi, loading } = useMutationApi<{ speed: number }>("/api/set-speed", {
    onSuccess: (data) => {
      setSimData((prev) => ({ ...prev, speed: data.speed }));
    },
    onError: (err) => {
      console.error("Erro ao alterar velocidade:", err);
    },
  });

  const handleSpeedChange = (newSpeed: number) => {
    if (newSpeed === simData?.speed) return;
    setSpeedApi({ speed: newSpeed });
  };

  return (
    <header className="bg-white shadow-sm">
      <div className="flex flex-wrap items-center justify-between p-4 gap-4">
        <h1 className="text-xl font-semibold text-gray-800">{pageLabel}</h1>

        <div className="flex items-center space-x-6">
          {/* Saldo */}
          <div className="flex items-center">
            <span className="text-sm text-gray-600 mr-2">Saldo:</span>
            <span className="font-medium">{simData?.cash !== undefined ? formatMoney(simData.cash) : "--"}</span>
          </div>

          {/* Velocidade */}
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
                    simData?.speed === option
                      ? "bg-blue-700 text-white"
                      : "bg-gray-200 text-gray-800 hover:bg-gray-300",
                    loading && "opacity-70 cursor-not-allowed"
                  )}
                >
                  {option === 0 ? "Pausar" : `${option}x`}
                </button>
              ))}
            </div>
          </div>

          {/* Data */}
          <div className="flex items-center">
            <span className="text-sm text-gray-600 mr-2">Simulação:</span>
            <span className="font-medium">{simData?.currentDate ?? "--/--/----"}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
