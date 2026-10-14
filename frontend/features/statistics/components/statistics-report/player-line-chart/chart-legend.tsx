import { Toggle } from "@/shared/components/ui/toggle";
import type { LineSeries } from "./series";

interface Props {
  series: LineSeries[];
  visible: Record<string, boolean>;
  toggle: (key: string) => void;
}

/** Legenda que liga e desliga cada linha; referência tracejada aparece com traço. */
export function LineChartLegend({ series, visible, toggle }: Props) {
  return (
    <div className="flex flex-wrap justify-center gap-1.5 pt-2">
      {series.map((s) => (
        <Toggle key={s.key} variant="outline" size="sm" pressed={visible[s.key]} onPressedChange={() => toggle(s.key)}>
          <span
            className={s.dashed ? "h-0.5 w-3.5 border-t-2 border-dashed" : "size-2.5 rounded-full"}
            style={s.dashed ? { borderColor: s.color } : { backgroundColor: s.color }}
            aria-hidden="true"
          />
          {s.label}
        </Toggle>
      ))}
    </div>
  );
}
