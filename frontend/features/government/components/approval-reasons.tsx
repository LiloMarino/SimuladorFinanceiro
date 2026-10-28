import { cn } from "@/shared/lib/utils";
import type { GovernmentApproval } from "@/types";
import { factorPoints, projectionSentence } from "../lib/approval";
import type { GroupApproval } from "../lib/approval";
import { shareLabel } from "../lib/government";
import { GROUP_INFO, READING_LABEL } from "../lib/voters";
import { GroupIcon } from "./value-chip";

type ApprovalReasonsProps = {
  group: GroupApproval;
  approval: Pick<GovernmentApproval, "reproves_below">;
};

/** Por que o grupo mira o alvo que mira: o ponto neutro e, fator a fator, o que soma ou tira. */
export function ApprovalReasons({ group, approval }: ApprovalReasonsProps) {
  const label = GROUP_INFO[group.group].label;
  const reads = group.readings.map((reading) => READING_LABEL[reading]).join(", ");

  return (
    <div className="grid gap-2.5 rounded-lg border border-info-border bg-info-soft/50 p-3.5">
      <div className="flex items-center gap-2">
        <GroupIcon group={group.group} className="size-7" />
        <div className="grid">
          <b className="text-[13px]">
            Por que o alvo de {label.toLowerCase()} é {group.target}
          </b>
          <span className="text-xs text-muted-foreground">
            Lê: {reads} · {shareLabel(group.weight)} do eleitorado
          </span>
        </div>
      </div>
      <ul className="grid">
        {group.factors.map((factor) => (
          <li
            key={`${factor.kind}-${factor.measure_id ?? ""}`}
            className="flex items-baseline gap-2.5 border-t py-1.25 text-[12.5px]"
          >
            <span
              className={cn(
                "w-9 shrink-0 font-mono font-semibold",
                factor.kind !== "BASE" && Number(factor.points) > 0 && "text-success",
                factor.kind !== "BASE" && Number(factor.points) < 0 && "text-destructive",
              )}
            >
              {factorPoints(factor)}
            </span>
            <span className="flex-1">{factor.description}</span>
          </li>
        ))}
        <li className="flex items-baseline gap-2.5 border-t-2 border-foreground py-1.5 text-[12.5px]">
          <span className="w-9 shrink-0 font-mono font-bold">{group.target}</span>
          <b className="flex-1">Alvo de {label.toLowerCase()}</b>
        </li>
      </ul>
      <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs leading-normal text-muted-foreground">
        A satisfação anda um terço do caminho até o alvo a cada fim de mês:{" "}
        {projectionSentence(group.satisfaction, group.target)}. Abaixo de {approval.reproves_below}, o grupo reprova o
        mês.
      </p>
    </div>
  );
}
