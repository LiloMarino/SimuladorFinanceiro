import { useState } from "react";
import { toast } from "sonner";
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
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Spinner } from "@/shared/components/ui/spinner";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { TradeLockNotice } from "@/shared/components/trade-lock-notice";
import { useTradeLock } from "@/shared/hooks/useTradeLock";
import { normalizeNumberString } from "@/shared/lib/utils";
import { formatMoney } from "@/shared/lib/utils/format";
import { displayMoney } from "@/shared/lib/utils/display";
import type { TreasuryPosition, TreasurySaleQuote } from "@/types";
import { useSellTreasury } from "../hooks/mutations/useSellTreasury";
import { useTreasurySaleQuote } from "../hooks/queries/useTreasurySaleQuote";
import { displayDay, displayGain, percentOf, shareOfMoney, termLabel, treasuryRateLabel } from "../lib/treasury";
import { ShareShortcuts } from "./share-shortcuts";

type SellDialogProps = {
  position: TreasuryPosition;
  currentDate: string;
  onClose: () => void;
};

const orDash = (value: string | null | undefined, format: (value: string) => string) =>
  value === null || value === undefined ? "—" : format(value);

/** O que a taxa fez com o preço do título desde a compra, em uma frase. */
function marketSentence(position: TreasuryPosition) {
  const bought = Number(position.bought_rate);
  const today = Number(position.today_rate);
  const rates = `de ${treasuryRateLabel(position.asset.rate_index, position.bought_rate)} para ${treasuryRateLabel(position.asset.rate_index, position.today_rate)}`;
  if (today > bought)
    return `A taxa subiu ${rates} desde a sua compra: o título vale menos que a curva, então vender hoje abre mão de parte do ganho.`;
  if (today < bought)
    return `A taxa caiu ${rates} desde a sua compra: o título vale mais que a curva, e vender hoje realiza esse ganho a mais.`;
  return "A taxa de hoje é a mesma da sua compra: o preço está na curva.";
}

