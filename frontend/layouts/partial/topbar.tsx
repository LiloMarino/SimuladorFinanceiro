import { useRef } from "react";
import { Pause, Play } from "lucide-react";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { useSetSimulationSpeed } from "@/shared/hooks/mutations/useSetSimulationSpeed";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { Button } from "@/shared/components/ui/button";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { displayShortDate } from "@/shared/lib/utils/display";
import { TopbarCash } from "./topbar-cash";
import { TopbarGoal } from "./topbar-goal";

interface TopbarProps {
  pageLabel: string;
}

const SPEED_OPTIONS = [1, 2, 4, 10, 100];

export default function Topbar({ pageLabel }: TopbarProps) {
  const { data: simData } = useSimulationState();
  const { simulation } = useSimulation();
  const match = simulation?.simulation;

  const { mutate: setSpeedApi, isPending: loading } = useSetSimulationSpeed();

  // Velocidade 0 é a pausa; o play retoma na última velocidade escolhida
  const lastSpeed = useRef(1);
  const speed = simData?.speed ?? 0;
  const paused = speed === 0;

  const handleSpeedChange = (newSpeed: number) => {
    if (newSpeed === speed) return;
    if (newSpeed > 0) lastSpeed.current = newSpeed;
    setSpeedApi(newSpeed);
  };

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-card">
      <div className="flex flex-wrap items-center justify-between gap-4 px-7 py-3">
        <h1 className="text-lg font-semibold">{pageLabel}</h1>

        <div className="flex flex-wrap items-center gap-3">
          {/* Corrida à meta */}
          {match && match.game_type !== "CLASSIC" && (
            <TopbarGoal
              grouping={match.player_grouping}
              teamNaming={match.team_naming}
              currentDate={simData?.current_date}
            />
          )}

          {/* Data, pausa e velocidade */}
          <div className="flex items-center gap-2 rounded-lg border border-border bg-subtle p-1">
            <span className="flex h-8 items-center px-3 font-mono text-[13px]">
              {simData?.current_date ? displayShortDate(simData.current_date) : "—"}
            </span>
            <Button
              variant="dark"
              size="icon-sm"
              disabled={loading}
              aria-label={paused ? "Retomar simulação" : "Pausar simulação"}
              onClick={() => handleSpeedChange(paused ? lastSpeed.current : 0)}
            >
              {paused ? <Play /> : <Pause />}
            </Button>
            <ToggleGroup
              variant="segmented"
              aria-label="Velocidade da simulação"
              value={paused ? [] : [String(speed)]}
              onValueChange={(values) => values[0] && handleSpeedChange(Number(values[0]))}
              disabled={loading}
            >
              {SPEED_OPTIONS.map((option) => (
                <ToggleGroupItem key={option} value={String(option)}>
                  {option}×
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </div>

          {/* Caixa */}
          <TopbarCash cash={simData?.cash} independence={match?.game_type === "FINANCIAL_INDEPENDENCE"} />
        </div>
      </div>
    </header>
  );
}
