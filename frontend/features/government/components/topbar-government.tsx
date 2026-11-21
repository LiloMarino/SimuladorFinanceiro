import { ChevronRight } from "lucide-react";
import { Link } from "react-router-dom";
import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { Badge } from "@/shared/components/ui/badge";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/shared/components/ui/hover-card";
import { useGovernmentStatus } from "@/shared/hooks/queries/useGovernmentStatus";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth } from "@/shared/lib/utils/display";
import { approvalArrow, approvalTone, isComputerGovernment } from "../lib/government";
import { ApprovalSparkline } from "./approval-sparkline";
import { PersonMark } from "@/shared/components/party-mark";

const TONES = { success: "text-success", warning: "text-warning", destructive: "text-destructive" } as const;

/** Selo do topo: quem governa e a aprovação, com a fila do Congresso ao passar o mouse. */
export function TopbarGovernment() {
  const { data: status } = useGovernmentStatus();
  if (!status) return null;

  if (status.computer_until_inauguration) {
    return (
      <Badge variant="secondary">
        <ExpansionEmblem expansion="government" size="xs" />
        <span className="2xl:hidden">Computador</span>
        <span className="hidden 2xl:inline">Governo do computador até a posse</span>
      </Badge>
    );
  }

  const { president, approval } = status;
  if (!president || !approval) {
    return (
      <Badge variant="secondary">
        <ExpansionEmblem expansion="government" size="xs" />
        Governo neutro do computador
      </Badge>
    );
  }

  const tone = TONES[approvalTone(approval)];
  const queued = status.queued_measures;

  return (
    <HoverCard>
      <HoverCardTrigger chip delay={150} render={<Link to="/government" />}>
        <ExpansionEmblem expansion="government" size="sm" className="size-6.5" />
        <span className="grid">
          <span className="text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">Governo</span>
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
        <ApprovalSparkline approval={approval} />
        <span className="text-xs text-muted-foreground">
          Aprovação do governo: de cada 100 eleitores, {approval.value} aprovam.{" "}
          {queued > 0
            ? `${queued} ${queued === 1 ? "medida" : "medidas"} na fila para ${displayDayMonth(status.next_vote)}.`
            : "Nenhuma medida na fila."}
        </span>
        <Link to="/government" className="text-[13px] font-medium text-primary hover:text-primary-hover">
          {isComputerGovernment(president)
            ? "Ver impostos e a fila do computador"
            : `Ver impostos, fila e a carteira de ${president.name}`}
        </Link>
      </HoverCardContent>
    </HoverCard>
  );
}
