import { cn } from "@/shared/lib/utils";
import { displayMoney } from "@/shared/lib/utils/display";
import type { CampaignAction } from "@/types";
import { ACTION_INFO, signed } from "../../lib/campaign";
import { ActionIcon } from "../campaign-action-icon";

type ActionChoiceProps = {
  action: CampaignAction;
  selected: boolean;
  short: number;
  cash: number;
  noRival: boolean;
  partyAbbr: string;
  onSelect: () => void;
};

export function ActionChoice({ action, selected, short, cash, noRival, partyAbbr, onSelect }: ActionChoiceProps) {
  const info = ACTION_INFO[action.action];
  const disabled = short > 0 || noRival;
  // O efeito médio da ação no melhor grupo, antes de escolher o grupo
  const best = action.targets.reduce(
    (top, target) => (Math.abs(Number(target.average)) > Math.abs(top) ? Number(target.average) : top),
    0,
  );
  const preview =
    action.action === "TV"
      ? `${signed(best, 1)} em cada grupo`
      : action.action === "ATTACK"
        ? `${signed(best, 1)} do rival`
        : action.action === "EVENT"
          ? `${signed(best, 1)} e repara a rejeição`
          : signed(best, 1);

  return (
    <button
      type="button"
      role="radio"
      aria-checked={selected}
      disabled={disabled}
      onClick={onSelect}
      className={cn(
        "relative grid content-start gap-1.5 rounded-[10px] border bg-card p-3 text-left outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
        selected && "border-primary bg-info-soft/40 ring-1 ring-primary",
        disabled && "bg-subtle",
      )}
    >
      <div className={cn("grid gap-1.5", disabled && "opacity-60")}>
        <div className="flex items-center justify-between">
          <ActionIcon kind={action.action} />
          <span className="font-mono text-[13px] font-semibold">{displayMoney(action.price)}</span>
        </div>
        <b className="text-sm">{info.label}</b>
        <span className="text-xs leading-snug text-muted-foreground">{info.blurb}</span>
        <div className="grid gap-0.5 border-t pt-1.5">
          <span className="font-mono text-xs font-semibold text-success">em média {preview}</span>
          <span className="text-xs text-faint-foreground">{info.dice}</span>
        </div>
      </div>
      {short > 0 && (
        <span className="text-xs text-destructive">
          Faltam {displayMoney(short)} no caixa do partido ({displayMoney(cash)})
        </span>
      )}
      {noRival && (
        <span className="text-xs text-muted-foreground">Sem rival: o {partyAbbr} é o único partido na eleição</span>
      )}
    </button>
  );
}
