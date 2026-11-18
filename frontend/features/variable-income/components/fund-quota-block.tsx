import { ControlNotice } from "@/shared/components/control-notice";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { Button } from "@/shared/components/ui/button";
import { fundStage } from "@/shared/lib/fund-view";
import { displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { quotaOrderOutlook } from "../lib/fund-quota-order";

type FundQuotaBlockProps = {
  fund: FundDetails;
  action: "buy" | "sell";
  /** Preço por cota da ordem, da prévia */
  price: number;
  quantity: number;
  disabled: boolean;
  /** Vende `size` cotas pelo mesmo tipo de ordem da boleta */
  onSell: (size: number) => void;
};

/** O que a ordem faz com a cota: ágio pago, posição depois e, para o gestor, o controle da gestora. */
export function FundQuotaBlock({ fund, action, price, quantity, disabled, onSell }: FundQuotaBlockProps) {
  const buying = action === "buy";
  const outlook = quotaOrderOutlook({
    action,
    mine: Number(fund.my_quotas),
    total: Number(fund.quotas),
    nav: fund.nav === null ? null : Number(fund.nav),
    price,
    quantity,
    issued: fundStage(fund) === "offer",
    manager: fund.my_role === "manager",
  });

  return (
    <div className="grid gap-3 border-t border-muted pt-3">
      <div>
        {outlook.premiumPaid !== null && outlook.premiumRate !== null && (
          <KeyValueRow
            label={`Ágio pago (${displayPercent(outlook.premiumRate, 1)})`}
            value={displayMoney(outlook.premiumPaid)}
          />
        )}
        <KeyValueRow
          label={buying ? "Você passa a ter" : "Você fica com"}
          value={`${displayQuantity(String(outlook.after.quotas))} cotas · ${displayPercent(outlook.after.share, 1)}`}
        />
      </div>

      {outlook.losesControl && quantity > 0 && (
        <>
          <ControlNotice keepsControl={false} title="Você perde o controle">
            Com {displayQuantity(String(outlook.after.quotas))} cotas você fica com{" "}
            {displayPercent(outlook.after.share, 1)}, abaixo dos 50%. Sem eles, outro cotista pode passar à frente de
            você.
          </ControlNotice>
          <Button
            type="button"
            variant="fund"
            disabled={outlook.sellable === 0 || disabled}
            onClick={() => onSell(outlook.sellable)}
          >
            Vender só {displayQuantity(String(outlook.sellable))}
          </Button>
        </>
      )}
    </div>
  );
}
