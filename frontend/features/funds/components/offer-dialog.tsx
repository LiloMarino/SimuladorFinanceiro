import { useState } from "react";
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
import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Spinner } from "@/shared/components/ui/spinner";
import { displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import { formatPositiveInteger } from "@/shared/lib/utils/format";
import { useOpenFundOffer } from "../hooks/mutations/useOpenFundOffer";
import { offerControl } from "../lib/fund-math";
import { ControlNotice } from "./control-notice";

type OfferDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fundId: number;
  fundName: string;
  /** Patrimônio por cota de hoje: o preço fixo da oferta */
  nav: number;
  /** As cotas do gestor e o total em circulação, para a conta do controle */
  managerQuotas: number;
  totalQuotas: number;
};

/** Oferta pública: o gestor escolhe quantas cotas novas a sala pode comprar ao patrimônio por cota, em 5 pregões. */
export function OfferDialog({
  open,
  onOpenChange,
  fundId,
  fundName,
  nav,
  managerQuotas,
  totalQuotas,
}: OfferDialogProps) {
  const [quotasText, setQuotasText] = useState("");
  const openOffer = useOpenFundOffer(fundId);
  const quotas = Number(quotasText);
  const valid = Number.isInteger(quotas) && quotas > 0;
  const control = offerControl(managerQuotas, totalQuotas, valid ? quotas : 0);

  const submit = () => openOffer.mutate({ quotas }, { onSuccess: () => onOpenChange(false) });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-145">
        <DialogHeader variant="divided">
          <DialogTitle>Oferta pública de {fundName}</DialogTitle>
          <DialogDescription>
            A sala tem 5 pregões para comprar cotas novas ao patrimônio por cota de hoje. Só nascem as cotas vendidas, e
            cada bot compra no máximo 20% da gestora.
          </DialogDescription>
        </DialogHeader>
        <DialogBody>
          <Field>
            <FieldLabel htmlFor="offer-quotas">Quantas cotas</FieldLabel>
            <Input
              id="offer-quotas"
              numeric
              inputMode="numeric"
              autoComplete="off"
              placeholder="Ex.: 800"
              value={quotasText}
              onChange={(event) => setQuotasText(formatPositiveInteger(event.target.value))}
            />
            <FieldDescription>
              Hoje existem {displayQuantity(String(totalQuotas))} cotas em circulação.
            </FieldDescription>
          </Field>
          <div>
            <KeyValueRow label="Preço fixo por cota (patrimônio por cota)" value={displayMoney(nav)} />
            <KeyValueRow label="Duração" value="5 pregões" />
            <KeyValueRow label="Se vender tudo, entra" value={valid ? displayMoney(quotas * nav) : "—"} />
          </div>
          {valid && (
            <ControlNotice
              keepsControl={control.keepsControl}
              title={control.keepsControl ? "Você mantém o controle" : "Você perde o controle"}
            >
              Se a sala comprar tudo, suas {displayQuantity(String(managerQuotas))} cotas serão{" "}
              {displayPercent(control.share, 1)} das {displayQuantity(String(totalQuotas + quotas))} cotas.{" "}
              {control.keepsControl
                ? "Passa dos 50%: você segue mandando na gestora."
                : "Abaixo de 50%, outro cotista pode passar à frente de você."}
            </ControlNotice>
          )}
        </DialogBody>
        <DialogFooter variant="divided">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button variant="fund" disabled={!valid || openOffer.isPending} onClick={submit}>
            {openOffer.isPending && <Spinner />}
            Abrir a oferta{valid ? ` de ${displayQuantity(String(quotas))} cotas` : ""}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
