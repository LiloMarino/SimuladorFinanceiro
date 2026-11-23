import { Info } from "lucide-react";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { displayMoney, displayMonthShort, displayPercent, parseLocalDate } from "@/shared/lib/utils/display";
import { useRedeemPension } from "../hooks/mutations/useRedeemPension";
import { monthsText, nextBracketGain, planTime, redeemSplit, type RetireeMechanic } from "../lib/pension";
import { REDEEM_TAX } from "../lib/profession-metrics";

type RedeemPensionDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mechanic: RetireeMechanic;
  amount: number;
  onRedeemed: () => void;
};

/** "Resgatar da previdência": o IR da faixa de hoje, o que cai no caixa e o que esperar pela próxima faixa deixaria a mais. */
export function RedeemPensionDialog({ open, onOpenChange, mechanic, amount, onRedeemed }: RedeemPensionDialogProps) {
  const redeem = useRedeemPension();
  const { tax, net } = redeemSplit(amount, mechanic.redeem_rate);
  const wait = nextBracketGain(mechanic, amount);

  const confirm = () =>
    redeem.mutate(
      { amount: amount.toFixed(2) },
      {
        onSuccess: () => {
          onRedeemed();
          onOpenChange(false);
        },
      },
    );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-130">
        <DialogHeader variant="divided">
          <DialogTitle>Resgatar {displayMoney(amount)} da previdência</DialogTitle>
          <DialogDescription>Confira antes de confirmar: o IR cai com o tempo no plano.</DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-4">
            <div>
              <KeyValueRow label="Valor resgatado" value={displayMoney(amount)} />
              <KeyValueRow
                label={
                  <span className="inline-flex items-center gap-1">
                    IR regressivo <MetricHint metric={REDEEM_TAX} />
                  </span>
                }
                note={`${displayPercent(mechanic.redeem_rate, 0)}: o saldo está no plano há ${planTime(mechanic.months_in_plan)}`}
                value={`−${displayMoney(tax)}`}
              />
              <KeyValueRow total label="Cai no caixa" value={displayMoney(net)} />
            </div>

            {/* A tabela do IR pelo tempo no plano */}
            <div>
              <h3 className="pb-1 text-[13px] font-semibold">A tabela do IR pelo tempo no plano</h3>
              {mechanic.brackets.map((bracket) => (
                <KeyValueRow
                  key={bracket.label}
                  label={bracket.label}
                  value={displayPercent(bracket.rate, 0)}
                  className={bracket.current ? "font-semibold" : ""}
                />
              ))}
            </div>

            {wait && (
              <Alert variant="info">
                <Info />
                <AlertDescription>
                  <b className="font-semibold">
                    Em {monthsText(wait.months)} o IR cai para {displayPercent(wait.rate, 0)}.
                  </b>{" "}
                  Esperar até {displayMonthShort(wait.on)} {parseLocalDate(wait.on).getFullYear()} deixa{" "}
                  {displayMoney(wait.gain)} a mais no caixa.
                </AlertDescription>
              </Alert>
            )}
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Esperar
          </Button>
          <Button onClick={confirm} disabled={redeem.isPending}>
            Resgatar {displayMoney(net)} líquido
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
