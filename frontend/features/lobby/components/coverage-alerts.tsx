import { CircleAlert, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { CoverageCheck } from "../lib/coverage";

export function CoverageAlerts({ check }: { check: CoverageCheck }) {
  const { missingAtStart, endingBeforeEnd } = check;

  return (
    <>
      {missingAtStart.length > 0 && (
        <Alert variant="destructive">
          <CircleAlert />
          <AlertTitle>Sem indicador na data inicial</AlertTitle>
          <AlertDescription>
            <p>
              {missingAtStart.map((s) => s.name).join(", ")} não {missingAtStart.length > 1 ? "têm" : "tem"} dado nessa
              data. Atualize os indicadores na Central de dados ou escolha uma data inicial mais recente.
            </p>
          </AlertDescription>
        </Alert>
      )}

      {endingBeforeEnd.length > 0 && (
        <Alert variant="warning">
          <TriangleAlert />
          <AlertTitle>Período passa do dado real</AlertTitle>
          <AlertDescription>
            <p>Depois do último dia com dado real, a partida repete o último valor conhecido:</p>
            <p>
              {endingBeforeEnd
                .map((s) => `${s.key} até ${displayDate(parseLocalDate(s.real_end as string))}`)
                .join(" · ")}
            </p>
          </AlertDescription>
        </Alert>
      )}
    </>
  );
}
