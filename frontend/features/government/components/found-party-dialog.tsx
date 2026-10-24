import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Check, Info } from "lucide-react";
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
import { cn } from "@/shared/lib/utils";
import { displayMoney } from "@/shared/lib/utils/display";
import { useFoundParty } from "../hooks/mutations/useFoundParty";
import { PARTY_COLORS } from "../lib/party-colors";
import { contributionAmount } from "../lib/contribution";
import { ContributionField } from "./contribution-field";
import { PromiseHint } from "./promise-hint";
import { PromisePicker } from "./promise-picker";

const ABBR_PATTERN = /^[A-ZÀ-Ý]{2,5}$/;

const foundPartySchema = z.object({
  name: z.string().trim().min(2, "Dê um nome de pelo menos 2 letras.").max(60, "O nome vai até 60 letras."),
  abbr: z.string().regex(ABBR_PATTERN, "A sigla tem de 2 a 5 letras."),
  color: z.string().regex(/^#[0-9A-Fa-f]{6}$/, "Escolha uma cor."),
  promise: z.number().int().min(1).max(5),
});

type FoundPartyForm = z.infer<typeof foundPartySchema>;

type FoundPartyDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Cores que outros partidos já usam */
  takenColors: string[];
  /** Caixa do jogador, em reais, para avisar quando a contribuição passa dele */
  cash: string | undefined;
};

/** Fundar um partido: nome, sigla, cor, promessa na régua e a contribuição de quem funda. */
export function FoundPartyDialog({ open, onOpenChange, takenColors, cash }: FoundPartyDialogProps) {
  const found = useFoundParty();
  const taken = new Set(takenColors.map((color) => color.toUpperCase()));
  const firstFree = PARTY_COLORS.find((color) => !taken.has(color)) ?? PARTY_COLORS[0];
  const [contribution, setContribution] = useState("");

  const form = useForm<FoundPartyForm>({
    resolver: zodResolver(foundPartySchema),
    defaultValues: { name: "", abbr: "", color: firstFree, promise: 3 },
  });

  const monthly = Number(contributionAmount(contribution));
  const overCash = cash !== undefined && monthly > Number(cash);

  const submit = form.handleSubmit((values) =>
    found.mutate(
      {
        name: values.name,
        abbr: values.abbr,
        color: values.color,
        promise: values.promise,
        contribution: contributionAmount(contribution),
      },
      { onSuccess: () => onOpenChange(false) },
    ),
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-120">
        <DialogHeader variant="divided">
          <DialogTitle>Fundar um partido</DialogTitle>
          <DialogDescription>Só se concorre por partido. Sozinho, é um partido de um filiado.</DialogDescription>
        </DialogHeader>

        <DialogBody>
          <form id="found-party-form" onSubmit={(event) => void submit(event)} className="grid gap-3.5">
            <div className="grid grid-cols-[1fr_7rem] gap-3">
              <Controller
                control={form.control}
                name="name"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="party-name">Nome</FieldLabel>
                    <Input id="party-name" autoComplete="off" aria-invalid={fieldState.invalid} {...field} />
                    <FieldError errors={[fieldState.error]} />
                  </Field>
                )}
              />
              <Controller
                control={form.control}
                name="abbr"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="party-abbr">Sigla</FieldLabel>
                    <Input
                      id="party-abbr"
                      numeric
                      autoComplete="off"
                      maxLength={5}
                      aria-invalid={fieldState.invalid}
                      {...field}
                      onChange={(event) => field.onChange(event.target.value.toUpperCase().replace(/[^A-ZÀ-Ý]/g, ""))}
                    />
                    {fieldState.error ? (
                      <FieldError errors={[fieldState.error]} />
                    ) : (
                      <FieldDescription>2 a 5 letras.</FieldDescription>
                    )}
                  </Field>
                )}
              />
            </div>

            <Controller
              control={form.control}
              name="color"
              render={({ field }) => (
                <Field>
                  <FieldLabel>Cor</FieldLabel>
                  <div role="radiogroup" aria-label="Cor do partido" className="flex flex-wrap gap-2">
                    {PARTY_COLORS.map((color) => {
                      const used = taken.has(color);
                      const selected = field.value === color;
                      return (
                        <button
                          key={color}
                          type="button"
                          role="radio"
                          aria-checked={selected}
                          aria-label={used ? `${color}, já usada` : color}
                          disabled={used}
                          onClick={() => field.onChange(color)}
                          className={cn(
                            "inline-flex size-6.5 items-center justify-center rounded-[7px] text-white outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
                            selected && "ring-2 ring-foreground ring-offset-2 ring-offset-card",
                            used && "opacity-25",
                          )}
                          style={{ backgroundColor: color }}
                        >
                          {used && <Check className="size-3.5" />}
                        </button>
                      );
                    })}
                  </div>
                  <FieldDescription>Cada partido tem uma cor; o cinza é dos partidos do computador.</FieldDescription>
                </Field>
              )}
            />

            <Controller
              control={form.control}
              name="promise"
              render={({ field }) => (
                <Field>
                  <div className="flex items-center gap-1.5">
                    <FieldLabel>Promessa do partido</FieldLabel>
                    <PromiseHint />
                  </div>
                  <PromisePicker value={field.value} onChange={field.onChange} />
                </Field>
              )}
            />

            <ContributionField
              id="found-contribution"
              value={contribution}
              onChange={setContribution}
              error={overCash ? `Seu caixa hoje é ${displayMoney(cash)}.` : null}
              note="Pode ser zero. Sai do seu caixa todo dia 1º e não volta; a verba do partido é a soma das contribuições."
            />

            <Alert variant="muted">
              <Info />
              <AlertTitle>Você será quem fundou o partido</AlertTitle>
              <AlertDescription>
                Escolhe candidato e vice entre os filiados e pode expulsar. Nome, sigla, cor e promessa ficam públicos.
              </AlertDescription>
            </Alert>
          </form>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button type="submit" form="found-party-form" disabled={found.isPending}>
            Fundar partido
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
