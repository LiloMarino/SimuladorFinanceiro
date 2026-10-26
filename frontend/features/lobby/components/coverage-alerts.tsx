import { Link } from "react-router-dom";
import { Ban, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { displayIsoDate } from "@/shared/lib/utils/display";
import type { CoverageCheck } from "../lib/coverage";

type CoverageAlertsProps = {
  check: CoverageCheck;
  startDate: string;
  /** Abre as regras para trocar a data; só o host tem essa saída */
  onChangeDate?: () => void;
};

// O aviso cita até 3 códigos; o resto vira "e mais N" e a lista completa fica na Central
const MAX_LISTED_CODES = 3;

function listCodes(keys: string[]): string {
  if (keys.length <= MAX_LISTED_CODES) return keys.join(", ");
  return `${keys.slice(0, MAX_LISTED_CODES).join(", ")} e mais ${keys.length - MAX_LISTED_CODES}`;
}

export function CoverageAlerts({ check, startDate, onChangeDate }: CoverageAlertsProps) {
  const { missingAtStart, endingBeforeEnd } = check;

  // Primeiro dia em que todos os indicadores faltantes já têm dado
  const firstCoveredStart = missingAtStart.every((s) => s.start)
    ? missingAtStart
        .map((s) => s.start as string)
        .sort()
        .at(-1)
    : undefined;
  const firstRealEnd = endingBeforeEnd.map((s) => s.real_end as string).sort()[0];

  return (
    <>
      {missingAtStart.length > 0 && (
        <Alert variant="destructive">
          <Ban />
          <AlertTitle>Não dá pra começar em {startDate ? displayIsoDate(startDate) : "—"}</AlertTitle>
          <AlertDescription>
            {missingAtStart.map((s) => s.key).join(" e ")} não {missingAtStart.length > 1 ? "têm" : "tem"} dado nessa
            data.{" "}
            {firstCoveredStart
              ? `Escolha um início a partir de ${displayIsoDate(firstCoveredStart)} ou atualize os indicadores.`
              : "Atualize os indicadores na Central de dados."}
          </AlertDescription>
          <div className="col-span-full mt-1 flex gap-4">
            {onChangeDate && (
              <Button variant="link" size="sm" onClick={onChangeDate}>
                Mudar a data
              </Button>
            )}
            <Button variant="link" size="sm" nativeButton={false} render={<Link to="/import-assets" />}>
              Abrir Central de dados
            </Button>
          </div>
        </Alert>
      )}

      {firstRealEnd !== undefined && (
        <Alert variant="warning">
          <TriangleAlert />
          <AlertDescription>
            Depois de <b className="font-mono">{displayIsoDate(firstRealEnd)}</b> não há preço real: a partida repete o
            último valor de {listCodes(endingBeforeEnd.map((s) => s.key))}.{" "}
            <Link to="/import-assets" className="font-medium text-primary hover:text-primary-hover">
              Ver séries
            </Link>
          </AlertDescription>
        </Alert>
      )}
    </>
  );
}
