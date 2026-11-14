import { Undo2 } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Progress } from "@/shared/components/ui/progress";
import { Spinner } from "@/shared/components/ui/spinner";
import { displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { useCancelFundBuyback } from "../hooks/mutations/useCancelFundBuyback";

type FundBuybackCardProps = { fund: FundDetails; viewer: boolean };

const STATE_LABEL = { open: "em aberto", done: "concluída", canceled: "cancelada" } as const;

/** Cartão da recompra: quanto já foi comprado e queimado, e o botão de cancelar o resto para o gestor. */
export function FundBuybackCard({ fund, viewer }: FundBuybackCardProps) {
  const cancel = useCancelFundBuyback(fund.id);
  const buyback = fund.buyback;
  if (buyback === null) return null;

  const open = buyback.state === "open";
  const quantity = Number(buyback.quantity);
  const bought = Number(buyback.bought);

  return (
    <Card variant={open ? "info" : "default"}>
      <CardContent>
        <div className="grid gap-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <Undo2 className="size-4 text-primary" />
              <b className="text-[15px] font-semibold">{open ? "Recompra em aberto" : "Recompra de cotas"}</b>
              <Badge variant={open ? "success" : "secondary"} size="tag">
                {STATE_LABEL[buyback.state]}
              </Badge>
            </div>
            {open && !viewer && (
              <Button variant="outline" size="sm" disabled={cancel.isPending} onClick={() => cancel.mutate()}>
                {cancel.isPending && <Spinner />}
                Cancelar o resto
              </Button>
            )}
          </div>
          <Progress value={quantity > 0 ? (bought / quantity) * 100 : 0} aria-label="Cotas já recompradas" />
          <p className="text-[13px] text-muted-foreground">
            <b className="font-mono font-semibold text-foreground">{displayQuantity(buyback.bought)}</b> de{" "}
            {displayQuantity(buyback.quantity)} cotas recompradas, pagando {displayMoney(buyback.paid)} ao todo. A
            gestora paga até {displayMoney(buyback.max_price)} por cota, e as cotas compradas deixam de existir.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
