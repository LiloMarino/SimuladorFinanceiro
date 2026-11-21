import { useDeferredValue, useState } from "react";
import { InfoHint } from "@/shared/components/info-hint";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { QuantityShortcuts } from "@/shared/components/quantity-shortcuts";
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
import { InputGroup, InputGroupAddon, InputGroupInput, InputGroupText } from "@/shared/components/ui/input-group";
import { Spinner } from "@/shared/components/ui/spinner";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import { quantityOfShare } from "@/shared/lib/quantity-shortcuts";
import { formatPositiveInteger } from "@/shared/lib/utils/format";
import type { FundDetails } from "@/types";
import { useIssueDirectedFundQuotas } from "../hooks/mutations/useIssueDirectedFundQuotas";
import { useFundDirectedIssuancePreview } from "../hooks/queries/useFundDirectedIssuancePreview";
import {
  ceilingHint,
  destinationNote,
  directedActionLabel,
  directedBuyers,
  overCeiling,
  priceNote,
  shareNote,
} from "../lib/fund-directed";

type DirectedIssuanceDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fund: FundDetails;
};

// Valor do segmento "Você"; os demais segmentos têm o apelido do co-gestor
const SELF = "";

/** Emissão dirigida: cotas novas para o gestor ou para um co-gestor ativo, pagas do caixa pessoal de quem compra. */
export function DirectedIssuanceDialog({ open, onOpenChange, fund }: DirectedIssuanceDialogProps) {
  const [quotasText, setQuotasText] = useState("");
  const [buyerChoice, setBuyerChoice] = useState(SELF);
  const buyers = directedBuyers(fund.comanagers);
  // Um co-gestor que saiu depois da escolha devolve a compra ao próprio gestor
  const buyer = buyers.find((comanager) => comanager.nickname === buyerChoice) ?? null;
  const forMe = buyer === null;

  const quotas = Number(quotasText);
  const deferredQuotas = useDeferredValue(quotas);
  // A prévia de 1 cota já traz o teto, que os atalhos de porcentagem usam
  const { data: preview } = useFundDirectedIssuancePreview(fund.id, Math.max(deferredQuotas, 1));
  const issue = useIssueDirectedFundQuotas(fund.id);

  const valid = Number.isInteger(quotas) && quotas > 0;
  const overLimit = valid && preview !== undefined && overCeiling(quotas, preview.room);
  const noCash = valid && forMe && preview !== undefined && !preview.cash_enough;
  const ready = valid && preview !== undefined && deferredQuotas === quotas && !overLimit && !noCash;
  const hint = preview ? ceilingHint(preview) : null;

  const submit = () => {
    if (!ready || issue.isPending) return;
    issue.mutate(
      { quotas, buyer_nickname: buyer?.nickname ?? null },
      {
        onSuccess: () => {
          setQuotasText("");
          onOpenChange(false);
        },
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-145">
        <DialogHeader variant="divided">
          <DialogTitle>Emissão dirigida</DialogTitle>
          <DialogDescription>
            Cotas novas para você ou para um co-gestor, pagas do caixa pessoal de quem compra e liquidadas no mesmo
            pregão.
          </DialogDescription>
        </DialogHeader>
        <DialogBody>
          {/* Quem compra */}
          {buyers.length > 0 && (
            <Field>
              <FieldLabel id="directed-buyer-label">Para quem</FieldLabel>
              <ToggleGroup
                variant="segmented"
                aria-labelledby="directed-buyer-label"
                value={[buyerChoice]}
                onValueChange={(values) => values[0] !== undefined && setBuyerChoice(values[0])}
              >
                <ToggleGroupItem value={SELF}>Você</ToggleGroupItem>
                {buyers.map((comanager) => (
                  <ToggleGroupItem key={comanager.user_id} value={comanager.nickname}>
                    {comanager.nickname}
                  </ToggleGroupItem>
                ))}
              </ToggleGroup>
            </Field>
          )}

          {/* Quantidade */}
          <Field data-invalid={overLimit}>
            <FieldLabel htmlFor="directed-quotas">Quantas cotas</FieldLabel>
            <InputGroup>
              <InputGroupInput
                id="directed-quotas"
                autoFocus
                numeric
                inputMode="numeric"
                autoComplete="off"
                placeholder="Ex.: 1.000"
                value={quotasText}
                aria-invalid={overLimit}
                onChange={(event) => setQuotasText(formatPositiveInteger(event.target.value))}
                onKeyDown={(event) => event.key === "Enter" && submit()}
              />
              <InputGroupAddon align="inline-end">
                <InputGroupText>cotas</InputGroupText>
              </InputGroupAddon>
            </InputGroup>
            <QuantityShortcuts
              size="sm"
              className="*:flex-1"
              disabled={preview?.room == null}
              onPick={(share) => preview?.room != null && setQuotasText(quantityOfShare(preview.room, share, false))}
            />
            {overLimit && hint ? <FieldError>{hint}</FieldError> : hint && <FieldDescription>{hint}</FieldDescription>}
          </Field>

          {/* Preço */}
          <div>
            <KeyValueRow
              label={
                <span className="inline-flex items-center gap-1">
                  Preço por cota
                  <InfoHint label="O que é o preço de ranking">
                    O preço de ranking é o que o mercado paga pela cota hoje: quem compra na emissão dirigida não entra
                    abaixo dele.
                  </InfoHint>
                </span>
              }
              note={preview ? priceNote(preview) : undefined}
              value={preview ? displayMoney(preview.price) : "—"}
            />
          </div>

          {/* Prévia */}
          {valid && preview && (
            <div>
              {forMe ? (
                <KeyValueRow
                  label="Você paga"
                  note={`Do seu caixa pessoal, de ${displayMoney(preview.buyer_cash)}`}
                  value={displayMoney(preview.cost)}
                />
              ) : (
                <KeyValueRow
                  label={`${buyer.nickname} paga`}
                  note="Do caixa pessoal de quem compra, ao preço e dentro do teto de quando aceitar; o de hoje é só a referência"
                  value={displayMoney(preview.cost)}
                />
              )}
              <KeyValueRow
                label="Entra na gestora"
                note={destinationNote(preview.to_payable, preview.to_cash)}
                value={displayMoney(preview.cost)}
              />
              {forMe && (
                <KeyValueRow
                  label="Suas cotas"
                  note={shareNote(preview)}
                  value={`${displayQuantity(fund.my_quotas)} → ${displayQuantity(preview.my_quotas_after)}`}
                />
              )}
              <KeyValueRow
                label="Patrimônio por cota"
                note="Quem já tem cota não perde valor"
                value={`${displayMoney(preview.nav)} → ${displayMoney(preview.nav_after)}`}
              />
            </div>
          )}

          {noCash && (
            <Alert variant="destructive">
              <AlertTitle>O seu caixa pessoal não cobre</AlertTitle>
              <AlertDescription>
                Faltam {displayMoney(Number(preview.cost) - Number(preview.buyer_cash))} para pagar{" "}
                {displayQuantity(String(quotas))} cotas.
              </AlertDescription>
            </Alert>
          )}
        </DialogBody>
        <DialogFooter variant="divided">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button variant="fund" disabled={!ready || issue.isPending} onClick={submit}>
            {issue.isPending && <Spinner />}
            {directedActionLabel(valid ? quotas : 0, buyer?.nickname ?? null)}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
