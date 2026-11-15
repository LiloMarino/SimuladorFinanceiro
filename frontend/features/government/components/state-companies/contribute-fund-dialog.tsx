import { Controller, useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Gavel, Newspaper, TriangleAlert } from "lucide-react";
import { z } from "zod";
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
import { displayDayMonth } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import { moneyToBody } from "@/shared/lib/utils/money-field";
import { useProposeMeasure } from "../../hooks/mutations/useProposeMeasure";
import { useSovereignContributionPreview } from "../../hooks/queries/useSovereignContributionPreview";
import {
  billionsToField,
  CONTRIBUTION_SHORTCUTS_BILLIONS,
  fundCashLabel,
  shortcutLabel,
} from "../../lib/sovereign-fund";
import { MeasureBudgetEffect } from "../measure-budget-effect";

const contributionSchema = z.object({
  value: z.string().refine((text) => Number(moneyToBody(text)) > 0, "Informe o valor do aporte."),
});

type ContributionValues = z.infer<typeof contributionSchema>;

type ContributeFundDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Dias entre a aprovação e a medida valer */
  vigenceDays: number;
};

type LineProps = { label: string; children: React.ReactNode };

function Line({ label, children }: LineProps) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right font-mono font-semibold">{children}</dd>
    </div>
  );
}

/** Aportar no Fundo Soberano: um valor em R$ que entra na dívida e no caixa do fundo; vai ao Congresso como medida de gasto. */
export function ContributeFundDialog({ open, onOpenChange, vigenceDays }: ContributeFundDialogProps) {
  const propose = useProposeMeasure();

  const form = useForm<ContributionValues>({
    resolver: zodResolver(contributionSchema),
    defaultValues: { value: "" },
  });

  const { value: text } = useWatch({ control: form.control });
  const parsed = contributionSchema.safeParse({ value: text ?? "" });
  const value = parsed.success ? moneyToBody(parsed.data.value) : null;
  const preview = useSovereignContributionPreview(value);
  const data = value === null ? undefined : preview.data;

  const submit = form.handleSubmit((fields) =>
    propose.mutate(
      { kind: "CONTRIBUTE_SOVEREIGN_FUND", value: moneyToBody(fields.value) },
      { onSuccess: () => onOpenChange(false) },
    ),
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-230">
        <DialogHeader variant="divided">
          <DialogTitle>Aportar no Fundo Soberano</DialogTitle>
          <DialogDescription>
            Medida de gasto: um valor em R$, que entra inteiro na dívida e no caixa do fundo.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <form id="contribute-fund-form" onSubmit={(event) => void submit(event)} className="grid gap-4">
            <Alert variant="info">
              <Gavel />
              <AlertTitle>É medida de gasto público: vai a votação no Congresso</AlertTitle>
              <AlertDescription>
                Outro aporte depois é outra medida. O Fundo Soberano é a carteira do governo na bolsa: compra ações e
                cotas de gestora com o caixa do aporte, e o que vende ou recebe de dividendo volta ao Tesouro e abate a
                dívida.
              </AlertDescription>
            </Alert>

            {/* Valor do aporte */}
            <Controller
              control={form.control}
              name="value"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="sovereign-contribution-value">Valor do aporte</FieldLabel>
                  <Input
                    id="sovereign-contribution-value"
                    numeric
                    inputMode="decimal"
                    autoComplete="off"
                    placeholder="R$ 0,00"
                    aria-invalid={fieldState.invalid}
                    {...field}
                    onChange={(event) => field.onChange(formatMoney(event.target.value))}
                  />
                  <div className="grid grid-cols-4 gap-1.5">
                    {CONTRIBUTION_SHORTCUTS_BILLIONS.map((billions) => (
                      <Button
                        key={billions}
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={() => field.onChange(billionsToField(billions))}
                      >
                        {shortcutLabel(billions)}
                      </Button>
                    ))}
                  </div>
                  {fieldState.error ? (
                    <FieldError errors={[fieldState.error]} />
                  ) : (
                    <FieldDescription>Os atalhos trocam o valor do campo.</FieldDescription>
                  )}
                </Field>
              )}
            />

            {/* Efeitos do aporte */}
            {data ? (
              <>
                <MeasureBudgetEffect effect={data.measure.budget} spending />
                <dl className="grid gap-2 rounded-lg border p-3.5 text-[13px]">
                  <Line label="Caixa do fundo hoje">{fundCashLabel(data.cash_before)}</Line>
                  <Line label="Caixa do fundo depois">{fundCashLabel(data.cash_after)}</Line>
                  <Line label="PIB">não muda</Line>
                </dl>
                <p className="text-xs text-muted-foreground">
                  Dívida sobre o PIB: quanto o governo deve comparado ao que o país produz num ano. Em 60%, a dívida
                  equivale a 7 meses de tudo o que o país produz; acima de 100% o país deve mais do que produz num ano
                  inteiro. Quanto menor, melhor.
                </p>
                <Alert variant="info">
                  <Gavel />
                  <AlertTitle>O Congresso vota em {displayDayMonth(data.measure.vote_date)}</AlertTitle>
                  <AlertDescription>
                    Passa com 51 votos Sim de 101, e as bancadas votam como o líder orienta. Aprovado, o dinheiro entra
                    no caixa do fundo em {displayDayMonth(data.measure.effective)}, {vigenceDays} dias depois.
                  </AlertDescription>
                </Alert>
              </>
            ) : (
              <p className="text-xs text-muted-foreground">
                Com o valor preenchido, a dívida, o caixa do fundo e o dia da votação aparecem aqui.
              </p>
            )}

            {preview.isError && value !== null && (
              <Alert variant="destructive">
                <TriangleAlert />
                <AlertTitle>Não deu para calcular o aporte</AlertTitle>
                <AlertDescription>{preview.error.message}</AlertDescription>
              </Alert>
            )}
            {propose.isError && (
              <Alert variant="destructive">
                <TriangleAlert />
                <AlertTitle>Não deu para enviar a medida</AlertTitle>
                <AlertDescription>{propose.error.message}</AlertDescription>
              </Alert>
            )}
          </form>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <span className="mr-auto flex items-center gap-1.5 text-xs text-muted-foreground">
            <Newspaper className="size-3.5" />
            Sai no jornal ao ser aprovado
          </span>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button type="submit" form="contribute-fund-form" disabled={propose.isPending || !data}>
            Enviar ao Congresso
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
