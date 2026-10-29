import { Link } from "react-router-dom";
import { Info } from "lucide-react";
import { PremiumCurveChart } from "@/shared/components/premium-curve-chart";
import { Badge } from "@/shared/components/ui/badge";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";
import { displayPremiumPoints } from "@/shared/lib/budget-metrics";
import { displayPercent, displayRateLabel } from "@/shared/lib/utils/display";
import type { Budget, FixedIncomeOffer } from "@/types";
import { premiumOf, premiumTagLabel, rateWithoutPremium } from "../lib/premium";

type PremiumTagProps = { offer: FixedIncomeOffer; budget: Budget };

/** A etiqueta "inclui X de prêmio" do Tesouro; abre a conta de onde a taxa veio. */
export function PremiumTag({ offer, budget }: PremiumTagProps) {
  return (
    <Popover>
      <PopoverTrigger
        nativeButton={false}
        render={<Badge variant="warning" size="sm" className="cursor-pointer justify-self-start" />}
        onClick={(e) => e.stopPropagation()}
      >
        {premiumTagLabel(offer)}
        <Info />
      </PopoverTrigger>
      <PopoverContent side="bottom" align="start" className="w-95 max-w-[90vw]">
        <div className="grid gap-3 p-3.5">
          <b className="text-[13px]">Por que a taxa subiu?</b>
          <span className="text-[12.5px] leading-normal">
            O governo deve <b>{displayPercent(budget.month.debt, 1)} do PIB</b>. Acima de{" "}
            {displayPercent(budget.premium_floor, 0)}, quem empresta ao governo cobra um prêmio pelo risco: hoje,{" "}
            {displayPremiumPoints(budget.month.premium)} a mais ao ano nos títulos novos.
          </span>

          {/* Taxa sem prêmio + prêmio = taxa de hoje */}
          <div className="grid grid-cols-[1fr_auto] gap-x-4 gap-y-1 text-[12.5px]">
            <span>Taxa sem o prêmio</span>
            <span className="text-right font-mono">{rateWithoutPremium(offer)}</span>
            <span>Prêmio de risco do governo</span>
            <span className="text-right font-mono text-warning">
              +{(premiumOf(offer) * 100).toFixed(2).replace(".", ",")}
            </span>
            <b className="border-t pt-1">Taxa de hoje</b>
            <b className="border-t pt-1 text-right font-mono">
              {displayRateLabel(offer.rate_index, offer.interest_rate)}
            </b>
          </div>

          <PremiumCurveChart budget={budget} height={150} />

          <span className="rounded-md bg-subtle px-2.5 py-1.5 text-xs text-muted-foreground">
            O título que você já tem mantém a taxa da compra. Taxa maior é bom para quem compra agora, e um sinal de que
            a dívida do governo pesa.
          </span>
          <Link to="/government?tab=accounts" className="text-[12.5px] font-medium text-primary hover:underline">
            Ver o orçamento do governo ›
          </Link>
        </div>
      </PopoverContent>
    </Popover>
  );
}
