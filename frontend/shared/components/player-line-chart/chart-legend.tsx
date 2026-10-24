import { TeamBadge } from "@/shared/components/team-badge";
import { Toggle } from "@/shared/components/ui/toggle";
import type { LineSeries } from "./series";

interface Props {
  series: LineSeries[];
  visible: Record<string, boolean>;
  toggle: (key: string) => void;
}

/** Legenda que liga e desliga cada linha; referência tracejada aparece com traço. */
export function LineChartLegend({ series, visible, toggle }: Props) {
  // Séries agrupadas viram uma só entrada, que liga e desliga todas de uma vez
  const entries = series.reduce<{ id: string; head: LineSeries; keys: string[]; label: string }[]>((list, s) => {
    const id = s.legendGroup?.key ?? s.key;
    const found = list.find((entry) => entry.id === id);
    if (found) {
      found.keys.push(s.key);
      return list;
    }
    return [...list, { id, head: s, keys: [s.key], label: s.legendGroup?.label ?? s.label }];
  }, []);

  return (
    <div className="flex flex-wrap justify-center gap-1.5 pt-2">
      {entries.map(({ id, head, keys, label }) => {
        const pressed = keys.every((key) => visible[key]);
        return (
          <Toggle
            key={id}
            variant="outline"
            size="sm"
            pressed={pressed}
            onPressedChange={() => keys.forEach((key) => visible[key] === pressed && toggle(key))}
          >
            <span
              className={
                head.dashed
                  ? "h-0.5 w-3.5 border-t-2 border-dashed"
                  : head.dotted
                    ? "h-0.5 w-3.5 border-t-2 border-dotted"
                    : "size-2.5 rounded-full"
              }
              style={head.dashed || head.dotted ? { borderColor: head.color } : { backgroundColor: head.color }}
              aria-hidden="true"
            />
            {label}
            {head.team?.index ? <TeamBadge team={head.team.index} naming={head.team.naming} form="icon" size="sm" /> : null}
          </Toggle>
        );
      })}
    </div>
  );
}
