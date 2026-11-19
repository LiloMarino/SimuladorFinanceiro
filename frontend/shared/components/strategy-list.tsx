import { ActiveMark } from "@/shared/components/active-mark";
import { InfoHint } from "@/shared/components/info-hint";
import { StrategyGroupIcon } from "@/shared/components/strategy-group-icon";
import { GROUP_SECTION } from "@/shared/lib/strategy-groups";
import { cn } from "@/shared/lib/utils";
import type { StrategyGroup, StrategyInfo } from "@/types";

const GROUPS: StrategyGroup[] = ["reference", "tactic"];

type StrategyListProps = {
  strategies: StrategyInfo[];
  selectedKey: string;
  /** A estratégia ligada, se houver */
  activeKey?: string | undefined;
  /** As estratégias com parâmetros diferentes do padrão */
  adjustedKeys?: ReadonlySet<string>;
  /** O fundo onde a lista assenta: o hover é o tom seguinte a ele */
  surface?: "card" | "panel";
  onSelect: (key: string) => void;
};

/** As estratégias por grupo, com a ligada e as ajustadas marcadas; a escolhida abre o detalhe ao lado. */
export function StrategyList({
  strategies,
  selectedKey,
  activeKey,
  adjustedKeys,
  surface = "card",
  onSelect,
}: StrategyListProps) {
  return (
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
                    selected
                      ? "border-primary bg-info-soft ring-1 ring-primary"
                      : surface === "card"
                        ? "hover:bg-subtle"
                        : "hover:bg-muted",
                  )}
                >
                  <StrategyGroupIcon group={group} />
                  <span className={cn("min-w-0 text-sm", selected ? "font-semibold" : "font-medium")}>
                    {strategy.name}
                  </span>
                  {strategy.key === activeKey ? (
                    <ActiveMark />
                  ) : adjustedKeys?.has(strategy.key) ? (
                    <span className="text-xs font-semibold text-info">Ajustada</span>
                  ) : (
                    <span />
                  )}
                  <span className="col-span-2 text-xs text-muted-foreground">{strategy.summary}</span>
                </button>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}
