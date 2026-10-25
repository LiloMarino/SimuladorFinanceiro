import { Badge } from "@/shared/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import type { SeriesCoverage } from "@/types";

type CorrectedDaysBadgeProps = { days: SeriesCoverage["corrected_days"] };

/** Selo da série com dias em que a fonte errou o preço e o fechamento foi interpolado. */
export function CorrectedDaysBadge({ days }: CorrectedDaysBadgeProps) {
  if (days === 0) return null;

  return (
    <Tooltip>
      <TooltipTrigger render={<span />}>
        <Badge variant="info" size="tag">
          {days === 1 ? "1 dia corrigido" : `${days} dias corrigidos`}
        </Badge>
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-64">
        Nesses dias a fonte (yfinance) trouxe um preço absurdo que voltou ao normal em poucos pregões, como uma queda de
        99% seguida de recuperação. O fechamento foi trocado por uma linha reta entre os pregões vizinhos e o volume
        ficou zerado.
      </TooltipContent>
    </Tooltip>
  );
}
