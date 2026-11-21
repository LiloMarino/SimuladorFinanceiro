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
import { Field, FieldContent, FieldDescription, FieldLabel, FieldTitle } from "@/shared/components/ui/field";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { Spinner } from "@/shared/components/ui/spinner";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { useProposeFundMerge } from "../hooks/mutations/useProposeFundMerge";
import { useFundMergePreview } from "../hooks/queries/useFundMergePreview";
import { exchangeText, exitPaymentNote, ratioFormula, type MergeSide } from "../lib/fund-merge";

type MergeDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fund: FundDetails;
};

/** Propor fusão: a gestora que incorpora e a que deixa de existir, com a troca de cotas e o que sobra para quem vota contra. */
export function MergeDialog({ open, onOpenChange, fund }: MergeDialogProps) {
  const partners = fund.assembly.merge_partners;
  const [partnerChoice, setPartnerChoice] = useState<number | null>(null);
  const [partnerIncorporates, setPartnerIncorporates] = useState(false);
  const partner = partners.find((candidate) => candidate.fund_id === partnerChoice) ?? partners[0];
  if (partner === undefined) return null;

  return (
    <MergeDialogBody
      open={open}
      onOpenChange={onOpenChange}
      fund={fund}
      partners={partners}
      partner={partner}
      partnerIncorporates={partnerIncorporates}
      onPartnerChange={setPartnerChoice}
      onIncorporatesChange={setPartnerIncorporates}
    />
  );
}

type MergeDialogBodyProps = MergeDialogProps & {
  partners: MergeSide[];
  partner: MergeSide;
  partnerIncorporates: boolean;
  onPartnerChange: (fundId: number) => void;
  onIncorporatesChange: (partnerIncorporates: boolean) => void;
};

function MergeDialogBody({
  open,
  onOpenChange,
  fund,
  partners,
  partner,
  partnerIncorporates,
  onPartnerChange,
  onIncorporatesChange,
}: MergeDialogBodyProps) {
  // A gestora desta página como uma ponta da fusão; o nome e o ticker são os que a página já tem
  const self: Pick<MergeSide, "fund_id" | "name" | "ticker"> = {
    fund_id: fund.id,
    name: fund.name,
    ticker: fund.ticker,
  };
  const mother = partnerIncorporates ? partner : self;
  const daughter = partnerIncorporates ? self : partner;
  const { preview } = useFundMergePreview(mother.fund_id, daughter.fund_id);
  const propose = useProposeFundMerge(mother.fund_id);
  const ready = preview !== undefined && preview.ratio !== null && !propose.isPending;
  const formula = preview ? ratioFormula(preview.daughter, preview.mother, preview.ratio) : null;

  const submit = () => {
    if (!ready) return;
    propose.mutate({ daughter_fund_id: daughter.fund_id }, { onSuccess: () => onOpenChange(false) });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-145">
        <DialogHeader variant="divided">
          <DialogTitle>Propor fusão</DialogTitle>
          <DialogDescription>
            Junta duas gestoras que você gere numa só. A proposta vai à assembleia de cada uma.
          </DialogDescription>
        </DialogHeader>
        <DialogBody>
          {/* Com qual gestora */}
          {partners.length > 1 && (
            <Field>
              <FieldLabel id="merge-partner-label">Com qual das suas gestoras</FieldLabel>
              <ToggleGroup
                variant="segmented"
                aria-labelledby="merge-partner-label"
                value={[String(partner.fund_id)]}
                onValueChange={(values) => values[0] !== undefined && onPartnerChange(Number(values[0]))}
              >
                {partners.map((candidate) => (
                  <ToggleGroupItem key={candidate.fund_id} value={String(candidate.fund_id)}>
                    {candidate.name}
                  </ToggleGroupItem>
                ))}
              </ToggleGroup>
            </Field>
          )}

          {/* Quem incorpora */}
          <Field>
            <FieldLabel id="merge-mother-label">Qual gestora incorpora</FieldLabel>
            <RadioGroup
              value={partnerIncorporates ? "partner" : "self"}
              onValueChange={(value) => onIncorporatesChange(value === "partner")}
              aria-labelledby="merge-mother-label"
              className="sm:grid-cols-2"
            >
              {[
                { key: "self", side: self },
                { key: "partner", side: partner },
              ].map(({ key, side }) => (
                <FieldLabel key={key} variant="fund" htmlFor={`merge-mother-${key}`}>
                  <Field orientation="horizontal">
                    <RadioGroupItem variant="fund" value={key} id={`merge-mother-${key}`} />
                    <FieldContent>
                      <FieldTitle>
                        <b className="font-bold">{side.name}</b>
                      </FieldTitle>
                      <FieldDescription>{side.ticker}</FieldDescription>
                    </FieldContent>
                  </Field>
                </FieldLabel>
              ))}
            </RadioGroup>
            <FieldDescription>A outra deixa de existir, e os cotistas dela recebem cotas desta.</FieldDescription>
          </Field>

          {/* O que a fusão faz */}
          {preview && (
            <div>
              <KeyValueRow
                label="Relação de troca"
                note={`Pelo patrimônio por cota do dia da aprovação${formula === null ? "" : `: ${formula}`}`}
                value={
                  preview.ratio === null
                    ? "—"
                    : exchangeText(preview.daughter.ticker, preview.mother.ticker, preview.ratio)
                }
              />
              <KeyValueRow
                label="Votação"
                note="Sai só se as duas aprovarem"
                value="5 pregões em cada assembleia"
                valueClassName="font-sans"
              />
              <KeyValueRow
                label={`Quem votar contra na ${preview.daughter.name}`}
                note={exitPaymentNote(preview.daughter, preview.mother)}
                value="Sai pelo patrimônio por cota"
                valueClassName="font-sans"
              />
              <KeyValueRow
                label={`${preview.mother.name} depois`}
                note={
                  preview.quotas_after !== null && preview.mother.nav !== null
                    ? `${displayQuantity(preview.quotas_after)} cotas a ${displayMoney(preview.mother.nav)}`
                    : "Sem patrimônio por cota para calcular"
                }
                value={preview.equity_after === null ? "—" : displayMoney(preview.equity_after)}
              />
            </div>
          )}

          <p className="text-xs text-muted-foreground">
            Só cotista da {daughter.name} pode sair. Se o caixa e a renda fixa de liquidez diária das duas não cobrirem,
            a fusão trava e o placar mostra quanto falta.
          </p>
        </DialogBody>
        <DialogFooter variant="divided">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button variant="fund" disabled={!ready} onClick={submit}>
            {propose.isPending && <Spinner />}
            Levar às duas assembleias
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
