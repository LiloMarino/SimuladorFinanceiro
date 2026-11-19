import { Clock, Info, ShoppingCart } from "lucide-react";
import { Link } from "react-router-dom";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Progress } from "@/shared/components/ui/progress";
import { displayMoney, displayNumericDayMonth, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { FundOffers } from "@/types";
import { holdersBoughtPercent, preferenceCost, preferenceShare, sessionsLeftLabel } from "../lib/fund-offers";

type PreferenceOfferRowProps = { offer: FundOffers["preference"][number] };

/** A preferência do cotista numa emissão: quanto ele pode comprar antes dos outros, a que preço, e como anda a compra dos cotistas. */
export function PreferenceOfferRow({ offer }: PreferenceOfferRowProps) {
  const endsOn = displayNumericDayMonth(offer.preference_ends_on);

  return (
    <div className="grid grid-cols-[36px_minmax(0,1fr)_auto] items-center gap-x-3.5 gap-y-1.5 border-y border-border px-5 py-3.5">
      {/* Ícone */}
      <span className="row-span-5 grid size-9 place-items-center rounded-[10px] bg-warning-soft text-warning">
        <ShoppingCart className="size-4.5" />
      </span>

      {/* Gestora e prazo */}
      <div className="col-start-2 flex items-center gap-2 font-semibold">
        {offer.name} · emissão de {displayQuantity(offer.issuance_quotas)} cotas
        <Badge variant="warning" size="tag">
          <Clock />
          até {endsOn}
        </Badge>
      </div>
      <p className="col-start-2 text-[13px] text-muted-foreground">
        Você pode comprar até {displayQuantity(offer.my_left)} cotas a {displayMoney(offer.price)} antes de qualquer
        outro investidor: a mesma parte de {displayPercent(preferenceShare(offer), 1)} que você já tem. Custa até{" "}
        {displayMoney(preferenceCost(offer))}.
      </p>

      {/* Compra dos cotistas */}
      <Progress
        className="col-start-2 max-w-140"
        size="md"
        indicatorTone="fund"
        value={holdersBoughtPercent(offer)}
        aria-label="Cotas da emissão já compradas pelos cotistas"
      />
      <p className="col-start-2 text-xs text-muted-foreground">
        {displayQuantity(offer.holders_bought)} de {displayQuantity(offer.issuance_quotas)} cotas já compradas pelos
        cotistas · {sessionsLeftLabel(offer.sessions_left)}
      </p>
      <p className="col-start-2 flex items-center gap-1.5 text-xs text-muted-foreground">
        <Info className="size-3.5 shrink-0" />
        Depois de {endsOn}, o que sobrar fica {offer.leftover_sessions} pregões aberto a qualquer investidor
      </p>

      {/* Compra */}
      <Button
        className="col-start-3 row-span-5 row-start-1"
        variant="fund"
        size="sm"
        nativeButton={false}
        render={<Link to={`/funds/${offer.fund_id}?tab=quotas`} />}
      >
        <ShoppingCart />
        Comprar até {displayQuantity(offer.my_left)} cotas
      </Button>
    </div>
  );
}
