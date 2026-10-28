import { Badge } from "@/shared/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { CampaignPromise } from "@/types";

type PromiseBadgesProps = {
  promises: CampaignPromise[];
  /** O partido do computador promete por regra, com medidas dos próprios valores */
  computer?: boolean;
};

/** As promessas da chapa como selos; o nome inteiro e o dia do anúncio ficam na dica. */
export function PromiseBadges({ promises, computer = false }: PromiseBadgesProps) {
  if (promises.length === 0) return null;
  return (
    <span className="flex flex-wrap gap-1">
      {promises.map((promise) => (
        <Tooltip key={`${promise.kind}|${promise.sector ?? ""}|${promise.segment ?? ""}`}>
          <TooltipTrigger render={<span className="max-w-full cursor-help" />}>
            <Badge variant="outline" size="sm" className="max-w-full">
              <span className="truncate">{promise.title}</span>
            </Badge>
          </TooltipTrigger>
          <TooltipContent>
            {promise.title} · prometido em {displayDayMonth(promise.announced)}
            {computer && " · o computador promete pelos valores dele"}
          </TooltipContent>
        </Tooltip>
      ))}
    </span>
  );
}
