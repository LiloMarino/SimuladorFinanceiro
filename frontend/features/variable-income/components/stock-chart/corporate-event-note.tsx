import { Badge } from "@/shared/components/ui/badge";
import { describeSplit } from "@/shared/lib/split-ratio";
import { displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import type { AssetCorporateEvent } from "@/types";

/** O evento da data ex sob a mira, em palavras: o que aconteceu e o que mudou na carteira do jogador. */
export function CorporateEventNote({ event }: { event: AssetCorporateEvent }) {
  return (
    <div className="mt-1.5 grid gap-1 border-t pt-2">
      {event.kind === "DIVIDEND" ? <DividendNote event={event} /> : <SplitNote event={event} />}
    </div>
  );
}

function DividendNote({ event }: { event: AssetCorporateEvent }) {
  return (
    <>
      <b className="flex items-center gap-1.5">
        <Badge variant="dividend">P</Badge>
        Provento de {displayMoney(event.value)} por ação
      </b>
      {event.received !== null && event.shares !== null && (
        <span>
          Suas {displayQuantity(event.shares)} ações renderam no caixa <b>{displayMoney(event.received)}</b>.
        </span>
      )}
      <span className="text-muted-foreground">
        Neste dia o preço abre mais ou menos {displayMoney(event.value)} mais baixo: o dinheiro sai da empresa e vai
        para quem tem a ação.
      </span>
    </>
  );
}

function SplitNote({ event }: { event: AssetCorporateEvent }) {
  const split = describeSplit(event.value);

  return (
    <>
      <b className="flex items-center gap-1.5">
        <Badge variant="split">D</Badge>
        {split.name} {split.label}
      </b>
      {event.shares !== null && event.shares_after !== null && (
        <span>
          Suas ações foram de {displayQuantity(event.shares)} para {displayQuantity(event.shares_after)}.
        </span>
      )}
      <span className="text-muted-foreground">
        O valor da sua posição não muda: o preço se ajusta na mesma proporção.
      </span>
    </>
  );
}
