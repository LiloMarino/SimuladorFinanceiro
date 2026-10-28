import { useEffect, useRef } from "react";
import { Pause, Play, Zap } from "lucide-react";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { useSetSimulationSpeed } from "@/shared/hooks/mutations/useSetSimulationSpeed";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { cn } from "@/shared/lib/utils";
import { displayShortDate } from "@/shared/lib/utils/display";
import { TopbarCash } from "./topbar-cash";
import { TopbarTutorialButton } from "@/features/tutorial/components/topbar-button";
import { TopbarGoal } from "./topbar-goal";
import { GoverningBanner } from "@/features/government/components/governing-banner";
import { TopbarGovernment } from "@/features/government/components/topbar-government";
import { TopbarInbox } from "@/features/inbox/components/topbar-inbox";
import { hasGoal } from "@/shared/lib/game-types";
import type { SimulationState } from "@/types";

interface TopbarProps {
  pageLabel: string;
}

const SPEED_OPTIONS = [1, 2, 4, 10, 100];
const MAX_SPEED = 100;

const PAUSE_REASON_LABELS: Record<NonNullable<SimulationState["pause_reason"]>, string> = {
  HOST: "Pausado",
  CAMPAIGN_OPENED: "Pausado: campanha aberta",
  FIRST_ROUND_RESULT: "Pausado: resultado do 1º turno",
  RUNOFF_RESULT: "Pausado: resultado do 2º turno",
  IMPEACHMENT: "Pausado: impeachment",
};

export default function Topbar({ pageLabel }: TopbarProps) {
  const { data: simData } = useSimulationState();
  const { simulation } = useSimulation();
  const match = simulation?.simulation;

  const { mutate: setSpeedApi, isPending: loading } = useSetSimulationSpeed();

  // Velocidade 0 é a pausa; o play retoma na última velocidade escolhida
  const lastSpeed = useRef(1);
  const speed = simData?.speed ?? 0;
  const paused = speed === 0;
  const maxSpeed = speed === MAX_SPEED;
  const pauseLabel = PAUSE_REASON_LABELS[simData?.pause_reason ?? "HOST"];

  // A aba do navegador avisa a pausa para quem está em outra aba
  useEffect(() => {
    if (!paused) return;
    const title = document.title;
    document.title = `⏸ ${title}`;
    return () => {
      document.title = title;
    };
  }, [paused]);

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
          {match && hasGoal(match.game_type) && (
            <TopbarGoal
              grouping={match.player_grouping}
              teamNaming={match.team_naming}
              currentDate={simData?.current_date}
            />
          )}

          {/* Expansão Governo & Política */}
          {match?.government_enabled && <TopbarGovernment />}

          {/* Caixa de entrada */}
          {match && <TopbarInbox simulationId={match.id} />}

          {/* Como jogar */}
          <TopbarTutorialButton />

          {/* Data, pausa e velocidade */}
          <div className="flex items-center gap-2 rounded-lg border border-border bg-subtle p-1">
            {paused && (
              <Badge variant="warning" size="status" pulse role="status">
                <Pause />
                {pauseLabel}
              </Badge>
            )}
            <span
              className={cn(
                "flex h-8 items-center rounded-md px-3 font-mono text-[13px]",
                maxSpeed && "bg-info-soft text-info",
              )}
            >
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
                <ToggleGroupItem key={option} value={String(option)} tone={option === MAX_SPEED ? "max" : undefined}>
                  {option === MAX_SPEED && <Zap />}
                  {option}×
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </div>

          {/* Caixa */}
          <TopbarCash cash={simData?.cash} independence={match?.game_type === "FINANCIAL_INDEPENDENCE"} />
        </div>
      </div>

      {/* Aviso do presidente */}
      {match?.government_enabled && <GoverningBanner />}
    </header>
  );
}
