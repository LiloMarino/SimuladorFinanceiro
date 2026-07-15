import clsx from "clsx";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { displayMoney } from "@/shared/lib/utils/display";

interface TopbarProps {
  pageLabel: string;
}

const SPEED_OPTIONS = [0, 1, 2, 4, 10, 100];

export default function Topbar({ pageLabel }: TopbarProps) {
  const { data: simData } = useSimulationState();

  // Mutação para alterar velocidade — não escreve o cache diretamente: quem
  // atualiza `speed` é o evento WS speed_update, via useSimulationState().
  const { mutate: setSpeedApi, isPending: loading } = useApiMutation({
    mutationFn: (speed: number) => apiFetch<{ speed: number }>("/api/set-speed", { method: "POST", body: { speed } }),
    onError: (err) => {
      console.error("Erro ao alterar velocidade:", err);
    },
  });

  const handleSpeedChange = (newSpeed: number) => {
    if (newSpeed === simData?.speed) return;
    setSpeedApi(newSpeed);
  };

  return (
    <header className="sticky top-0 z-30 bg-background border-b border-border shadow-sm">
      <div className="flex flex-wrap items-center justify-between p-4 gap-4">
        <h1 className="text-xl font-semibold text-foreground">{pageLabel}</h1>

        <div className="flex items-center space-x-6">
          {/* Saldo */}
          <div className="flex items-center">
            <span className="text-sm text-muted-foreground mr-2">Saldo:</span>
            <span className="font-medium">{simData?.cash !== undefined ? displayMoney(simData.cash) : "--"}</span>
          </div>

          {/* Velocidade */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-muted-foreground hidden md:block">Velocidade:</span>

            <div className="flex divide-x divide-border rounded-md overflow-hidden border border-border">
              {SPEED_OPTIONS.map((option) => (
                <button
                  key={option}
                  onClick={() => handleSpeedChange(option)}
                  disabled={loading}
                  className={clsx(
                    "px-3 py-1 text-sm transition-colors duration-200",
                    simData?.speed === option
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                    loading && "opacity-70 cursor-not-allowed",
                  )}
                >
                  {option === 0 ? "Pausar" : `${option}x`}
                </button>
              ))}
            </div>
          </div>

          {/* Data */}
          <div className="flex items-center">
            <span className="text-sm text-muted-foreground mr-2">Simulação:</span>
            <span className="font-medium">{simData?.current_date ?? "--/--/----"}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
