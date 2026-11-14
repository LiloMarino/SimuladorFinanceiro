import { useState } from "react";
import { Info } from "lucide-react";
import { toast } from "sonner";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
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
import { Field, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Spinner } from "@/shared/components/ui/spinner";
import { DisabledHint } from "@/shared/components/disabled-hint";
import { AmountShortcuts } from "@/shared/components/amount-shortcuts";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { TradeLockNotice } from "@/shared/components/trade-lock-notice";
import { useBuyFixedIncome } from "@/shared/hooks/mutations/useBuyFixedIncome";
import { useFixedIncomeProjection } from "@/shared/hooks/queries/useFixedIncomeProjection";
import { AccountOriginNotice } from "@/shared/components/account-origin-notice";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useTradeLock } from "@/shared/hooks/useTradeLock";
import { normalizeNumberString } from "@/shared/lib/utils";
import { formatMoney } from "@/shared/lib/utils/format";
import { displayMoney } from "@/shared/lib/utils/display";
import type { TreasuryTitle } from "@/types";
import { baseRateCaption, displayDay, displayMonthYear, percentOf, pointsOf, treasuryRateLabel } from "../lib/treasury";

type BuyDialogProps = {
  title: TreasuryTitle;
  currentDate: string;
  onClose: () => void;
};

/** A compra de um título: o valor, a taxa que fica travada e o que o título devolve se for até o vencimento. */
export function BuyDialog({ title, currentDate, onClose }: BuyDialogProps) {
  const [amountText, setAmountText] = useState(formatMoney("0"));
  const [touched, setTouched] = useState(false);
  const amountString = normalizeNumberString(amountText);
  const amount = Number(amountString) || 0;

  const { data: quote } = useFixedIncomeProjection(title.asset_uuid, amountString, currentDate);
  const buy = useBuyFixedIncome(title.asset_uuid);
  const tradeLock = useTradeLock();
  const locked = tradeLock !== null;
  // Com uma gestora ativa a ordem sai do caixa dela
  const { fund } = useActiveAccount();

  const cash = quote ? Number(quote.cash_before) : 0;
  const zero = amount <= 0;
  const overCash = quote !== undefined && amount > cash;
  const invalid = zero || overCash;
  const showError = touched && invalid;
  // O motivo do botão apagado: o que falta para investir
  const blockedReason = zero
    ? "Digite quanto quer investir."
    : overCash
      ? `Você tem ${displayMoney(cash)} em caixa.`
      : null;

  const canSubmit = !locked && !invalid && !buy.isPending;

  const submit = () =>
    buy.mutate(
      { quantity: amountString },
      {
        onSuccess: () => {
          toast.success(`${displayMoney(amount)} investidos no ${title.name}`);
          onClose();
        },
      },
    );

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-130">
        <DialogHeader variant="divided">
          <DialogTitle>Investir no {title.name}</DialogTitle>
          <DialogDescription>
            Vence em {displayDay(title.maturity_date)} · à venda até {displayMonthYear(title.sold_until)}
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          {tradeLock ? <TradeLockNotice lock={tradeLock} /> : <AccountOriginNotice />}

          {/* Valor */}
          <form
            id="treasury-buy-form"
            onSubmit={(event) => {
              event.preventDefault();
              if (canSubmit) submit();
            }}
          >
            <Field data-invalid={showError}>
              <FieldLabel htmlFor="treasury-buy-amount">Quanto investir</FieldLabel>
              <Input
                id="treasury-buy-amount"
                fieldSize="xl"
                numeric
                inputMode="decimal"
                disabled={locked}
                value={amountText}
                aria-invalid={showError}
                onChange={(event) => {
                  setTouched(true);
                  setAmountText(formatMoney(event.target.value));
                }}
              />
              {/* Atalhos: as frações valem sobre o caixa */}
              <AmountShortcuts
                kind="treasury-buy"
                defaultMode="percent"
                value={amountText}
                onChange={(text) => {
                  setTouched(true);
                  setAmountText(text);
                }}
                max={quote ? cash : undefined}
                baseLabel="do caixa"
                limitLabel="caixa"
                fixed={[1000, 5000, 10000]}
                disabled={locked}
                error={
                  showError && (zero ? "Digite quanto quer investir." : `Você tem ${displayMoney(cash)} em caixa.`)
                }
              />
            </Field>
          </form>

          {/* Taxa travada */}
          <div className="flex items-center justify-between gap-3 rounded-lg border border-border px-3.5 py-3">
            <div className="grid gap-0.5">
              <span className="text-xs font-medium text-muted-foreground">Taxa travada na compra</span>
              <span className="text-xs text-muted-foreground">
                {Number(title.premium) === 0 ? (
                  "0 de prêmio"
                ) : (
                  <>
                    {baseRateCaption(title.rate_index, title.base_rate)}{" "}
                    <b className="font-semibold text-warning">{pointsOf(title.premium)} prêmio</b>
                  </>
                )}{" "}
                · revista todo mês para quem compra depois
              </span>
            </div>
            <b className="font-mono text-lg font-semibold whitespace-nowrap">
              {treasuryRateLabel(title.rate_index, title.rate)}
            </b>
          </div>

          {/* Se esperar até o vencimento */}
          <div className="grid gap-1 rounded-lg border border-info-border bg-info-soft/50 px-3.5 py-3">
            <b className="text-[13px] font-semibold">
              Se esperar até {quote ? displayDay(quote.redemption_date) : displayDay(title.maturity_date)}
            </b>
            <div>
              <KeyValueRow
                label="Valor no vencimento"
                value={quote?.gross_amount && !zero ? displayMoney(quote.gross_amount) : "—"}
              />
              <KeyValueRow
                label={`IR, ${quote ? percentOf(quote.income_tax_rate) : "—"} do ganho`}
                value={quote?.income_tax && !zero ? displayMoney(quote.income_tax) : "—"}
              />
              <KeyValueRow
                total
                label="Você recebe"
                value={quote?.net_amount && !zero ? displayMoney(quote.net_amount) : "—"}
              />
            </div>
          </div>

          <Alert variant="info">
            <Info />
            <AlertTitle>Dá para vender antes, pelo preço do dia</AlertTitle>
            <AlertDescription>
              {title.rate_index === "SELIC"
                ? "O Tesouro Selic vale o que acumulou: vender antes não tem perda nem ganho de marcação."
                : "Se a taxa do Tesouro subir depois da sua compra, o título vale menos até o vencimento; se cair, vale mais."}
            </AlertDescription>
          </Alert>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <DisabledHint reason={locked ? null : blockedReason}>
            <Button type="submit" form="treasury-buy-form" variant={fund ? "fund" : "default"} disabled={!canSubmit}>
              {buy.isPending && <Spinner />}
              {invalid ? "Investir" : `Investir ${displayMoney(amount)}`}
            </Button>
          </DisabledHint>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
