import { Handshake, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { OrderPreview } from "@/types";

type SovereignStakeProps = {
  data: NonNullable<OrderPreview["sovereign"]>;
};

/** A fatia do Fundo Soberano na empresa ou na gestora depois da compra, com a régua do teto de fatia. */
export function SovereignStake({ data }: SovereignStakeProps) {
  const ceiling = Number(data.ceiling);
  const after = data.stake_after === null ? null : Number(data.stake_after);
  const filled = after === null ? 0 : Math.min(after / ceiling, 1);

  return (
    <>
      {/* Fatia e teto */}
      <div className="grid gap-2 rounded-[10px] bg-fund-soft p-3.5 text-[13px]">
        <div className="flex justify-between gap-3">
          <span className="font-semibold">Fatia da {data.issuer} depois</span>
          <span className="font-mono font-semibold">{after === null ? "—" : displayPercent(after, 1)}</span>
        </div>
        <div className="h-1.5 rounded-full bg-card">
          <div className="h-full rounded-full bg-fund" style={{ width: `${filled * 100}%` }} />
        </div>
        <p className="text-muted-foreground">
          {data.room === null || data.stake_before === null
            ? "Sem o número de papéis em circulação não há fatia para medir."
            : `Hoje o fundo tem ${displayPercent(data.stake_before, 1)}. Cabem mais ${displayQuantity(data.room)} ${
                data.is_fund ? "cotas" : "ações"
              } até o teto de ${displayPercent(ceiling, 0)} do que existe.`}
        </p>
      </div>

      {/* Gestora de aliado */}
      {data.allied && (
        <Alert variant="warning">
          <Handshake />
          <AlertTitle>Gestora de aliado: vira manchete de favorecimento</AlertTitle>
          <AlertDescription>
            Comprar cotas de uma gestora do partido do governo ou da base sai no jornal como favorecimento e soma
            rejeição ao partido em todos os grupos, em proporção à fatia ganha.
          </AlertDescription>
        </Alert>
      )}

      {/* Compra que o fundo não faz */}
      {data.refusal !== null && (
        <Alert variant="destructive">
          <TriangleAlert />
          <AlertTitle>O fundo não compra este ativo</AlertTitle>
          <AlertDescription>{data.refusal}</AlertDescription>
        </Alert>
      )}
    </>
  );
}
