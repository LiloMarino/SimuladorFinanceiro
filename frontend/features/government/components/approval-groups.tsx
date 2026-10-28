import { Check, Minus, TrendingDown, Users } from "lucide-react";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayMonthShort } from "@/shared/lib/utils/display";
import type { GovernmentApproval } from "@/types";
import { ALL_GROUPS, VERDICT_BADGE, VERDICT_FILL, targetArrow, verdictOf } from "../lib/approval";
import type { GroupVerdict, Selection } from "../lib/approval";
import { SATISFACTION, TARGET } from "../lib/government-metrics";
import { shareLabel } from "../lib/government";
import { GROUP_INFO } from "../lib/voters";
import { GroupIcon } from "./value-chip";

const VERDICT_ICON = { APPROVES: Check, NEUTRAL: Minus, REPROVES: TrendingDown } as const;

const ROW = "grid grid-cols-[28px_minmax(0,1fr)_128px_30px_50px_82px] items-center gap-2";

type SatisfactionBarProps = {
  value: number;
  target: number | null;
  verdict: GroupVerdict;
  approval: Pick<GovernmentApproval, "approves_above" | "reproves_below">;
};

/** A barra da satisfação: a faixa neutra ao fundo e o traço do alvo por cima. */
function SatisfactionBar({ value, target, verdict, approval }: SatisfactionBarProps) {
  return (
    <div className="relative h-2 rounded-full bg-muted" aria-hidden>
      <span
        className="absolute inset-y-0 bg-border"
        style={{ left: `${approval.reproves_below}%`, width: `${approval.approves_above - approval.reproves_below}%` }}
      />
      <span
        className={cn("absolute inset-y-0 left-0 rounded-full", VERDICT_FILL[verdict])}
        style={{ width: `${value}%` }}
      />
      {target !== null && (
        <span
          className="absolute -top-1 h-4 w-0.5 rounded-xs bg-foreground ring-2 ring-card"
          style={{ left: `calc(${target}% - 1px)` }}
        />
      )}
    </div>
  );
}

type RowProps = {
  selected: boolean;
  onSelect: () => void;
  icon: React.ReactNode;
  name: string;
  caption: string;
  satisfaction: number;
  target: number | null;
  verdict: GroupVerdict;
  approval: GovernmentApproval;
  /** A coluna do fechamento: o veredito do mês, ou a data em que ele sai */
  closing: React.ReactNode;
};

function GroupRow({
  selected,
  onSelect,
  icon,
  name,
  caption,
  satisfaction,
  target,
  verdict,
  approval,
  closing,
}: RowProps) {
  return (
    <li className="border-t first:border-t-0">
      <button
        type="button"
        aria-pressed={selected}
        onClick={onSelect}
        className={cn(
          ROW,
          "w-full cursor-pointer rounded-md py-2 text-left text-[13px]",
          selected && "bg-info-soft/60",
        )}
      >
        {icon}
        <span className="grid min-w-0">
          <b className="truncate font-medium">{name}</b>
          <span className="text-[11.5px] text-muted-foreground">{caption}</span>
        </span>
        <SatisfactionBar value={satisfaction} target={target} verdict={verdict} approval={approval} />
        <span className="text-right font-mono font-semibold">{satisfaction}</span>
        {target === null ? (
          <span className="font-mono text-xs text-muted-foreground">—</span>
        ) : (
          <span
            className={cn(
              "font-mono text-xs",
              target > satisfaction && "text-success",
              target < satisfaction && "text-destructive",
              target === satisfaction && "text-muted-foreground",
            )}
          >
            {targetArrow(satisfaction, target)}
          </span>
        )}
        {closing}
      </button>
    </li>
  );
}

function VerdictBadge({ verdict }: { verdict: GroupVerdict }) {
  const { label, variant } = VERDICT_BADGE[verdict];
  const Icon = VERDICT_ICON[verdict];
  return (
    <Badge variant={variant} size="sm">
      <Icon />
      {label}
    </Badge>
  );
}

type ApprovalGroupsProps = {
  approval: GovernmentApproval;
  selection: Selection;
  onSelect: (selection: Selection) => void;
  /** O presidente, para a legenda "votou N% em ..." no mês da posse */
  president: string | null;
};

/** A lista de grupos: o total no topo e uma linha por grupo, do maior ao menor, para comparar de relance. */
export function ApprovalGroups({ approval, selection, onSelect, president }: ApprovalGroupsProps) {
  // Antes do primeiro fechamento só existe o ponto da posse: cada grupo começa como votou
  const atInauguration = approval.history.length <= 1;
  const closedMonth = approval.history.at(-1);
  const closeHeader = atInauguration ? "Fecha" : `Em ${displayMonthShort(closedMonth?.date ?? approval.closes_on)}`;
  const closesOn = displayDayMonth(approval.closes_on);

  return (
    <ul className="grid">
      <li className={cn(ROW, "pb-0.5 text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase")}>
        <span />
        <span>Grupo</span>
        <span className="inline-flex items-center gap-1 normal-case tracking-normal">
          <MetricLabel metric={SATISFACTION} />
        </span>
        <span />
        <span className="inline-flex items-center gap-1 normal-case tracking-normal">
          <MetricLabel metric={TARGET} />
        </span>
        <span>{closeHeader}</span>
      </li>
      <GroupRow
        selected={selection === ALL_GROUPS}
        onSelect={() => onSelect(ALL_GROUPS)}
        icon={
          <span className="inline-flex size-7 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
            <Users className="size-4" />
          </span>
        }
        name="Geral"
        caption="100% do eleitorado"
        satisfaction={approval.value}
        target={atInauguration ? null : approval.target}
        verdict={verdictOf(approval.value, approval)}
        approval={approval}
        closing={
          atInauguration ? (
            <span className="text-xs text-muted-foreground">{closesOn}</span>
          ) : (
            <VerdictBadge verdict={verdictOf(approval.value, approval)} />
          )
        }
      />
      {approval.groups.map((group) => (
        <GroupRow
          key={group.group}
          selected={selection === group.group}
          onSelect={() => onSelect(group.group)}
          icon={<GroupIcon group={group.group} className="size-7" />}
          name={GROUP_INFO[group.group].label}
          caption={
            atInauguration && president
              ? `votou ${group.satisfaction}% em ${president}`
              : `${shareLabel(group.weight)} do eleitorado`
          }
          satisfaction={group.satisfaction}
          target={atInauguration ? null : group.target}
          verdict={group.verdict}
          approval={approval}
          closing={
            atInauguration ? (
              <span className="text-xs text-muted-foreground">{closesOn}</span>
            ) : (
              <VerdictBadge verdict={group.verdict} />
            )
          }
        />
      ))}
    </ul>
  );
}
