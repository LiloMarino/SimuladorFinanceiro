import { InfoHint } from "@/shared/components/info-hint";
import { StrategyGroupIcon } from "@/shared/components/strategy-group-icon";
import { Card, CardContent } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import type { StrategyGroup, StrategyInfo } from "@/types";
import { GROUP_SECTION } from "@/shared/lib/strategy-groups";
import { ActiveMark } from "./active-mark";

const GROUPS: StrategyGroup[] = ["reference", "tactic"];

type StrategyListProps = {
  strategies: StrategyInfo[];
  selectedKey: string;
  /** A estratégia ligada, se houver */
  activeKey: string | undefined;
  onSelect: (key: string) => void;
};

/** As estratégias por grupo; a escolhida abre o detalhe ao lado. */
export function StrategyList({ strategies, selectedKey, activeKey, onSelect }: StrategyListProps) {
  return (
    <Card size="sm">
      <CardContent>
        <div className="grid gap-0.5">
          {GROUPS.map((group) => {
            const items = strategies.filter((strategy) => strategy.group === group);
            if (items.length === 0) return null;
            return (
              <div key={group} className="grid gap-0.5">
                {/* Título do grupo */}
                <div className="flex items-center gap-1.5 px-3.5 pt-3.5 pb-1.5 text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">
                  {GROUP_SECTION[group].title}
                  <InfoHint label={`O que são as ${GROUP_SECTION[group].title.toLowerCase()}`}>
                    {GROUP_SECTION[group].hint}
                  </InfoHint>
                </div>

                {/* Estratégias do grupo */}
                {items.map((strategy) => {
                  const selected = strategy.key === selectedKey;
                  return (
                    <button
                      key={strategy.key}
                      type="button"
                      aria-pressed={selected}
                      onClick={() => onSelect(strategy.key)}
                      className={cn(
                        "grid grid-cols-[36px_1fr_auto] items-center gap-x-3 gap-y-0.5 rounded-[10px] border border-transparent px-3.5 py-3 text-left outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
                        selected ? "border-primary bg-info-soft ring-1 ring-primary" : "hover:bg-subtle",
                      )}
                    >
                      <StrategyGroupIcon group={group} />
                      <span className={cn("min-w-0 text-sm", selected ? "font-semibold" : "font-medium")}>
                        {strategy.name}
                      </span>
                      {strategy.key === activeKey ? <ActiveMark /> : <span />}
                      <span className="col-span-2 text-xs text-muted-foreground">{strategy.summary}</span>
                    </button>
                  );
                })}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
