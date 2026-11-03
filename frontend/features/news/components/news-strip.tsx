import { Link } from "react-router-dom";
import { useNotificationCatalog } from "@/shared/hooks/queries/useNotificationCatalog";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { News } from "@/types";
import { useNewsMonth } from "../hooks/queries/useNewsMonth";
import { useNewsPresenter } from "../hooks/useNewsPresenter";
import { type Month, monthOf } from "../lib/months";
import { NewsKicker } from "./news-parts";

/**
 * A faixa de manchetes sob a topbar, para quem escolheu essa posição. Com manchete nova, mostra
 * a do pregão; passado o tempo do cartão, a faixa fica com a última, apagada.
 */
export function NewsStrip() {
  const { position, state } = useNewsPresenter();
  const { simulation } = useSimulation();
  const { data: simulationState } = useSimulationState();
  const simulationId = simulation?.simulation?.id;
  if (position !== "STRIP" || simulationId === undefined || !simulationState?.current_date) return null;

  return (
    <Strip
      simulationId={simulationId}
      month={monthOf(simulationState.current_date)}
      live={state.expanded ? state.lead?.news : undefined}
      others={state.count - 1}
    />
  );
}

type StripProps = {
  simulationId: number;
  /** O mês da partida: a faixa mostra a última manchete dele */
  month: Month;
  /** A manchete nova do pregão, enquanto ela é novidade */
  live: News | undefined;
  others: number;
};

function Strip({ simulationId, month, live, others }: StripProps) {
  const { data: items } = useNewsMonth(simulationId, month);
  const { data: catalog } = useNotificationCatalog();
  const { preferences } = useNotificationPreferences();

  // A última manchete que o jogador deixou aparecer: janela e jornal
  const latest = items?.find((item) => {
    const level = preferences?.news[item.news_type];
    return level === "WINDOW" || level === "JOURNAL";
  });
  const shown = live ?? latest;

  return (
    <div className="flex h-10 items-center gap-3.5 border-t border-paper-border bg-paper px-7">
      <b className="border-r-[3px] border-double border-foreground pr-3.5 font-serif lining-nums text-sm whitespace-nowrap">
        Diário do Pregão
      </b>
      {shown && catalog ? (
        <>
          <NewsKicker type={shown.news_type} />
          <span
            className={cn(
              "min-w-0 flex-1 truncate font-serif lining-nums text-sm",
              live ? "font-semibold" : "text-muted-foreground",
            )}
          >
            {live ? shown.headline : `${displayDayMonth(shown.news_date)}: ${shown.headline}`}
          </span>
        </>
      ) : (
        <span className="min-w-0 flex-1 truncate font-serif lining-nums text-sm text-muted-foreground">
          Sem manchetes ainda
        </span>
      )}
      {live && others > 0 && (
        <span className="text-xs whitespace-nowrap text-muted-foreground">+{others} neste pregão</span>
      )}
      <Link to="/journal" className="text-xs font-semibold whitespace-nowrap text-primary hover:text-primary-hover">
        Abrir o jornal ›
      </Link>
    </div>
  );
}
