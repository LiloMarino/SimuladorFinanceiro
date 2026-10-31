import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useElection } from "@/shared/hooks/queries/useElection";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import type { SimulationState } from "@/types";
import { RoundResultDialog } from "./round-result-dialog";

/** O turno que cada pausa por resultado espera o jogador ver. */
const ROUND_BY_PAUSE: Partial<Record<NonNullable<SimulationState["pause_reason"]>, number>> = {
  FIRST_ROUND_RESULT: 1,
  RUNOFF_RESULT: 2,
};

/**
 * O resultado do turno abre em qualquer tela enquanto a partida estiver pausada por ele,
 * inclusive depois de recarregar; fechado, não volta até o próximo turno.
 */
export function PausedRoundResult() {
  const navigate = useNavigate();
  const { data: state } = useSimulationState();
  const { data: panel } = useElection();
  const [dismissed, setDismissed] = useState<string | null>(null);

  const result = panel?.last_result ?? null;
  const awaited = state?.pause_reason ? ROUND_BY_PAUSE[state.pause_reason] : undefined;
  const key = result ? `${result.round}:${result.date}` : null;
  const open = result !== null && result.round === awaited && key !== dismissed;

  return (
    <RoundResultDialog
      result={open ? result : null}
      panel={panel}
      onClose={() => setDismissed(key)}
      onOpenPage={() => {
        setDismissed(key);
        void navigate("/election");
      }}
    />
  );
}
