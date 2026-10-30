import { ChevronRight, Lock } from "lucide-react";
import { Link } from "react-router-dom";
import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { Badge } from "@/shared/components/ui/badge";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/shared/components/ui/hover-card";
import { useGovernment } from "@/shared/hooks/queries/useGovernment";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth } from "@/shared/lib/utils/display";
import { approvalArrow, approvalTone, isComputerGovernment } from "../lib/government";
import { ApprovalChart } from "./approval-chart";
import { PersonMark } from "./party-mark";

const TONES = { success: "text-success", warning: "text-warning", destructive: "text-destructive" } as const;

/** Selo do topo: quem governa e a aprovação, com a fila do Congresso ao passar o mouse. */
export function TopbarGovernment() {
  const { data: panel } = useGovernment();
  if (!panel) return null;

  if (panel.computer_until_inauguration || !panel.term) {
    return (
      <Badge variant="secondary">
        <ExpansionEmblem expansion="government" size="xs" />
        Governo do computador até a posse
      </Badge>
    );
  }

  const president = panel.term.president;
  const approval = panel.approval;
  if (!president || !approval) {
    return (
      <Badge variant="secondary">
        <ExpansionEmblem expansion="government" size="xs" />
        Governo neutro do computador
      </Badge>
    );
  }

  const tone = TONES[approvalTone(approval)];
  const queued = panel.queue.filter((measure) => measure.status === "QUEUED").length;

  return (
    <>
      <HoverCard>
        <HoverCardTrigger chip delay={150} render={<Link to="/government" />}>
          <ExpansionEmblem expansion="government" size="sm" className="size-6.5" />
          <span className="grid">
            <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">Governo</span>
            <span className="flex items-center gap-1.5 text-[13px]">
              <PersonMark person={president} />
              <b className="font-semibold">{president.name}</b>
              <span className={cn("font-mono text-xs", tone)}>
                aprovação {approval.value}% {approvalArrow(approval)}
              </span>
            </span>
          </span>
          <ChevronRight className="size-3.5 text-muted-foreground" />
        </HoverCardTrigger>
        <HoverCardContent compact align="end">
          <div className="flex justify-between">
            <b className="text-sm">Governo {president.name}</b>
            <span className={cn("font-mono font-semibold", tone)}>{approval.value}%</span>
          </div>
          <ApprovalChart approval={approval} height={64} compact />
          <span className="text-xs text-muted-foreground">
            Aprovação do governo: de cada 100 eleitores, {approval.value} aprovam.{" "}
            {queued > 0
              ? `${queued} ${queued === 1 ? "medida" : "medidas"} na fila para ${displayDayMonth(panel.next_vote)}.`
              : "Nenhuma medida na fila."}
          </span>
          <Link to="/government" className="text-[13px] font-medium text-primary hover:text-primary-hover">
            {isComputerGovernment(panel.term)
              ? "Ver impostos e a fila do computador"
              : `Ver impostos, fila e a carteira de ${president.name}`}
          </Link>
        </HoverCardContent>
      </HoverCard>

      {panel.is_president && (
        <Badge variant="warning" className="h-7.5">
          <Lock />
          Carteira congelada
        </Badge>
      )}
    </>
  );
}
