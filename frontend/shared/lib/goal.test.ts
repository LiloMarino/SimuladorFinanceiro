import { describe, expect, it } from "vitest";
import type { GoalProgress, PortfolioHistoryPoint } from "@/types";
import {
  displayGoalPercent,
  displayProjectionDistance,
  goalAt,
  goalFraction,
  goalPercent,
  ownStanding,
  playerStandings,
  projectGoalDate,
  remainingToGoal,
  teamStandings,
} from "./goal";

const progress: GoalProgress = {
  goal: "200000",
  players: [
    { nickname: "Ana", color: "blue", team: 1, networth: "120000" },
    { nickname: "Bia", color: "red", team: 1, networth: "80000" },
    { nickname: "Caio", color: "green", team: 2, networth: "150000" },
    { nickname: "Duda", color: "pink", team: null, networth: "200000" },
  ],
};

const point = (snapshot_date: string, total_networth: string): PortfolioHistoryPoint => ({
  snapshot_date,
  total_networth,
  total_equity: "0",
  total_fixed: "0",
  total_cash: total_networth,
  total_contribution: "0",
  total_debt: "0",
  total_provided: "0",
});

describe("fração e restante até a meta", () => {
  it("calcula a fração e o percentual truncado", () => {
    expect(goalFraction("50000", "100000")).toBe(0.5);
    expect(displayGoalPercent(0.5)).toBe("50%");
    expect(goalPercent(0.9996)).toBe(99);
    // 0,29 × 100 dá 28,999…: o percentual mostrado continua 29
    expect(goalPercent(0.29)).toBe(29);
  });

  it("patrimônio zero está a 0% e falta a meta inteira", () => {
    expect(goalFraction(0, 100000)).toBe(0);
    expect(remainingToGoal(0, 100000)).toBe(100000);
  });

  it("meta já batida não deixa restante negativo", () => {
    expect(remainingToGoal("50000", "100000")).toBe(50000);
    expect(remainingToGoal("130000", "100000")).toBe(0);
  });
});

describe("classificação de jogadores e equipes", () => {
  it("ordena os jogadores pela fração da meta", () => {
    const standings = playerStandings(progress);
    expect(standings.map((s) => s.nickname)).toEqual(["Duda", "Caio", "Ana", "Bia"]);
    expect(standings.map((s) => s.fraction)).toEqual([1, 0.75, 0.6, 0.4]);
  });

  it("a equipe vale a média dos membros e quem não tem equipe fica de fora", () => {
    const teams = teamStandings(progress);
    // Equipe 1: (120.000 + 80.000) / 2 = 100.000, metade da meta
    expect(teams.map((t) => [t.team, t.networth, t.fraction])).toEqual([
      [2, 150000, 0.75],
      [1, 100000, 0.5],
    ]);
    expect(teams[1]?.members.map((m) => m.nickname)).toEqual(["Ana", "Bia"]);
  });

  it("acha a posição do próprio jogador ou da equipe dele", () => {
    expect(ownStanding(progress, "INDIVIDUAL", "Caio")).toMatchObject({ nickname: "Caio", fraction: 0.75 });
    expect(ownStanding(progress, "TEAMS", "Bia")).toMatchObject({ team: 1, networth: 100000 });
    expect(ownStanding(progress, "TEAMS", "Duda")).toBeUndefined();
    expect(ownStanding(progress, "INDIVIDUAL", "Zeca")).toBeUndefined();
  });
});

describe("meta em degraus", () => {
  const steps = [
    { date: "2020-01-01", value: "100" },
    { date: "2021-01-01", value: "200" },
  ];

  it("vale o degrau mais recente até a data", () => {
    expect(goalAt(steps, "2020-06-01")).toBe(100);
    expect(goalAt(steps, "2021-01-01")).toBe(200);
  });

  it("antes do primeiro degrau vale o primeiro, e sem degraus não há meta", () => {
    expect(goalAt(steps, "2019-06-01")).toBe(100);
    expect(goalAt([], "2020-01-01")).toBeUndefined();
  });
});

describe("projeção da data da meta", () => {
  it("projeta pelo ganho médio do último ano", () => {
    const history = [point("2022-01-01", "100000"), point("2022-07-01", "106000"), point("2023-01-01", "112000")];
    const projection = projectGoalDate(history, "130000");
    // 12.000 em 365 dias; faltam 18.000, então 1,5 × 365 = 547,5 dias depois de 01/01/2023
    expect(projection?.months).toBeCloseTo((1.5 * 365) / (365.25 / 12), 6);
    expect(projection?.monthYear).toBe("jul/2024");
  });

  it("histórico de um ponto só ou de menos de um ano não projeta", () => {
    expect(projectGoalDate([], "130000")).toBeNull();
    expect(projectGoalDate([point("2023-01-01", "112000")], "130000")).toBeNull();
    expect(projectGoalDate([point("2022-06-01", "100000"), point("2023-01-01", "112000")], "130000")).toBeNull();
  });

  it("sem ganho, ou com a meta já batida, não projeta", () => {
    const flat = [point("2022-01-01", "100000"), point("2023-01-01", "100000")];
    const falling = [point("2022-01-01", "100000"), point("2023-01-01", "90000")];
    const reached = [point("2022-01-01", "100000"), point("2023-01-01", "140000")];
    expect(projectGoalDate(flat, "130000")).toBeNull();
    expect(projectGoalDate(falling, "130000")).toBeNull();
    expect(projectGoalDate(reached, "130000")).toBeNull();
  });

  it("descreve a distância em meses ou anos", () => {
    expect(displayProjectionDistance(0.5)).toBe("daqui a menos de 1 mês");
    expect(displayProjectionDistance(1)).toBe("daqui a uns 1 mês");
    expect(displayProjectionDistance(5.4)).toBe("daqui a uns 5 meses");
    expect(displayProjectionDistance(11.6)).toBe("daqui a uns 12 meses");
    expect(displayProjectionDistance(12)).toBe("daqui a uns 1 ano");
    expect(displayProjectionDistance(18)).toBe("daqui a uns 2 anos");
  });
});
