import { differenceInCalendarDays } from "date-fns";
import { InfoHint } from "@/shared/components/info-hint";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { useStatisticsNextUpdate } from "@/shared/hooks/queries/useStatisticsNextUpdate";
import { displayIsoDate, parseLocalDate } from "@/shared/lib/utils/display";

/** Avisa que as estatísticas fecham uma vez por mês de jogo: o dia da última atualização e, com a partida andando, quantos dias faltam para a próxima. */
export function UpdateNotice() {
  const { data: nextUpdate } = useStatisticsNextUpdate();
  const { data: state } = useSimulationState();

  if (!state?.current_date || !nextUpdate) return null;

  // Pausada, o relógio da partida não anda: não há contagem a mostrar
  const running = (state.speed ?? 0) > 0;
  const days = nextUpdate.next_update_date
    ? differenceInCalendarDays(parseLocalDate(nextUpdate.next_update_date), parseLocalDate(state.current_date))
    : null;

  return (
    <p className="flex items-center gap-1 text-sm text-muted-foreground">
      Atualizadas uma vez por mês de jogo
      {nextUpdate.last_update_date && ` · última atualização em ${displayIsoDate(nextUpdate.last_update_date)}`}
      {running && days !== null && ` · próxima atualização em ${days} ${days === 1 ? "dia" : "dias"}`}
      <InfoHint label="Por que as estatísticas atualizam por mês">
        <div className="space-y-1 text-left">
          <p>
            Risco e nota são calculados sobre uma série de retornos mensais, então os números só fecham na virada do mês
            da partida.
          </p>
          <p>Os dias contados são dias da partida, não do relógio: com a partida pausada, a contagem não anda.</p>
        </div>
      </InfoHint>
    </p>
  );
}
