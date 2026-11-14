import { useDeferredValue, useState } from "react";
import { MetricLabel } from "@/shared/components/metric-hint";
import { KeyValueRow } from "@/shared/components/key-value-row";
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
import { displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import { formatPositiveInteger } from "@/shared/lib/utils/format";
import { useAnnounceFundIssuance } from "../hooks/mutations/useAnnounceFundIssuance";
import { useFundIssuancePreview } from "../hooks/queries/useFundIssuancePreview";
import { PREFERENCE_RIGHT } from "../lib/fund-metrics";
import { ControlNotice } from "./control-notice";

type IssuanceDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fundId: number;
  fundName: string;
  /** Patrimônio por cota de hoje: o preço fixo da emissão */
  nav: number;
  totalQuotas: number;
};

/** Emissão de cotas novas: o gestor escolhe quantas, e o preço fica fixo no patrimônio por cota de hoje. */
export function IssuanceDialog({ open, onOpenChange, fundId, fundName, nav, totalQuotas }: IssuanceDialogProps) {
  const [quotasText, setQuotasText] = useState("");
  const quotas = Number(quotasText);
  const deferredQuotas = useDeferredValue(quotas);
  const { data: preview } = useFundIssuancePreview(fundId, deferredQuotas);
  const announce = useAnnounceFundIssuance(fundId);

  const valid = Number.isInteger(quotas) && quotas > 0;
  const overLimit = valid && preview !== undefined && quotas > Number(preview.limit);
  const ready = valid && preview !== undefined && deferredQuotas === quotas && !overLimit;

  const submit = () => {
    if (ready && !announce.isPending) {
      announce.mutate({ quotas }, { onSuccess: () => onOpenChange(false) });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-145">
        <DialogHeader variant="divided">
          <DialogTitle>Emitir cotas de {fundName}</DialogTitle>
          <DialogDescription>
            Os cotistas têm 10 pregões para comprar primeiro, na proporção do que já têm. Depois, 5 pregões de sobra
            abertos a todos. Só nascem as cotas vendidas, ao preço de hoje.
          </DialogDescription>
        </DialogHeader>
        <DialogBody>
          <Field data-invalid={overLimit}>
            <FieldLabel htmlFor="issuance-quotas">Quantas cotas novas</FieldLabel>
            <Input
              id="issuance-quotas"
              autoFocus
              numeric
              inputMode="numeric"
              autoComplete="off"
              placeholder="Ex.: 800"
              value={quotasText}
              aria-invalid={overLimit}
              onChange={(event) => setQuotasText(formatPositiveInteger(event.target.value))}
              onKeyDown={(event) => event.key === "Enter" && submit()}
            />
            {overLimit ? (
              <FieldError>
                Cada emissão vai até {displayQuantity(preview.limit)} cotas, o total que existe hoje.
              </FieldError>
            ) : (
              <FieldDescription>
                Hoje existem {displayQuantity(String(totalQuotas))} cotas em circulação.
              </FieldDescription>
            )}
          </Field>
          <div>
            <KeyValueRow label="Preço fixo por cota (patrimônio por cota)" value={displayMoney(nav)} />
            <KeyValueRow label="Duração" value="10 pregões de preferência + 5 de sobra" />
            <KeyValueRow
              label="Se vender tudo, entra no caixa"
              value={valid && preview ? displayMoney(preview.raised) : "—"}
            />
            {valid && preview && Number(preview.manager_rights) > 0 && (
              <KeyValueRow
                label={<MetricLabel metric={PREFERENCE_RIGHT} />}
                value={`${displayQuantity(preview.manager_rights)} cotas · ${displayMoney(preview.manager_cost)}`}
              />
            )}
          </div>
          {valid && preview && !overLimit && (
            <ControlNotice
              keepsControl={preview.keeps_control_if_skip}
              title={
                preview.keeps_control_if_skip
                  ? "Você mantém o controle"
                  : preview.keeps_control_if_buy
                    ? "Você só mantém o controle usando o seu direito"
                    : "Você perde o controle"
              }
            >
              Se você não comprar, suas cotas serão {displayPercent(preview.share_if_skip, 1)} das{" "}
              {displayQuantity(preview.total_after)} cotas (hoje, {displayPercent(preview.share_now, 1)}). Comprando o
              seu direito, ficam {displayPercent(preview.share_if_buy, 1)}.{" "}
              {preview.keeps_control_if_skip
                ? "Passa dos 50%: você segue mandando na gestora."
                : "Abaixo de 50%, outro cotista pode passar à frente de você."}
            </ControlNotice>
          )}
        </DialogBody>
        <DialogFooter variant="divided">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button variant="fund" disabled={!ready || announce.isPending} onClick={submit}>
            {announce.isPending && <Spinner />}
            Anunciar emissão{valid ? ` de ${displayQuantity(String(quotas))} cotas` : ""}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
