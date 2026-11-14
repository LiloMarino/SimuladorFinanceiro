import { useEffect, useRef } from "react";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { TopbarCash } from "./topbar-cash";
import { TopbarTutorialButton } from "@/features/tutorial/components/topbar-button";
import { TopbarGoal } from "./topbar-goal";
import { TopbarTime } from "./topbar-time";
import { FundBanner } from "./fund-banner";
import { GoverningBanner } from "@/features/government/components/governing-banner";
import { TopbarGovernment } from "@/features/government/components/topbar-government";
import { NewsStrip } from "@/features/news/components/news-strip";
import { hasGoal } from "@/shared/lib/game-types";

interface TopbarProps {
  pageLabel: string;
}

export default function Topbar({ pageLabel }: TopbarProps) {
  const { data: simData } = useSimulationState();
  const { simulation } = useSimulation();
  const match = simulation?.simulation;

  // A altura do topo (que varia com a faixa de manchetes e o aviso) vira variável, para o que gruda sob ele
  const headerRef = useRef<HTMLElement>(null);
  useEffect(() => {
    const header = headerRef.current;
    if (!header) return;
    const root = document.documentElement;
    const publish = () => root.style.setProperty("--topbar-height", `${header.offsetHeight}px`);
    publish();
    const observer = new ResizeObserver(publish);
    observer.observe(header);
    return () => {
      observer.disconnect();
      root.style.removeProperty("--topbar-height");
    };
  }, []);

  return (
    <header ref={headerRef} className="sticky top-0 z-30 border-b border-border bg-card">
      <div className="flex flex-wrap items-center justify-between gap-4 px-7 py-3">
        <h1 className="min-w-0 truncate text-lg font-semibold">{pageLabel}</h1>

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

          {/* Como jogar */}
          <TopbarTutorialButton />

          {/* Data, pausa e velocidade */}
          <TopbarTime />

          {/* Caixa */}
          <TopbarCash cash={simData?.cash} independence={match?.game_type === "FINANCIAL_INDEPENDENCE"} />
        </div>
      </div>

      {/* Faixa da gestora */}
      {match?.funds_enabled && <FundBanner />}

      {/* Faixa de manchetes */}
      <NewsStrip />

      {/* Aviso do presidente */}
      {match?.government_enabled && <GoverningBanner />}
    </header>
  );
}
