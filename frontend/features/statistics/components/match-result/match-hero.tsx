import { Link } from "react-router-dom";
import { Flag } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { teamName, teamShortName } from "@/shared/lib/teams";
import {
  displayDate,
  displayMoney,
  displayMoneyCompact,
  displayNumber,
  displaySignedPercent,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import { displayAnnualMultiple, displayRatePercent, unexpectedLabel } from "@/shared/lib/financial-independence";
import { displayGoalPercent } from "@/shared/lib/goal";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { OverviewReport, SimulationListItem } from "@/types";
import {
  displayCriterionContribution,
  displayCriterionGap,
  displayCriterionValue,
  rankingMeasure,
} from "../../lib/criterion";
import { Podium } from "./podium";
import { TeamPodium } from "./team-podium";

type Player = OverviewReport["players"][number];

/** A meta foi atingida quando a fração da meta do líder chega a 1. */
const reachedGoal = (fraction: string | null) => fraction !== null && Number(fraction) >= 1;

/** A frase do vencedor na unidade do critério; sem valor no critério, só a colocação. */
function headline(report: OverviewReport, winner: Player) {
  const value = winner.criterion_value;
  const name = winner.player_nickname;
  if (value === null) return `${name} ficou em 1º`;
  switch (rankingMeasure(report)) {
    case "GOAL":
      if (report.game_type === "FINANCIAL_INDEPENDENCE") {
        return reachedGoal(value)
          ? `${name} conquistou a independência financeira`
          : `Ninguém chegou à independência financeira; ${name} ficou mais perto`;
      }
      return reachedGoal(value) ? `${name} chegou primeiro à meta` : `Ninguém chegou à meta; ${name} ficou mais perto`;
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
  switch (rankingMeasure(report)) {
    case "GOAL":
      if (report.game_type === "FINANCIAL_INDEPENDENCE") {
        return reachedGoal(value)
          ? `${name} conquistou a independência financeira`
          : `Nenhuma equipe chegou à independência financeira; ${name} ficou mais perto`;
      }
      return reachedGoal(value)
        ? `${name} chegou primeiro à meta`
        : `Nenhuma equipe chegou à meta; ${name} ficou mais perto`;
    case "SCORE":
      // Equipe de uma pessoa vale a nota dela: não há média a dizer
      return first.members === 1
        ? `${name} venceu com ${displayNumber(value, 0)} pontos`
        : `${name} venceu com ${displayNumber(value, 0)} pontos de média`;
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
  const { teams, team_naming: naming, goal_net_worth } = report;
  const criterion = rankingMeasure(report);
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
                <b className="font-mono text-white">{displayCriterionGap(criterion, second.leader_gap, goal_net_worth)}</b> à frente da{" "}
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
                , a <b className="font-mono text-white">{displayCriterionGap(criterion, mine.leader_gap, goal_net_worth)}</b>
              </>
            )}
            .
            {mine.top_puller && mine.top_puller.player_nickname === currentPlayerName && (
              <>
                {" "}
                Você foi quem mais puxou a {teamShortName(mine.team, naming)} para cima:{" "}
                <b className="font-mono text-white">
                  {displayCriterionContribution(criterion, mine.top_puller.contribution)}
                </b>{" "}
                na
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

/** Pluraliza "N anos", "N meses" ou "N dias" para a antecedência do fim da partida. */
function displayLeadTime(days: number) {
  if (days >= 365) {
    const years = Math.floor(days / 365);
    return `${years} ${years === 1 ? "ano" : "anos"}`;
  }
  if (days >= 30) {
    const months = Math.floor(days / 30);
    return `${months} ${months === 1 ? "mês" : "meses"}`;
  }
  return `${days} ${days === 1 ? "dia" : "dias"}`;
}

/** As regras da vida real da partida em uma linha: "Imprevistos normais · IPCA ligado". */
function displayLifeRules(simulation: SimulationListItem) {
  const unexpected =
    simulation.unexpected_per_year === 0
      ? "Sem imprevistos"
      : `Imprevistos ${unexpectedLabel(simulation.unexpected_per_year).toLowerCase()}`;
  return `${unexpected} · IPCA ${simulation.inflation_adjusted ? "ligado" : "desligado"}`;
}

/** O que a frase do topo diz da corrida: quando e com quanto alguém chegou, ou quem ficou mais perto. */
function GoalSummary({
  report,
  simulation,
  reached,
  currentPlayerName,
}: {
  report: OverviewReport;
  simulation: SimulationListItem | undefined;
  reached: boolean;
  currentPlayerName?: string;
}) {
  const { goal_net_worth: goal, teams } = report;
  const inTeams = teams.length > 0;
  const leader = inTeams ? teams[0] : report.players[0];
  const you = report.players.find((p) => p.player_nickname === currentPlayerName);
  const yourRank = inTeams ? teams.find((t) => t.team === you?.team) : you;
  const lastDay = simulation?.resume_from ?? simulation?.end_date;
  const daysEarly =
    simulation && lastDay
      ? Math.round((parseLocalDate(simulation.end_date).getTime() - parseLocalDate(lastDay).getTime()) / 86_400_000)
      : 0;
  const goalText = goal ? ` (meta ${displayMoneyCompact(goal)})` : "";
  const independence = report.game_type === "FINANCIAL_INDEPENDENCE";
  const leaderName = "player_nickname" in leader ? leader.player_nickname : teamName(leader.team, report.team_naming);

  return (
    <>
      {reached ? (
        <>
          {lastDay && (
            <>
              Em <b className="font-mono text-white">{displayDate(parseLocalDate(lastDay))}</b>,{" "}
            </>
          )}
          {independence && simulation ? (
            <>
              {inTeams ? "a média do patrimônio da" : "o patrimônio de"} <b className="text-white">{leaderName}</b>{" "}
              chegou a <b className="text-white">{displayAnnualMultiple(Number(simulation.withdrawal_rate))}</b> a despesa
              anual: retirando {displayRatePercent(simulation.withdrawal_rate)} ao ano, dá para viver de renda.
            </>
          ) : (
            <>
              com <b className="font-mono text-white">{displayMoney(leader.total_networth)}</b>{" "}
              de {inTeams ? "patrimônio médio" : "patrimônio"}
              {goalText}.
            </>
          )}
          {daysEarly > 0 && <> A partida terminou nesse dia, {displayLeadTime(daysEarly)} antes da data final.</>}
        </>
      ) : (
        <>
          Chegou a data final com <b className="text-white">{leaderName}</b> em{" "}
          <b className="font-mono text-white">{displayCriterionValue("GOAL", leader.criterion_value)}</b> da{" "}
          {independence ? "independência" : "meta"}
          {goal ? <> de {displayMoneyCompact(goal)}</> : null}: quem fica mais perto vence.
        </>
      )}
      {yourRank &&
        (yourRank.position === 1 ? (
          <> Você venceu.</>
        ) : (
          <>
            {" "}
            Você ficou em <b className="text-white">{yourRank.position}º</b>, com{" "}
            <b className="font-mono text-white">{displayGoalPercentOf(yourRank.criterion_value)}</b> da meta.
          </>
        ))}
    </>
  );
}

const displayGoalPercentOf = (fraction: string | null) => (fraction === null ? "—" : displayGoalPercent(Number(fraction)));

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
  const measure = rankingMeasure(report);
  const criterion = measure === "GOAL" ? null : VICTORY_CRITERIA[measure];
  const reached = measure === "GOAL" && reachedGoal((inTeams ? report.teams[0] : winner).criterion_value);
  const tradingDays = Math.max(...report.players.map((p) => p.days));
  const lastDay = simulation?.resume_from ?? simulation?.end_date;

  return (
    <section className="flex flex-wrap items-end justify-between gap-8 rounded-2xl bg-sidebar px-9 py-8 text-sidebar-foreground">
      <div className="grid max-w-[520px] gap-3.5">
        <span className="text-[11px] font-semibold tracking-[0.06em] text-sidebar-primary uppercase">
          Fim de partida · {winner.simulation_name}
          {inTeams && " · em equipes"}
        </span>
        <h1 className="flex items-center gap-3 text-[34px] leading-tight font-bold text-white">
          {reached && <Flag className="size-7 shrink-0 text-trophy" />}
          {inTeams ? teamHeadline(report) : headline(report, winner)}
        </h1>
        <p className="text-[15px]">
          {measure === "GOAL" ? (
            <GoalSummary report={report} simulation={simulation} reached={reached} currentPlayerName={currentPlayerName} />
          ) : inTeams ? (
            <>
              Vitória por <b className="text-white">{criterion?.label}</b>, em equipes: vale a média dos membros.
              <TeamSummary report={report} currentPlayerName={currentPlayerName} />
            </>
          ) : (
            <>
              Vitória por <b className="text-white">{criterion?.label}</b>: {criterion?.description}
            </>
          )}
          {!inTeams &&
            measure !== "GOAL" &&
            you &&
            (you.position === 1 ? (
              <> Você venceu.</>
            ) : (
              <>
                {" "}
                Você ficou em <b className="text-white">{you.position}º</b>
                {you.leader_gap !== null && (
                  <>
                    , a <b className="font-mono text-white">{displayCriterionGap(measure, you.leader_gap)}</b> de{" "}
                    {winner.player_nickname}
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
          <span>
            {report.game_type === "FINANCIAL_INDEPENDENCE" && simulation
              ? displayLifeRules(simulation)
              : `${tradingDays} pregões`}
          </span>
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
