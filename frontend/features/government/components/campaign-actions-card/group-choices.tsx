import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { cn } from "@/shared/lib/utils";
import { displayPercent } from "@/shared/lib/utils/display";
import type { CampaignAction, CampaignActionKind, ElectionParty, ElectionPoll, VoterGroup } from "@/types";
import { ACTION_INFO, monthLabel, nextMonthLabel, ratePercent } from "../../lib/campaign";
import { GROUP_INFO } from "../../lib/voters";
import { GroupIcon } from "@/shared/components/value-chip";
import { GroupPollCell } from "./group-poll-cell";

type GroupChoicesProps = {
  action: CampaignAction;
  kind: CampaignActionKind;
  group: VoterGroup;
  onGroup: (group: VoterGroup) => void;
  weights: Map<VoterGroup, string>;
  undecided: Map<VoterGroup, string | null> | null;
  today: string;
  party: ElectionParty;
  parties: ElectionParty[];
  poll: ElectionPoll | undefined;
};

const GROUP_ROW = "grid grid-cols-[16px_28px_minmax(0,1fr)_54px_64px_92px_74px] items-center gap-3";
const GROUP_ROW_POLL = "grid grid-cols-[16px_28px_minmax(0,1fr)_54px_64px_112px_92px_74px] items-center gap-3";

export function GroupChoices({
  action,
  kind,
  group,
  onGroup,
  weights,
  undecided,
  today,
  party,
  parties,
  poll,
}: GroupChoicesProps) {
  // A pesquisa no grupo é do 1º turno: no 2º, o Voto e os Indecisos ocupam o lugar dela
  const showPoll = !undecided;
  const rowClass = showPoll ? GROUP_ROW_POLL : GROUP_ROW;
  return (
    <div role="radiogroup" aria-label="Grupo" className="grid gap-0.5">
      <div
        className={cn(rowClass, "px-2 pb-0.5 text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase")}
      >
        <span />
        <span />
        <span>Grupo</span>
        <span className="text-right">{undecided ? "Voto" : "Apoio"}</span>
        <span className="text-right">{undecided ? "Indecisos" : "Rejeição"}</span>
        {showPoll && <span className="text-right">Pesquisa no grupo</span>}
        <span>
          {ACTION_INFO[kind].plural}
          {undecided ? " no 2º turno" : ` em ${monthLabel(today)}`}
        </span>
        <span className="text-right">Rende</span>
      </div>
      {action.targets.map((target) => {
        if (target.group === null) return null;
        const selected = target.group === group;
        const rate = Number(target.rate);
        return (
          <button
            key={target.group}
            type="button"
            role="radio"
            aria-checked={selected}
            onClick={() => onGroup(target.group!)}
            className={cn(
              rowClass,
              "rounded-lg border border-transparent px-2 py-1.5 text-left text-[13px] outline-none hover:bg-subtle focus-visible:ring-3 focus-visible:ring-ring/50",
              selected && "border-primary bg-info-soft/40",
            )}
          >
            <span
              aria-hidden
              className={cn(
                "size-4 rounded-full border-2 border-input",
                selected && "border-primary bg-primary shadow-[inset_0_0_0_3px_var(--card)]",
              )}
            />
            <GroupIcon group={target.group} className="size-7" />
            <span className="grid min-w-0">
              <span className={cn("truncate", selected ? "font-semibold" : "font-medium")}>
                {GROUP_INFO[target.group].label}
              </span>
              <span className="text-xs text-faint-foreground">
                {displayPercent(weights.get(target.group) ?? 0, 0)} do eleitorado
              </span>
            </span>
            <span className="text-right font-mono">{Math.round(Number(target.support ?? 0))}</span>
            <span className="text-right font-mono">
              {undecided
                ? Math.round(Number(undecided.get(target.group) ?? 0))
                : Math.round(Number(target.rejection ?? 0))}
            </span>
            {showPoll && (
              <GroupPollCell
                poll={poll?.groups.find((item) => item.group === target.group)}
                party={party}
                parties={parties}
              />
            )}
            <span className="flex items-center gap-1.5">
              <span className="flex gap-0.5" aria-hidden>
                {[0, 1, 2].map((pip) => (
                  <i
                    key={pip}
                    className={cn(
                      "size-2 rounded-full not-italic",
                      pip < target.uses_this_month ? "bg-primary" : "bg-border",
                    )}
                  />
                ))}
              </span>
              <span className="text-xs text-faint-foreground">{target.uses_this_month}×</span>
            </span>
            <span
              className={cn(
                "text-right font-mono font-semibold",
                rate >= 1 ? "text-success" : rate >= 0.5 ? "text-warning" : "text-destructive",
              )}
            >
              <Tooltip>
                <TooltipTrigger render={<span className="cursor-help" />}>
                  <span className="underline decoration-dotted">{ratePercent(rate)}</span>
                </TooltipTrigger>
                <TooltipContent side="top" className="max-w-80">
                  Retorno decrescente: a mesma ação no mesmo grupo rende 100%, 50% e 25% no mês. O partido já fez{" "}
                  {target.uses_this_month}× aqui neste mês; em {nextMonthLabel(today)} volta a 100%.
                </TooltipContent>
              </Tooltip>
            </span>
          </button>
        );
      })}
    </div>
  );
}
