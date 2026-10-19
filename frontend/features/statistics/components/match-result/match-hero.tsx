import { Link } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { teamName, teamShortName } from "@/shared/lib/teams";
import {
  displayDate,
  displayMoney,
  displayNumber,
  displaySignedPercent,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { OverviewReport, SimulationListItem } from "@/types";
import { displayCriterionGap, displayCriterionValue } from "../../lib/criterion";
import { Podium } from "./podium";
import { TeamPodium } from "./team-podium";

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

/** A frase da equipe vencedora; empate na média vai para o patrimônio médio. */
function teamHeadline(report: OverviewReport) {
  const [first, second] = report.teams;
  const name = teamName(first.team, report.team_naming);
  const value = first.criterion_value;
  if (value === null) return `${name} ficou em 1ª`;
  if (second && second.criterion_value !== null && Number(second.criterion_value) === Number(value)) {
    return `${name} venceu no desempate`;
  }
  switch (report.criterion) {
    case "SCORE":
      return `${name} venceu com ${displayNumber(value, 0)} pontos de média`;
    case "RETURN":
      return `${name} venceu com ${displaySignedPercent(value)} de retorno médio`;
    case "NETWORTH":
      return `${name} venceu com ${displayMoney(value)} de patrimônio médio`;
    case "SHARPE":
      return `${name} venceu com Sharpe médio ${displayNumber(value, 2)}`;
  }
}

/** O que a frase do topo diz da sua equipe, do empate e de quem ficou fora da média. */
function TeamSummary({ report, currentPlayerName }: { report: OverviewReport; currentPlayerName?: string }) {
  const { teams, criterion, team_naming: naming } = report;
  const [first, second] = teams;
  const you = report.players.find((p) => p.player_nickname === currentPlayerName);
  const mine = teams.find((t) => t.team === you?.team);
  const tie =
    second && first.criterion_value !== null && second.criterion_value !== null &&
    Number(first.criterion_value) === Number(second.criterion_value);
  const partial = teams.find((t) => t.measured_members < t.members);

  return (
    <>
      {tie && (
        <>
          {" "}
          As duas fecharam com <b className="font-mono text-white">{displayCriterionValue(criterion, first.criterion_value)}</b>{" "}
          de média. Desempata o patrimônio médio:{" "}
          <b className="font-mono text-white">{displayMoney(first.total_networth)}</b> contra{" "}
          <b className="font-mono text-white">{displayMoney(second.total_networth)}</b>.
        </>
      )}
      {mine &&
        !tie &&
        (mine.position === 1 ? (
          <>
            {" "}
            Sua equipe venceu
            {second && second.leader_gap !== null && (
              <>
                ,{" "}
                <b className="font-mono text-white">{displayCriterionGap(criterion, second.leader_gap)}</b> à frente da{" "}
                {teamName(second.team, naming)}
              </>
            )}
            .
          </>
        ) : (
          <>
            {" "}
            Sua equipe ficou em <b className="text-white">{mine.position}º</b>
            {mine.leader_gap !== null && (
              <>
                , a <b className="font-mono text-white">{displayCriterionGap(criterion, mine.leader_gap)}</b>
              </>
            )}
            .
            {mine.top_puller && mine.top_puller.player_nickname === currentPlayerName && (
              <>
                {" "}
                Você foi quem mais puxou a {teamShortName(mine.team, naming)} para cima:{" "}
                <b className="font-mono text-white">+{displayCriterionGap(criterion, mine.top_puller.contribution)}</b> na
                média.
              </>
            )}
          </>
        ))}
      {partial && (
        <>
          {" "}
          Na {teamName(partial.team, naming)} a média usa quem tem valor ({partial.measured_members} de {partial.members}).
        </>
      )}
    </>
  );
}

interface MatchHeroProps {
  report: OverviewReport;
  simulation: SimulationListItem | undefined;
  currentPlayerName?: string;
}

/** Topo do fim de partida: quem venceu, por qual critério, onde você ficou e o pódio. */
export function MatchHero({ report, simulation, currentPlayerName }: MatchHeroProps) {
  const winner = report.players[0];
  const inTeams = report.teams.length > 0;
  const you = report.players.find((p) => p.player_nickname === currentPlayerName);
  const criterion = VICTORY_CRITERIA[report.criterion];
  const tradingDays = Math.max(...report.players.map((p) => p.days));
  const lastDay = simulation?.resume_from ?? simulation?.end_date;

  return (
    <section className="flex flex-wrap items-end justify-between gap-8 rounded-2xl bg-sidebar px-9 py-8 text-sidebar-foreground">
      <div className="grid max-w-[520px] gap-3.5">
        <span className="text-[11px] font-semibold tracking-[0.06em] text-sidebar-primary uppercase">
          Fim de partida · {winner.simulation_name}
          {inTeams && " · em equipes"}
        </span>
        <h1 className="text-[34px] leading-tight font-bold text-white">
          {inTeams ? teamHeadline(report) : headline(report.criterion, winner)}
        </h1>
        <p className="text-[15px]">
          {inTeams ? (
            <>
              Vitória por <b className="text-white">{criterion.label}</b>, em equipes: vale a média dos membros.
              <TeamSummary report={report} currentPlayerName={currentPlayerName} />
            </>
          ) : (
            <>
              Vitória por <b className="text-white">{criterion.label}</b>: {criterion.description}
            </>
          )}
          {!inTeams &&
            you &&
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
            {inTeams && ` · ${report.teams.length} equipes`}
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
      {inTeams ? <TeamPodium report={report} /> : <Podium report={report} currentPlayerName={currentPlayerName} />}
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
