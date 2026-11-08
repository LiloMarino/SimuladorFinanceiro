import { Eraser } from "lucide-react";
import { InfoHint } from "@/shared/components/info-hint";
import type { SeriesCoverage } from "@/types";

type CorrectedDaysHintProps = { days: SeriesCoverage["corrected_days"] };

/** Dica discreta da série com dias em que a fonte errou o preço e o fechamento foi interpolado. */
export function CorrectedDaysHint({ days }: CorrectedDaysHintProps) {
  if (days === 0) return null;

  const count = days === 1 ? "1 dia corrigido" : `${days} dias corrigidos`;
  return (
    <InfoHint label={count} icon={Eraser}>
      <div className="space-y-1 text-left">
        <p className="font-semibold">{count}</p>
        <p>
          Nesses dias a fonte (yfinance) trouxe um preço absurdo que voltou ao normal em poucos pregões, como uma queda
          de 99% seguida de recuperação. O fechamento foi trocado por uma linha reta entre os pregões vizinhos e o
          volume ficou zerado.
        </p>
      </div>
    </InfoHint>
  );
}
