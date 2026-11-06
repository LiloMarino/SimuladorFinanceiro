import { Vault } from "lucide-react";
import { Card, CardContent } from "@/shared/components/ui/card";
import type { TreasuryCatalog } from "@/types";
import { ratesDay, reviewMonthName } from "../lib/treasury";

type TreasuryHeaderProps = { catalog: TreasuryCatalog };

/** Título da tela, o que o Tesouro é nesta partida e a data das taxas. */
export function TreasuryHeader({ catalog }: TreasuryHeaderProps) {
  const withGovernment = catalog.thermometer !== null;

  return (
    <Card>
      <CardContent>
        <div className="flex flex-wrap items-center gap-4">
          <span
            aria-hidden
            className="inline-flex size-14 shrink-0 items-center justify-center rounded-[14px] bg-info text-white"
          >
            <Vault className="size-[30px]" />
          </span>
          <div className="grid min-w-0 flex-1 gap-1">
            <b className="text-xl">Tesouro</b>
            <span className="text-[13px] text-muted-foreground">
              {withGovernment
                ? "Os títulos do governo, sempre à venda. Todos pagam o prêmio de risco do país, que sobe quando a dívida cresce."
                : "Os títulos do governo, sempre à venda, pela taxa base. Nesta partida não há governo nem dívida no jogo, então não há prêmio."}
            </span>
          </div>
          <div className="grid gap-0.5 text-right">
            <span className="text-xs font-semibold tracking-wider text-faint-foreground uppercase">
              Taxas de {ratesDay(catalog.next_review)}
            </span>
            <span className="text-xs text-muted-foreground">
              a próxima revisão é no fechamento de {reviewMonthName(catalog.next_review)}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
