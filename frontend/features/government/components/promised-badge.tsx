import { Badge } from "@/shared/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import type { GovernmentPanel, MeasureKind } from "@/types";
import { promiseValue } from "../lib/promises";

type PromisedBadgeProps = {
  kind: MeasureKind;
  target: GovernmentPanel["taxes"][number]["promised_target"];
};

/** O selo de medida prometida pela chapa que governa; a dica traz o valor prometido. */
export function PromisedBadge({ kind, target }: PromisedBadgeProps) {
  const badge = (
    <Badge variant="info" size="sm">
      prometido
    </Badge>
  );
  if (target === null) return badge;
  return (
    <Tooltip>
      <TooltipTrigger render={<span className="cursor-help" />}>{badge}</TooltipTrigger>
      <TooltipContent>Prometido: {promiseValue(kind, target)}</TooltipContent>
    </Tooltip>
  );
}
