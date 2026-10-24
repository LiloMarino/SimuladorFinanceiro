import { Check } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { cn } from "@/shared/lib/utils";
import { displayShortDate, displayMonthShort } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionPhase } from "@/types";
import { countdownLabel, phaseLabel } from "../lib/election";
import { PartyMark } from "./party-mark";

type StepState = "done" | "current" | "pending";

/** O passo do calendário em que a eleição está: antes da candidatura e durante o mandato nenhum passo corre. */
const CURRENT_STEP: Record<ElectionPhase, number> = {
  BEFORE_CAMPAIGN: -1,
  CAMPAIGN: 0,
  BETWEEN_ROUNDS: 2,
  AWAITING_TERM: 3,
  TERM: -1,
};

const monthYear = (isoDate: string) => `${displayMonthShort(isoDate)} ${isoDate.slice(0, 4)}`;

/** Para onde a contagem regressiva aponta em cada fase. */
function nextMilestone(panel: ElectionPanel) {
  const { dates } = panel;
  switch (panel.phase) {
    case "BEFORE_CAMPAIGN":
    case "TERM":
      return { label: "Faltam para abrir a candidatura", date: dates.campaign_start };
    case "CAMPAIGN":
      return { label: "Faltam para o 1º turno", date: dates.first_round };
    case "BETWEEN_ROUNDS":
      return { label: "Faltam para o 2º turno", date: dates.runoff };
    case "AWAITING_TERM":
      return { label: "Faltam para a posse", date: dates.inauguration };
  }
}

function viewerBadge(panel: ElectionPanel) {
  const mine = panel.my_party;
  const party = mine && panel.parties.find((p) => p.id === mine.party_id);
  if (!mine || !party) return null;
  const role = mine.is_candidate
    ? "Você concorre pelo"
    : mine.vice === "ACCEPTED"
      ? "Você é vice no"
      : mine.vice === "PENDING"
        ? "Convite de vice do"
        : "Você é filiado ao";
  return { role, party };
}

type ElectionHeaderProps = { panel: ElectionPanel };

/** Cabeçalho da eleição: o ano, o papel de quem vê, a contagem regressiva e os quatro passos do calendário. */
export function ElectionHeader({ panel }: ElectionHeaderProps) {
  const { dates, phase, today } = panel;
  const milestone = nextMilestone(panel);
  const badge = viewerBadge(panel);
  const computers = panel.parties.filter((party) => party.is_computer).length;
  const players = panel.parties.length - computers;
  const runoffSkipped = phase === "AWAITING_TERM" && panel.last_result?.round === 1;
  const current = CURRENT_STEP[phase];

  const steps = [
    { title: "Campanha", date: `${monthYear(dates.campaign_start)} → ${monthYear(dates.ticket_deadline)}`, note: "Partidos, chapas e verba abertos" },
    { title: "1º turno", date: displayShortDate(dates.first_round), note: "Mais de 50% dos votos válidos leva" },
    {
      title: "2º turno, se precisar",
      date: displayShortDate(dates.runoff),
      note: runoffSkipped ? "Dispensado: houve vencedor no 1º turno" : "Os dois mais votados; quem ficou de fora pode doar",
    },
    { title: "Posse", date: displayShortDate(dates.inauguration), note: "Começa o mandato de 4 anos" },
  ];
  const stateOf = (index: number): StepState => (index < current ? "done" : index === current ? "current" : "pending");

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4">
          <div className="flex flex-wrap items-center gap-4">
            <ExpansionEmblem expansion="government" size="lg" />
            <div className="grid min-w-0 flex-1 gap-1">
              <div className="flex flex-wrap items-center gap-2.5">
                <b className="text-xl">Eleição de {monthYear(dates.first_round)}</b>
                <Badge variant="secondary">{phaseLabel(phase)}</Badge>
                {badge && (
                  <Badge variant="info">
                    {badge.role}
                    <PartyMark abbr={badge.party.abbr} color={badge.party.color} size="sm" />
                  </Badge>
                )}
              </div>
              <span className="text-[13px] text-muted-foreground">
                {panel.parties.length === 0
                  ? "Ainda sem partidos. Quando a candidatura abrir, é aqui que eles aparecem."
                  : `${panel.parties.length} ${panel.parties.length === 1 ? "partido" : "partidos"}: ${players} de jogadores e ${computers} do computador, que completa as vagas até 3 · mandato de 4 anos, com uma reeleição`}
              </span>
            </div>
            <div className="grid justify-items-end">
              <span className="text-xs text-muted-foreground uppercase">{milestone.label}</span>
              <span className="font-mono text-[22px] font-semibold">{countdownLabel(today, milestone.date)}</span>
            </div>
          </div>

          {/* Calendário */}
          <ol className="flex flex-wrap gap-3 border-t pt-3.5">
            {steps.map((step, index) => {
              const state = stateOf(index);
              return (
                <li key={step.title} className="flex min-w-44 flex-1 items-start gap-2.5">
                  <span
                    className={cn(
                      "inline-flex size-6.5 shrink-0 items-center justify-center rounded-full text-xs font-semibold",
                      state === "current" && "bg-primary text-primary-foreground",
                      state === "done" && "bg-success-soft text-success",
                      state === "pending" && "bg-muted text-muted-foreground",
                    )}
                  >
                    {state === "done" ? <Check className="size-3.5" /> : index + 1}
                  </span>
                  <span className="grid gap-px">
                    <b className="text-[13px]">{step.title}</b>
                    <span className="font-mono text-xs">{step.date}</span>
                    <span className="text-xs text-muted-foreground">{step.note}</span>
                  </span>
                </li>
              );
            })}
          </ol>
        </div>
      </CardContent>
    </Card>
  );
}
