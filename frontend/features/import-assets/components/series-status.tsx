import { CircleCheck } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Spinner } from "@/shared/components/ui/spinner";
import { isOutdatedStock } from "@/shared/lib/series-coverage";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { SeriesCoverage } from "@/types";

type SeriesStatusProps = {
  series: SeriesCoverage;
  /** A série está sendo baixada agora */
  updating?: boolean;
};

/** A situação da série: o que pede atenção vira selo, e o que está bem vira "Em dia". */
export function SeriesStatus({ series, updating = false }: SeriesStatusProps) {
  if (updating) {
    return (
      <Badge variant="info">
        <Spinner />
        Atualizando…
      </Badge>
    );
  }
  if (!series.real_end) return <Badge variant="destructive">Sem dado</Badge>;
  if (isOutdatedStock(series)) {
    return <Badge variant="warning">Parou em {displayDate(parseLocalDate(series.real_end))}</Badge>;
  }
  if (series.kind === "STOCK" && !series.segment) return <Badge variant="warning">Sem setor</Badge>;
  return (
    <span className="inline-flex items-center gap-1.5 text-[13px] text-muted-foreground">
      <CircleCheck className="size-4 text-success" />
      Em dia
    </span>
  );
}
