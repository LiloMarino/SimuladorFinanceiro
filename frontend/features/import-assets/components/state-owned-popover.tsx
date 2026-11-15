import { useState } from "react";
import { Landmark } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Popover, PopoverContent, PopoverHeader, PopoverTitle, PopoverTrigger } from "@/shared/components/ui/popover";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { STATE_LEVER_LABEL, STATE_LEVERS } from "@/shared/lib/state-lever";
import { normalizeNumberString } from "@/shared/lib/utils";
import type { StateLever, StateOwnedStock } from "@/types";
import { useMarkStateOwned } from "../hooks/mutations/useMarkStateOwned";
import { useUnmarkStateOwned } from "../hooks/mutations/useUnmarkStateOwned";
import { useSegmentSuggestion } from "../hooks/queries/useSegmentSuggestion";
import { useStateOwnedStock } from "../hooks/queries/useStateOwnedStock";

/** Fatia do governo numa empresa que já existe: o governo guarda 51% ou mais. */
const DEFAULT_SHARE_PERCENT = "51";

type StateOwnedPopoverProps = {
  ticker: string;
};

/** O botão "Estatal" do ativo: marca a empresa como estatal, com a fatia do governo, as ações e a alavanca do preço. */
export function StateOwnedPopover({ ticker }: StateOwnedPopoverProps) {
  const { data: owned, isPending } = useStateOwnedStock(ticker);
  const { data: suggestion } = useSegmentSuggestion(ticker);
  const [open, setOpen] = useState(false);

  if (isPending) return null;

  // A marcação salva vale; sem ela, a sugestão do yFinance preenche as ações e a alavanca
  const initial = owned
    ? {
        share: String(Number((Number(owned.government_share) * 100).toFixed(3))).replace(".", ","),
        shares: String(owned.shares),
        lever: owned.lever,
      }
    : {
        share: DEFAULT_SHARE_PERCENT,
        shares: suggestion?.shares_outstanding ? String(suggestion.shares_outstanding) : "",
        lever: suggestion?.lever ?? null,
      };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger render={<Button variant="outline" size="sm" />}>
        <Landmark data-icon="inline-start" />
        {owned ? `Estatal · ${initial.share}%` : "Estatal"}
      </PopoverTrigger>
      <PopoverContent align="start" className="w-88">
        <PopoverHeader>
          <PopoverTitle>Empresa estatal</PopoverTitle>
          <p className="text-xs text-muted-foreground">
            O governo da partida passa a ser dono dessa fatia da empresa: ela paga dividendo ao Tesouro e, com a
            alavanca, o presidente pode segurar o preço dela.
          </p>
        </PopoverHeader>
        <StateOwnedForm ticker={ticker} initial={initial} marked={!!owned} onClose={() => setOpen(false)} />
      </PopoverContent>
    </Popover>
  );
}

type StateOwnedFormProps = {
  ticker: string;
  initial: { share: string; shares: string; lever: StateOwnedStock["lever"] };
  marked: boolean;
  onClose: () => void;
};

function StateOwnedForm({ ticker, initial, marked, onClose }: StateOwnedFormProps) {
  const [share, setShare] = useState(initial.share);
  const [shares, setShares] = useState(initial.shares);
  const [lever, setLever] = useState<StateLever | null>(initial.lever);

  const mark = useMarkStateOwned(ticker);
  const unmark = useUnmarkStateOwned(ticker);
  const busy = mark.isPending || unmark.isPending;

  const sharePercent = Number(normalizeNumberString(share));
  const sharesCount = Number(shares);
  const valid = sharePercent > 0 && sharePercent <= 100 && sharesCount > 0;

  return (
    <div className="grid gap-3">
      <div className="grid grid-cols-2 gap-3">
        <Field>
          <FieldLabel htmlFor={`state-share-${ticker}`}>Fatia do governo (%)</FieldLabel>
          <Input
            id={`state-share-${ticker}`}
            numeric
            inputMode="decimal"
            value={share}
            onChange={(event) => setShare(event.target.value)}
          />
        </Field>
        <Field>
          <FieldLabel htmlFor={`state-shares-${ticker}`}>Ações da empresa</FieldLabel>
          <Input
            id={`state-shares-${ticker}`}
            numeric
            inputMode="numeric"
            value={shares}
            onChange={(event) => setShares(event.target.value.replace(/\D/g, ""))}
          />
        </Field>
      </div>

      <Field>
        <FieldLabel>Alavanca do preço</FieldLabel>
        <ToggleGroup
          variant="segmented"
          aria-label="Alavanca do preço"
          className="w-full"
          value={lever ? [lever] : []}
          onValueChange={(values) => setLever(STATE_LEVERS.find((option) => option === values[0]) ?? null)}
        >
          {STATE_LEVERS.map((option) => (
            <ToggleGroupItem key={option} value={option} className="flex-1">
              {STATE_LEVER_LABEL[option]}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
        <FieldDescription>Sem alavanca, a estatal paga dividendo mas não tem preço a segurar.</FieldDescription>
      </Field>

      <div className="flex items-center justify-between gap-2">
        {marked ? (
          <Button
            variant="link-destructive"
            size="sm"
            disabled={busy}
            onClick={() => unmark.mutate(undefined, { onSuccess: onClose })}
          >
            Tirar marcação
          </Button>
        ) : (
          <span />
        )}
        <div className="flex gap-2">
          <Button variant="outline" size="sm" disabled={busy} onClick={onClose}>
            Cancelar
          </Button>
          <Button
            size="sm"
            disabled={busy || !valid}
            onClick={() =>
              mark.mutate(
                { government_share: String(sharePercent / 100), shares: sharesCount, lever },
                { onSuccess: onClose },
              )
            }
          >
            Salvar
          </Button>
        </div>
      </div>
    </div>
  );
}
