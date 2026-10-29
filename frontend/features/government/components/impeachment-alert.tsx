import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { displayDayMonth, displayList } from "@/shared/lib/utils/display";
import type { GovernmentPanel } from "@/types";
import { closingsLeft, remainingMonths, streakMonths } from "../lib/approval";
import { lowStreakLabel, successionLabel } from "../lib/government";
import { StreakPips } from "./impeachment-floor";

type ImpeachmentAlertProps = { panel: GovernmentPanel };

/** O aviso ao presidente: desde o primeiro fechamento abaixo do piso, quantos faltam para o impeachment. */
export function ImpeachmentAlert({ panel }: ImpeachmentAlertProps) {
  const approval = panel.approval;
  if (!approval || approval.in_grace || approval.low_streak === 0) return null;

  const left = closingsLeft(approval);
  const recovers = approval.target >= approval.floor;
  const outlook = `Aprovação de ${approval.value}% hoje, com alvo de ${approval.target}%: no ritmo atual ela ${recovers ? "volta" : "não volta"} acima do piso.`;
  const consequence =
    left <= 1
      ? `Se ${displayDayMonth(approval.closes_on)} fechar abaixo de ${approval.floor}%, abre o pedido de impeachment e a casa vota se tira você; com 68 de 101 votos Sim, ${successionLabel(panel)}.`
      : `Mais ${left} meses (${remainingMonths(approval)}) e abre o pedido de impeachment: a casa vota e, com 68 de 101 votos Sim, ${successionLabel(panel)}.`;

  return (
    <Alert variant="destructive">
      <TriangleAlert />
      <AlertTitle>{lowStreakLabel(approval)}</AlertTitle>
      <AlertDescription>
        <div className="grid gap-2">
          <span>
            {outlook} Fecharam abaixo: {displayList(streakMonths(approval))}. {consequence}
          </span>
          <span className="flex items-center gap-3">
            <StreakPips approval={approval} />
            <a href="#approval" className="text-[13px] font-medium">
              Ver o que puxa cada grupo ›
            </a>
          </span>
        </div>
      </AlertDescription>
    </Alert>
  );
}
