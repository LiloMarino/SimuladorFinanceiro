import clsx from "clsx";
import { useMutationApi } from "@/hooks/useMutationApi";
import { useRealtime } from "@/hooks/useRealtime";
import { useQueryApi } from "@/hooks/useQueryApi";

interface TopbarProps {
  pageLabel: string;
}

const SPEED_OPTIONS = [0, 1, 2, 4, 10];

export default function Topbar({ pageLabel }: TopbarProps) {
  // Estado inicial da simulação (tempo + velocidade)
  const { data: simData, setData: setSimData } = useQueryApi<{ currentDate?: string; speed?: number }>(
    "/api/get-simulation-state",
    { initialFetch: true }
  );

  // Atualiza quando o backend emite eventos realtime
  useRealtime("simulation_update", (update) => {
    setSimData((prev) => ({ ...prev, ...update }));
  });

  // Mutações de velocidade
  const { mutate: setSpeedApi, loading } = useMutationApi<{ speed: number }>("/api/set-speed", {
    onSuccess: (data) => {
      setSimData((prev) => ({ ...prev, speed: data.speed }));
      console.log("Velocidade atualizada:", data);
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
                  simData?.speed === option ? "bg-blue-700 text-white" : "bg-gray-200 text-gray-800 hover:bg-gray-300",
                  loading && "opacity-70 cursor-not-allowed"
                )}
              >
                {option === 0 ? "Pausar" : `${option}x`}
              </button>
            ))}
          </div>

          <div className="ml-4 flex items-center">
            <span className="text-sm text-gray-600 mr-2">Simulação:</span>
            <span className="font-medium">{simData?.currentDate ?? "--/--/----"}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
