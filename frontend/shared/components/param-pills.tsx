import { Badge } from "@/shared/components/ui/badge";
import { paramPills, type ParamValues } from "@/shared/lib/strategy-params";
import type { StrategyInfo } from "@/types";

type ParamPillsProps = {
  strategy: StrategyInfo;
  values: ParamValues;
};

/** Os parâmetros da estratégia em etiquetas curtas; em azul, o que saiu do padrão. */
export function ParamPills({ strategy, values }: ParamPillsProps) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {paramPills(strategy, values).map((pill) => (
        <Badge key={pill.key} variant={pill.changed ? "info" : "secondary"} size="tag" numeric={false}>
          {pill.label}
          <b className="font-mono font-semibold">{pill.value}</b>
        </Badge>
      ))}
    </div>
  );
}
