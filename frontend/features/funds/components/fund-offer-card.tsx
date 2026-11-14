import { Megaphone } from "lucide-react";
import type { ReactNode } from "react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Progress } from "@/shared/components/ui/progress";
import { displayIsoDate, displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { fundStage } from "../lib/fund-view";

/** Cartão da oferta no topo da página: em andamento (com as vendas até agora) ou encerrada (com o resultado). */
export function FundOfferCard({ fund, action }: { fund: FundDetails; action?: ReactNode }) {
  const stage = fundStage(fund);
  if (stage === "closed" || fund.offer_quotas === null) return null;

  const offered = Number(fund.offer_quotas);
  const sold = Number(fund.offer_sold ?? 0);
  const open = stage === "offer";

  return (
    <Card variant={open ? "info" : "default"}>
      <CardContent>
        <div className="grid gap-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <Megaphone className="size-4 text-primary" />
              <b className="text-[15px] font-semibold">
                {open ? "Oferta pública em andamento" : "Oferta pública encerrada"}
              </b>
              <Badge variant={open ? "success" : "secondary"} size="tag">
                {open
                  ? `pregão ${fund.offer_session ?? 1} de 5`
                  : fund.offer_closed_on
                    ? `em ${displayIsoDate(fund.offer_closed_on)}`
                    : "encerrada"}
              </Badge>
            </div>
            {action}
          </div>
          <Progress value={offered > 0 ? (sold / offered) * 100 : 0} aria-label="Cotas vendidas na oferta" />
          <p className="text-[13px] text-muted-foreground">
            <b className="font-mono font-semibold text-foreground">{displayQuantity(String(sold))}</b> de{" "}
            {displayQuantity(fund.offer_quotas)} cotas vendidas a{" "}
            {fund.offer_price === null ? "—" : displayMoney(fund.offer_price)} cada
            {fund.offer_raised !== null && <>, somando {displayMoney(fund.offer_raised)}</>}
            {open && fund.offer_ends_on && <>. Vai até {displayIsoDate(fund.offer_ends_on)}.</>}
          </p>
          {fund.offer_buyers && fund.offer_buyers.length > 0 && (
            <ul className="flex flex-wrap gap-x-4 gap-y-1.5">
              {fund.offer_buyers.map((buyer) => (
                <li
                  key={`${buyer.kind}-${buyer.user_id ?? buyer.nickname}`}
                  className="flex items-center gap-1.5 text-xs"
                >
                  <PlayerAvatar
                    nickname={buyer.nickname}
                    bot={buyer.kind !== "player"}
                    {...(buyer.color ? { color: buyer.color } : {})}
                    size="sm"
                  />
                  {buyer.nickname}
                  <span className="font-mono text-muted-foreground">{displayQuantity(buyer.quotas)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
