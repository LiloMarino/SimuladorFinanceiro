import { Link } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import {
  displayDate,
  displayMoney,
  displayNumber,
  displaySignedPercent,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { OverviewReport, SimulationListItem } from "@/types";
import { displayCriterionGap } from "../../lib/criterion";
import { Podium } from "./podium";

type Player = OverviewReport["players"][number];

/** A frase do vencedor na unidade do critério; sem valor no critério, só a colocação. */
function headline(criterion: OverviewReport["criterion"], winner: Player) {
  const value = winner.criterion_value;
  const name = winner.player_nickname;
  if (value === null) return `${name} ficou em 1º`;
  switch (criterion) {
    case "SCORE":
      return `${name} venceu com ${displayNumber(value, 0)} pontos`;
    case "RETURN":
      return `${name} venceu com ${displaySignedPercent(value)} de retorno`;
    case "NETWORTH":
      return `${name} venceu com ${displayMoney(value)} de patrimônio`;
    case "SHARPE":
      return `${name} venceu com Sharpe ${displayNumber(value, 2)}`;
  }
}

interface MatchHeroProps {
  report: OverviewReport;
  simulation: SimulationListItem | undefined;
  currentPlayerName?: string;
  colorOf: (label: string) => string;
}

/** Topo do fim de partida: quem venceu, por qual critério, onde você ficou e o pódio. */
export function MatchHero({ report, simulation, currentPlayerName, colorOf }: MatchHeroProps) {
  const winner = report.players[0];
  const you = report.players.find((p) => p.player_nickname === currentPlayerName);
  const criterion = VICTORY_CRITERIA[report.criterion];
  const tradingDays = Math.max(...report.players.map((p) => p.days));
  const lastDay = simulation?.resume_from ?? simulation?.end_date;

  return (
    <section className="flex flex-wrap items-end justify-between gap-8 rounded-2xl bg-sidebar px-9 py-8 text-sidebar-foreground">
      <div className="grid max-w-[520px] gap-3.5">
        <span className="text-[11px] font-semibold tracking-[0.06em] text-sidebar-primary uppercase">
          Fim de partida · {winner.simulation_name}
        </span>
        <h1 className="text-[34px] leading-tight font-bold text-white">{headline(report.criterion, winner)}</h1>
        <p className="text-[15px]">
          Vitória por <b className="text-white">{criterion.label}</b>: {criterion.description}
          {you &&
            (you.position === 1 ? (
              <> Você venceu.</>
            ) : (
              <>
                {" "}
                Você ficou em <b className="text-white">{you.position}º</b>
                {you.leader_gap !== null && (
                  <>
                    , a <b className="font-mono text-white">{displayCriterionGap(report.criterion, you.leader_gap)}</b>{" "}
                    de {winner.player_nickname}
                  </>
                )}
                .
              </>
            ))}
        </p>
        <div className="flex flex-wrap gap-[18px] font-mono text-xs text-sidebar-muted">
          {simulation && lastDay && (
            <span>
              {displayDate(parseLocalDate(simulation.start_date))} → {displayDate(parseLocalDate(lastDay))}
            </span>
          )}
          <span>
            {report.players.length} {report.players.length === 1 ? "jogador" : "jogadores"}
          </span>
          <span>{tradingDays} pregões</span>
        </div>
        <div className="mt-1.5 flex flex-wrap gap-2">
          <Button nativeButton={false} render={<Link to="/lobby" />}>
            Voltar ao lobby
          </Button>
          <Button
            variant="inverse"
            nativeButton={false}
            render={<Link to={`/compare-simulations?ids=${winner.simulation_id}`} />}
          >
            Comparar com outras partidas
          </Button>
        </div>
      </div>
      <Podium report={report} currentPlayerName={currentPlayerName} colorOf={colorOf} />
    </section>
  );
}

/** Esqueleto do topo enquanto o resultado carrega. */
export function MatchHeroSkeleton() {
  return (
    <section className="grid h-60 content-start gap-3.5 rounded-2xl bg-sidebar p-8" aria-busy="true">
      <span className="h-3 w-40 animate-pulse rounded-md bg-sidebar-accent" />
      <span className="h-7 w-90 max-w-full animate-pulse rounded-md bg-sidebar-accent" />
      <span className="h-3 w-75 max-w-full animate-pulse rounded-md bg-sidebar-accent" />
    </section>
  );
}
