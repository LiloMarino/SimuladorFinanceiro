import { useState } from "react";
import { Controller, useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
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
import { PartyIdentityFields } from "@/shared/components/party-identity-fields";
import { partyIdentitySchema } from "@/shared/lib/party-identity";
import { displayMoney } from "@/shared/lib/utils/display";
import { useFoundParty } from "../hooks/mutations/useFoundParty";
import { PARTY_COLORS } from "@/shared/lib/party-colors";
import { congressAmount, contributionAmount } from "../lib/contribution";
import { ContributionField } from "./contribution-field";
import { ContributionSplit } from "./contribution-split";
import type { ElectionPanel, PartyIdentity } from "@/types";
import { FlagsPicker } from "./flags-picker";

type FoundPartyDialogProps = {
  panel: ElectionPanel;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Cores que outros partidos já usam */
  takenColors: string[];
  /** Caixa do jogador, em reais, para avisar quando a contribuição passa dele */
  cash: string | undefined;
};

/** Fundar um partido: nome, sigla, cor, as 3 bandeiras e a contribuição de quem funda. */
export function FoundPartyDialog({ panel, open, onOpenChange, takenColors, cash }: FoundPartyDialogProps) {
  const found = useFoundParty();
  const taken = new Set(takenColors.map((color) => color.toUpperCase()));
  const firstFree = PARTY_COLORS.find((color) => !taken.has(color)) ?? PARTY_COLORS[0];
  const [contribution, setContribution] = useState("");
  const [share, setShare] = useState(0);

  const form = useForm<PartyIdentity>({
    resolver: zodResolver(partyIdentitySchema),
    defaultValues: { name: "", abbr: "", color: firstFree, flags: [] },
  });

  const color = useWatch({ control: form.control, name: "color" });
  const abbr = useWatch({ control: form.control, name: "abbr" });
  const monthly = Number(contributionAmount(contribution));
  const overCash = cash !== undefined && monthly > Number(cash);

  const submit = form.handleSubmit((values) =>
    found.mutate(
      {
        name: values.name,
        abbr: values.abbr,
        color: values.color,
        flags: values.flags,
        contribution: contributionAmount(contribution),
        congress: congressAmount(monthly, share, true),
      },
      { onSuccess: () => onOpenChange(false) },
    ),
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-230">
        <DialogHeader variant="divided">
          <DialogTitle>Fundar partido</DialogTitle>
          <DialogDescription>
            Você vira o fundador e o candidato do partido. A fundação é pública: a sala vê o partido, as bandeiras e
            quem contribui com quanto.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <form id="found-party-form" onSubmit={(event) => void submit(event)} className="grid gap-3.5">
            <PartyIdentityFields control={form.control} takenColors={takenColors} idPrefix="party" />

            <Controller
              control={form.control}
              name="flags"
              render={({ field, fieldState }) => (
                <FlagsPicker
                  panel={panel}
                  value={field.value}
                  onChange={field.onChange}
                  color={color}
                  error={fieldState.error?.message}
                />
              )}
            />

            <ContributionField
              id="found-contribution"
              value={contribution}
              onChange={setContribution}
              error={overCash ? `Seu caixa hoje é ${displayMoney(cash)}.` : null}
              note="Pode ser zero. Sai do seu caixa todo dia 1º e não volta; a verba do partido é a soma das contribuições."
            />
            <ContributionSplit share={share} onShare={setShare} monthly={monthly} runs />

            <Alert variant="muted">
              <Info />
              <AlertTitle>Você será quem fundou o partido</AlertTitle>
              <AlertDescription>
                Escolhe candidato e vice entre os filiados e pode expulsar. Nome, sigla, cor e bandeiras ficam públicos.
              </AlertDescription>
            </Alert>
          </form>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button type="submit" form="found-party-form" disabled={found.isPending}>
            {abbr.length >= 2 ? `Fundar o ${abbr}` : "Fundar partido"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
