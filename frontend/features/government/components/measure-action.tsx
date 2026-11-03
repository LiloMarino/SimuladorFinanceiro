import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { GovernmentMeasure } from "@/types";

type MeasureActionProps = {
  pending: GovernmentMeasure | null;
  isPresident: boolean;
  onPropose: () => void;
};

/** O que a linha de uma medida mostra no fim: o selo da mudança na fila ou esperando a vigência, ou o botão Mudar para o presidente. */
export function MeasureAction({ pending, isPresident, onPropose }: MeasureActionProps) {
  if (pending) {
    return (
      <Badge variant="warning" size="sm">
        {pending.status === "QUEUED" || !pending.effective
          ? "na fila"
          : `vale em ${displayDayMonth(pending.effective)}`}
      </Badge>
    );
  }
  if (!isPresident) return null;
  return (
    <Button size="xs" variant="outline" onClick={onPropose}>
      Mudar
    </Button>
  );
}
