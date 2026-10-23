import { useDeferredValue, useState } from "react";
import { TriangleAlert } from "lucide-react";
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
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { cn, normalizeNumberString } from "@/shared/lib/utils";
import { displayMoney, displayPercent, toCentsString } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import type { CreditLoan, PrepaymentMode } from "@/types";
import { usePayoffLoan } from "../hooks/mutations/usePayoffLoan";
import { usePrepayLoan } from "../hooks/mutations/usePrepayLoan";
import { usePrepaymentPreview } from "../hooks/queries/usePrepaymentPreview";
import { KeyValueRow } from "@/shared/components/key-value-row";

export type PrepayChoice = "part" | "all";

type PrepayDialogProps = {
  loan: CreditLoan;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Abre em "Amortizar uma parte" ou em "Quitar tudo" */
  initialChoice: PrepayChoice;
  /** Valor já preenchido, em reais (vem das sugestões de nota) */
  initialAmount?: string;
};

/** "Pagar antes": amortiza uma parte (encurta o prazo ou reduz a parcela) ou quita o empréstimo. */
export function PrepayDialog({ loan, open, onOpenChange, initialChoice, initialAmount }: PrepayDialogProps) {
  const [choice, setChoice] = useState<PrepayChoice>(initialChoice);
  const [amountText, setAmountText] = useState(() =>
    initialAmount ? formatMoney(toCentsString(initialAmount)) : "",
  );
  const [mode, setMode] = useState<PrepaymentMode>("SHORTEN_TERM");

  const amount = Number(normalizeNumberString(amountText)) || 0;
  const deferredAmount = useDeferredValue(amount);
  const { data: preview } = usePrepaymentPreview(loan.id, String(choice === "part" ? deferredAmount : 0));

  const prepay = usePrepayLoan(loan.id);
  const payoff = usePayoffLoan(loan.id);

  const remaining = loan.total_installments - loan.paid_installments;
  const close = () => onOpenChange(false);

  const cash = preview ? Number(preview.cash) : 0;
  const balance = preview ? Number(preview.balance) : Number(loan.balance);
  const payoffAmount = preview ? Number(preview.payoff_amount) : 0;
  const missingCash = Math.max(payoffAmount - cash, 0);

  const partError =
    amount > cash
      ? `Você tem ${displayMoney(cash)} em caixa.`
      : amount >= balance && amount > 0
        ? "Esse valor quita o empréstimo: use Quitar tudo."
        : null;
  const canPrepay = preview !== undefined && amount > 0 && partError === null && deferredAmount === amount;
  const canPayoff = preview !== undefined && missingCash === 0;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-130">
        <DialogHeader variant="divided">
          <DialogTitle>Empréstimo {loan.number} · pagar antes</DialogTitle>
          <DialogDescription>
            {displayMoney(loan.principal)} em {loan.total_installments} parcelas, a {displayPercent(loan.annual_rate)} ao
            ano · {loan.paid_installments} de {loan.total_installments} pagas
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-4">
            <ToggleGroup
              variant="segmented"
              aria-label="Como pagar antes"
              value={[choice]}
              onValueChange={(values) => values[0] && setChoice(values[0] as PrepayChoice)}
            >
              <ToggleGroupItem value="part">Amortizar uma parte</ToggleGroupItem>
              <ToggleGroupItem value="all">Quitar tudo</ToggleGroupItem>
            </ToggleGroup>

            {choice === "part" ? (
              <>
                {/* Quanto pagar */}
                <Field data-invalid={amount > 0 && partError !== null}>
                  <FieldLabel htmlFor="prepay-amount">Quanto pagar agora</FieldLabel>
                  <Input
                    id="prepay-amount"
                    fieldSize="xl"
                    numeric
                    inputMode="decimal"
                    value={amountText}
                    aria-invalid={amount > 0 && partError !== null}
                    onChange={(event) => setAmountText(formatMoney(event.target.value))}
                  />
                  {amount > 0 && partError ? (
                    <FieldError>{partError}</FieldError>
                  ) : (
                    <FieldDescription>
                      Saldo devedor <span className="font-mono">{displayMoney(balance)}</span> · caixa{" "}
                      <span className="font-mono">{displayMoney(cash)}</span>
                    </FieldDescription>
                  )}
                </Field>

                {/* O que fazer com o que sobra */}
                <div className="grid gap-2">
                  <span className="text-sm font-medium">O que fazer com o que sobra</span>
                  <RadioGroup value={mode} onValueChange={(value) => setMode(value as PrepaymentMode)}>
                    <PrepayOption
                      value="SHORTEN_TERM"
                      selected={mode === "SHORTEN_TERM"}
                      title="Diminuir o prazo"
                      interestSaved={preview?.shorten_term?.interest_saved}
                      detail={
                        preview?.shorten_term &&
                        `Parcela segue ${displayMoney(preview.shorten_term.installment)}; faltam ${preview.shorten_term.installments_remaining} em vez de ${remaining}`
                      }
                    />
                    <PrepayOption
                      value="REDUCE_INSTALLMENT"
                      selected={mode === "REDUCE_INSTALLMENT"}
                      title="Diminuir a parcela"
                      interestSaved={preview?.reduce_installment?.interest_saved}
                      detail={
                        preview?.reduce_installment &&
                        `Seguem ${preview.reduce_installment.installments_remaining} parcelas, de ${displayMoney(preview.reduce_installment.installment)}`
                      }
                    />
                  </RadioGroup>
                </div>
                <span className="text-xs text-muted-foreground">
                  Pagar antes abate os juros que ainda não correram (Código de Defesa do Consumidor, art. 52).
                </span>
              </>
            ) : (
              <>
                {/* Quitar */}
                <div>
                  <KeyValueRow
                    label={`${preview?.payoff_installments ?? remaining} parcelas restantes`}
                    value={preview ? displayMoney(preview.payoff_remaining_payments) : "—"}
                  />
                  <KeyValueRow
                    label="Juro que ainda não correu"
                    value={preview ? `−${displayMoney(preview.payoff_interest_saved)}` : "—"}
                  />
                  <KeyValueRow total label="Para quitar hoje" value={preview ? displayMoney(payoffAmount) : "—"} />
                </div>
                {missingCash > 0 && (
                  <Alert variant="destructive">
                    <TriangleAlert />
                    <AlertTitle>Falta {displayMoney(missingCash)} no caixa</AlertTitle>
                    <AlertDescription>
                      Você tem {displayMoney(cash)}. Venda algo antes ou amortize uma parte agora.
                    </AlertDescription>
                  </Alert>
                )}
              </>
            )}
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={close}>
            Cancelar
          </Button>
          {choice === "part" ? (
            <Button
              disabled={!canPrepay || prepay.isPending}
              onClick={() =>
                prepay.mutate({ amount: normalizeNumberString(amountText), mode }, { onSuccess: close })
              }
            >
              Pagar {displayMoney(amount)}
            </Button>
          ) : (
            <Button disabled={!canPayoff || payoff.isPending} onClick={() => payoff.mutate(undefined, { onSuccess: close })}>
              Quitar {preview ? displayMoney(payoffAmount) : ""}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

type PrepayOptionProps = {
  value: PrepaymentMode;
  selected: boolean;
  title: string;
  interestSaved: string | undefined;
  detail: string | undefined | null | false;
};

function PrepayOption({ value, selected, title, interestSaved, detail }: PrepayOptionProps) {
  return (
    <label
      className={cn(
        "grid cursor-pointer grid-cols-[auto_1fr_auto] items-center gap-x-2.5 gap-y-0.5 rounded-[10px] border px-3 py-2.5 text-[13px]",
        selected && "border-primary bg-info-soft/60 ring-1 ring-primary",
      )}
    >
      <RadioGroupItem value={value} className="row-span-2" />
      <b className="font-semibold">{title}</b>
      <span className="font-mono font-semibold text-success">
        {interestSaved === undefined ? "—" : `−${displayMoney(interestSaved)} de juro`}
      </span>
      <span className="col-span-2 col-start-2 text-xs text-muted-foreground">{detail || "Digite um valor para ver o efeito"}</span>
    </label>
  );
}