/** A venda de um título pelo preço de hoje, inteiro ou em parte, ao lado de esperar o vencimento. */
export function SellDialog({ position, currentDate, onClose }: SellDialogProps) {
  const { asset } = position;
  const selic = asset.rate_index === "SELIC";
  // `all` marca a posição inteira: o campo mostra o valor de mercado e o envio vai sem valor
  const [all, setAll] = useState(true);
  const [partText, setPartText] = useState(formatMoney("0"));
  const amountText = all ? formatMoney(shareOfMoney(position.market_value, 1)) : partText;
  const partString = normalizeNumberString(partText);

  // Vender tudo cota o valor de mercado inteiro da posição
  const gross = all ? position.market_value : partString;
  const { data: latestQuote } = useTreasurySaleQuote(asset.asset_uuid, gross, currentDate);
  const sell = useSellTreasury(asset.asset_uuid);
  const tradeLock = useTradeLock();

  const max = Number(position.market_value);
  const partAmount = Number(partString) || 0;
  const overMax = !all && partAmount > max;
  const empty = !all && partAmount <= 0;
  // Sem valor digitado não há venda a cotar: o resumo fica em branco
  const quote = empty ? undefined : latestQuote;
  const invalid = tradeLock !== null || overMax || empty || !quote || quote.net_amount === null;

  const net = quote?.net_amount;

  // Tudo vende o título inteiro; as frações valem sobre o valor de mercado da posição
  const fillShare = (share: number) => {
    setAll(share === 1);
    setPartText(formatMoney(shareOfMoney(position.market_value, share)));
  };

  const submit = () =>
    sell.mutate(
      { gross: all ? null : partString },
      {
        onSuccess: () => {
          toast.success(`${asset.name} vendido`);
          onClose();
        },
      },
    );

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-150">
        <DialogHeader variant="divided">
          <DialogTitle>Vender o {asset.name}</DialogTitle>
          <DialogDescription>
            Comprado em {displayDay(position.first_applied_date)}
            {selic
              ? all
                ? ""
                : " · venda de uma parte"
              : ` a ${treasuryRateLabel(asset.rate_index, position.bought_rate)}`}
            {asset.rate_index === "IPCA" && " ao ano"}
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          {tradeLock && <TradeLockNotice lock={tradeLock} />}

          {/* Quanto vender */}
          <Field data-invalid={overMax}>
            <FieldLabel htmlFor="treasury-sell-amount">Quanto vender</FieldLabel>
            <div className="flex gap-1.5">
              <Input
                id="treasury-sell-amount"
                fieldSize="xl"
                numeric
                inputMode="decimal"
                aria-invalid={overMax}
                value={amountText}
                onChange={(event) => {
                  setAll(false);
                  setPartText(formatMoney(event.target.value));
                }}
              />
              <ShareShortcuts disabled={tradeLock !== null} onPick={fillShare} />
            </div>
            {overMax ? (
              <FieldError>Você tem {displayMoney(max)} nele.</FieldError>
            ) : (
              <FieldDescription>
                Você tem {displayMoney(max)} nele.
                {!all && quote?.remaining != null && ` Fica ${displayMoney(quote.remaining)}.`}
              </FieldDescription>
            )}
          </Field>

          {selic ? (
            <SelicSummary quote={quote} />
          ) : (
            <MarketSummary position={position} quote={quote} currentDate={currentDate} />
          )}
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button variant="dark" disabled={invalid || sell.isPending} onClick={submit}>
            {sell.isPending && <Spinner />}
            {net ? `Vender por ${displayMoney(net)}` : "Vender"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function SelicSummary({ quote }: { quote: TreasurySaleQuote | undefined }) {
  return (
    <div className="grid gap-3">
      <div>
        <KeyValueRow
          label="Valor vendido"
          value={orDash(quote?.applied_amount == null ? null : quote.amount, displayMoney)}
        />
        <KeyValueRow
          label={`IR, ${quote ? percentOf(quote.income_tax_rate) : "—"} do ganho da parte`}
          value={orDash(quote?.income_tax, displayMoney)}
        />
        <KeyValueRow total label="Você recebe" value={orDash(quote?.net_amount, displayMoney)} />
      </div>
      <span className="text-xs text-muted-foreground">
        O Tesouro Selic vale o que acumulou: a taxa de hoje quase não mexe no preço dele, então não há marcação.
      </span>
    </div>
  );
}

type MarketSummaryProps = {
  position: TreasuryPosition;
  quote: TreasurySaleQuote | undefined;
  currentDate: string;
};

function MarketSummary({ position, quote, currentDate }: MarketSummaryProps) {
  const iof = quote?.iof;
  const maturity = quote?.maturity_date ?? position.asset.maturity_date;

  return (
    <div className="grid gap-3">
      <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs leading-normal text-muted-foreground">
        {marketSentence(position)}
      </p>
      <div className="grid grid-cols-2 gap-3">
        {/* Vender hoje */}
        <div className="grid content-start gap-1 rounded-lg border border-info-border bg-info-soft/50 px-3.5 py-3">
          <b className="text-[13px] font-semibold">Vender hoje</b>
          <KeyValueRow label="Aplicado" value={orDash(quote?.applied_amount, displayMoney)} />
          <KeyValueRow label="Rendeu" value={orDash(quote?.yield_amount, displayGain)} />
          <KeyValueRow label="Marcação" value={orDash(quote?.mark, displayGain)} />
          {iof != null && Number(iof) > 0 && <KeyValueRow label="IOF" value={displayMoney(iof)} />}
          <KeyValueRow
            label={`IR, ${quote ? percentOf(quote.income_tax_rate) : "—"} do ganho`}
            value={orDash(quote?.income_tax, displayMoney)}
          />
          <KeyValueRow total label="Você recebe" value={orDash(quote?.net_amount, displayMoney)} />
        </div>

        {/* Esperar o vencimento */}
        <div className="grid content-start gap-1 rounded-lg border border-border px-3.5 py-3">
          <b className="text-[13px] font-semibold">Esperar até {displayDay(maturity)}</b>
          <KeyValueRow label="Valor no vencimento" value={orDash(quote?.maturity_gross_amount, displayMoney)} />
          <KeyValueRow label="Marcação" value={<span className="text-faint-foreground">zero</span>} />
          <KeyValueRow label="IR" value={orDash(quote?.maturity_income_tax, displayMoney)} />
          <KeyValueRow total label="Você recebe" value={orDash(quote?.maturity_net_amount, displayMoney)} />
          <span className="text-xs text-muted-foreground">em {termLabel(maturity, currentDate)}</span>
        </div>
      </div>
    </div>
  );
}
