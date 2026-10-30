import { Lock, X } from "lucide-react";
import { InfoHint } from "@/shared/components/info-hint";
import { cn } from "@/shared/lib/utils";
import type { GovernmentPanel } from "@/types";
import { remainingMonths, streakMonths } from "../lib/approval";
import { isComputerGovernment, monthYear, successionLabel } from "../lib/government";

type StreakPipsProps = {
  approval: NonNullable<GovernmentPanel["approval"]>;
  className?: string;
};

/** Um quadradinho por fechamento que o impeachment exige: vermelho para os que já fecharam abaixo do piso, cadeado na carência. */
export function StreakPips({ approval, className }: StreakPipsProps) {
  return (
    <span
      className={cn("inline-flex gap-1", className)}
      role="img"
      aria-label={`${approval.low_streak} de ${approval.impeachment_months} fechamentos abaixo do piso`}
    >
      {Array.from({ length: approval.impeachment_months }, (_, index) => {
        const on = !approval.in_grace && index < approval.low_streak;
        return (
          <span
            key={index}
            className={cn(
              "inline-flex size-4 items-center justify-center rounded-sm",
              on ? "bg-destructive text-white" : approval.in_grace ? "bg-subtle ring-1 ring-border" : "bg-muted",
            )}
          >
            {on && <X className="size-2.5" strokeWidth={3} />}
            {approval.in_grace && <Lock className="size-2.5 text-muted-foreground" />}
          </span>
        );
      })}
    </span>
  );
}

/** A frase do piso: a regra, a carência ou a contagem em andamento com os meses que faltam. */
function floorSentence(panel: GovernmentPanel, approval: NonNullable<GovernmentPanel["approval"]>) {
  const { floor, impeachment_months: total, grace_until: graceUntil } = approval;
  const posse = approval.history.length <= 1;
  if (approval.in_grace) {
    return posse
      ? `${total} meses seguidos abaixo de ${floor}% derrubam o governo. Carência até ${monthYear(graceUntil)}.`
      : `Carência até ${monthYear(graceUntil)}: nenhum impeachment no 1º ano, e os meses abaixo de ${floor}% não entram na contagem.`;
  }
  if (approval.low_streak === 0) {
    return `${total} meses seguidos abaixo de ${floor}% derrubam o governo. A carência acabou em ${monthYear(graceUntil)}.`;
  }
  const since = streakMonths(approval)[0];
  const president = panel.term?.president?.name ?? "o presidente";
  return `Abaixo de ${floor}% desde ${since}. Se o governo fechar mais ${total - approval.low_streak} ${total - approval.low_streak === 1 ? "mês" : "meses"} abaixo (${remainingMonths(approval)}), ${president} cai e ${successionLabel(panel)}.`;
}

type ImpeachmentFloorProps = { panel: GovernmentPanel };

/** O piso do impeachment no card de aprovação: público, com a contagem para todos os jogadores. */
export function ImpeachmentFloor({ panel }: ImpeachmentFloorProps) {
  const approval = panel.approval;
  // O partido do computador governa até o fim do mandato, sem piso
  if (!approval || isComputerGovernment(panel.term)) return null;

  return (
    <div className="flex items-center justify-between gap-3 border-t pt-3">
      <div className="grid gap-0.5">
        <span className="flex items-center gap-1 text-[13px] font-semibold">
          Piso do impeachment
          <InfoHint label="Como funciona o piso do impeachment">
            Se a aprovação geral fechar o mês abaixo do piso, entra na contagem; {approval.impeachment_months}{" "}
            fechamentos seguidos abrem o pedido de impeachment, que a casa vota com 68 de 101 cadeiras. No primeiro ano
            do mandato o piso não conta, e fechar um mês acima dele zera a contagem.
          </InfoHint>
        </span>
        <span className="text-xs leading-normal text-muted-foreground">{floorSentence(panel, approval)}</span>
      </div>
      <div className="grid justify-items-end gap-1">
        <StreakPips approval={approval} />
        <span className="font-mono text-[11px] text-muted-foreground">
          {approval.in_grace ? "carência" : `${approval.low_streak} de ${approval.impeachment_months}`}
        </span>
      </div>
    </div>
  );
}
