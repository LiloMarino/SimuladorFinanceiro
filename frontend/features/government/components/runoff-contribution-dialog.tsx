import { useState } from "react";
import { Info } from "lucide-react";
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
import { displayDayMonth, displayMoney } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty, RunoffRace } from "@/types";
import { useContributeRunoff } from "../hooks/mutations/useContributeRunoff";
import { contributionAmount } from "@/shared/lib/contribution";
import { monthlyYield } from "../lib/election";
import { ContributionField } from "@/shared/components/contribution-field";
import { DisabledHint } from "@/shared/components/disabled-hint";

const FORM_ID = "runoff-contribution-form";

type RunoffContributionDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  panel: ElectionPanel;
  race: RunoffRace;
  party: ElectionParty;
  cash: string | undefined;
};

/** A contribuição única do filiado de um finalista para a campanha do 2º turno. */
export function RunoffContributionDialog({
  open,
  onOpenChange,
  panel,
  race,
  party,
  cash,
}: RunoffContributionDialogProps) {
  const [text, setText] = useState("");
  const contribute = useContributeRunoff();
  const amount = Number(contributionAmount(text));
  const overCash = cash !== undefined && amount > Number(cash);
  // Os pontos que a contribuição soma são a diferença da curva de rendimento do total do partido
  const before = race.contributions
    .filter((item) => item.party_id === party.id)
    .reduce((sum, item) => sum + Number(item.amount), 0);
  const effect = monthlyYield(before + amount) - monthlyYield(before);

  const overCap = amount > Number(panel.contribution_cap);
  const canSubmit = amount > 0 && !overCash && !overCap && !contribute.isPending;
  // O motivo do botão apagado: o que falta para contribuir
  const blockedReason =
    amount <= 0
      ? "Digite quanto quer contribuir."
      : overCash
        ? `Seu caixa hoje é ${displayMoney(cash)}.`
        : overCap
          ? `O teto é ${displayMoney(panel.contribution_cap)} por pessoa.`
          : null;

  const submit = () =>
    contribute.mutate({ amount: contributionAmount(text) }, { onSuccess: () => onOpenChange(false) });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-110">
        <DialogHeader variant="divided">
          <DialogTitle>Contribuir com o {party.abbr} no 2º turno</DialogTitle>
          <DialogDescription>
            Uma única vez, até {displayDayMonth(panel.dates.donation_deadline)}. O valor sai do seu caixa de uma vez.
          </DialogDescription>
        </DialogHeader>
        <DialogBody>
          <div className="grid gap-3.5">
            <form
              id={FORM_ID}
              onSubmit={(event) => {
                event.preventDefault();
                if (canSubmit) submit();
              }}
            >
              <ContributionField
                cap={panel.contribution_cap}
                id="runoff-contribution"
                autoFocus
                value={text}
                onChange={setText}
                error={overCash ? `Seu caixa hoje é ${displayMoney(cash)}.` : null}
                note="Vira verba da campanha do partido no 2º turno e entra no ranking como gasto seu."
              />
            </form>
            {amount > 0 && (
              <dl className="grid divide-y rounded-lg border px-3 text-[13px]">
                <div className="flex justify-between gap-3 py-1.5">
                  <dt className="text-muted-foreground">Efeito estimado</dt>
                  <dd className="text-right font-mono font-semibold">
                    +{effect.toLocaleString("pt-BR", { maximumFractionDigits: 1 })} pontos para o {party.abbr}
                  </dd>
                </div>
              </dl>
            )}
            <Alert variant="muted">
              <Info />
              <AlertTitle>A sala vê a contribuição</AlertTitle>
              <AlertDescription>Quem contribuiu e quanto aparecem no aviso e na página da eleição.</AlertDescription>
            </Alert>
          </div>
        </DialogBody>
        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <DisabledHint reason={blockedReason}>
            <Button type="submit" form={FORM_ID} disabled={!canSubmit}>
              Contribuir
            </Button>
          </DisabledHint>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
