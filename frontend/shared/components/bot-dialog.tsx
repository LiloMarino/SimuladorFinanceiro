import type { ReactNode } from "react";
import { Controller, useForm, useWatch, type UseFormReturn } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { BotColorSwatches } from "@/shared/components/bot-color-swatches";
import { BotNameField } from "@/shared/components/bot-name-field";
import { ErrorState } from "@/shared/components/error-state";
import { InfoHint } from "@/shared/components/info-hint";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { StrategyParamsForm } from "@/shared/components/strategy-params-form";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/shared/components/ui/dialog";
import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import { useBotStrategies } from "@/shared/hooks/queries/useBotStrategies";
import { useBotTickers } from "@/shared/hooks/queries/useBotTickers";
import type { BotFormValues, TakenSlot } from "@/shared/lib/bot-form";
import { drawBotName, isDrawnName, nameTaken } from "@/shared/lib/bot-names";
import { GROUP_SECTION } from "@/shared/lib/strategy-groups";
import { defaultValues, draftErrors, fromDraft, toDraft, type ParamValues } from "@/shared/lib/strategy-params";
import { cn } from "@/shared/lib/utils";
import type { StrategyGroup, StrategyInfo } from "@/types";

const GROUPS: StrategyGroup[] = ["reference", "tactic"];
const BOT_NAME_MAX = 30;

/** O que o diálogo entrega ao confirmar: os campos do formulário e os parâmetros já como números. */
export type BotSubmit = BotFormValues & { params: ParamValues };

export type BotSubmitControls = {
  close: () => void;
  /** O servidor recusou o nome: a mensagem aparece no campo */
  refuseName: () => void;
};

type BotDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  /** Data de início que fixa a faixa dos parâmetros; sem ela vale a das regras do lobby */
  startDate?: string;
  /** Quem já ocupa nome e cor; o bot em edição fica de fora */
  others: TakenSlot[];
  /** O dinheiro do exemplo em reais dos parâmetros e de onde ele vem */
  startingCash: string;
  cashLabel: string;
  /** Os valores do formulário, resolvidos com a lista de estratégias já carregada */
  initial: (strategies: StrategyInfo[]) => BotFormValues;
  /** Parâmetros salvos do bot em edição, para o "Era X" */
  saved?: { strategyKey: string; params: ParamValues };
  nameTakenMessage: string;
  nameHelp: string;
  submitLabel: string;
  submitIcon?: ReactNode;
  saving: boolean;
  /** Campos a mais depois da cor, como a equipe da sala */
  extraFields?: (form: UseFormReturn<BotFormValues>, others: TakenSlot[]) => ReactNode;
  /** Compara os parâmetros com o padrão da estratégia, em vez de com o salvo */
  compareToDefault?: boolean;
  /** Os dados que chegam por fora do diálogo (a sala, as regras) ainda carregam */
  loading?: boolean;
  onSubmit: (bot: BotSubmit, controls: BotSubmitControls) => void;
};

/** Adicionar ou configurar um bot: a estratégia à esquerda e, à direita, o nome, a cor e os parâmetros. */
export function BotDialog({ open, onOpenChange, ...content }: BotDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        flush
        className="max-h-[calc(100vh-4rem)] grid-rows-[auto_minmax(0,1fr)] overflow-hidden sm:max-w-245"
      >
        <BotDialogContent {...content} onClose={() => onOpenChange(false)} />
      </DialogContent>
    </Dialog>
  );
}

type BotDialogContentProps = Omit<BotDialogProps, "open" | "onOpenChange"> & { onClose: () => void };

/** Cabeçalho e a lista de estratégias resolvida: o formulário só monta com o dado pronto. */
function BotDialogContent({ title, description, startDate, loading = false, onClose, ...form }: BotDialogContentProps) {
  const strategies = useBotStrategies(startDate);
  const tickers = useBotTickers();

  const ready = strategies.data && strategies.data.length > 0 && !loading;

  return (
    <>
      {/* Cabeçalho */}
      <div className="border-b px-6 py-5 pr-14">
        <DialogTitle large>{title}</DialogTitle>
        <DialogDescription>{description}</DialogDescription>
      </div>

      {strategies.error ? (
        <div className="p-6">
          <ErrorState
            title="Não deu para carregar as estratégias"
            description="Sem a lista, não dá para escolher o tipo do bot."
            error={strategies.error}
            onRetry={() => void strategies.refetch()}
          />
        </div>
      ) : ready ? (
        <BotForm strategies={strategies.data} tickerOptions={tickers.data ?? []} onClose={onClose} {...form} />
      ) : (
        <BotDialogSkeleton />
      )}
    </>
  );
}

function BotDialogSkeleton() {
  return (
    <div className="grid gap-2 p-6" aria-busy="true" aria-label="Carregando as estratégias">
      {Array.from({ length: 6 }, (_, i) => (
        <div key={i} className="flex items-center gap-2.5 px-3 py-2">
          <Skeleton circle className="size-4" />
          <div className="grid flex-1 gap-1.5">
            <Skeleton className="h-3 w-[55%]" />
            <Skeleton className="h-2.5 w-[85%]" />
          </div>
        </div>
      ))}
    </div>
  );
}

type BotFormProps = Omit<BotDialogContentProps, "title" | "description" | "startDate" | "loading"> & {
  strategies: StrategyInfo[];
  tickerOptions: string[];
};

function BotForm({
  strategies,
  tickerOptions,
  others,
  startingCash,
  cashLabel,
  initial,
  saved,
  nameTakenMessage,
  nameHelp,
  submitLabel,
  submitIcon,
  saving,
  extraFields,
  compareToDefault,
  onSubmit,
  onClose,
}: BotFormProps) {
  const takenNames = others.map((p) => p.nickname);

  // O nome vale contra quem ocupa nomes agora: a validação roda a cada digitação
  const schema = z.object({
    nickname: z
      .string()
      .trim()
      .min(1, "Dê um nome ao bot.")
      .max(BOT_NAME_MAX, `Use até ${BOT_NAME_MAX} letras.`)
      .refine((name) => !nameTaken(name, takenNames), nameTakenMessage),
    strategyKey: z.string(),
    color: z.string(),
    team: z.number().nullable(),
    drafts: z.record(z.string(), z.any()),
  });

  const form = useForm<BotFormValues>({
    resolver: zodResolver(schema),
    mode: "onChange",
    defaultValues: initial(strategies),
  });
  const { strategyKey, nickname, color, drafts } = useWatch({ control: form.control }) as BotFormValues;

  const strategy = strategies.find((s) => s.key === strategyKey) ?? strategies[0];
  const draft = drafts[strategy.key];
  const errors = draftErrors(strategy.params, draft);
  const values = fromDraft(strategy.params, draft);
  const canSave = values !== null && Object.keys(errors).length === 0 && form.formState.isValid && !saving;

  const pickStrategy = (key: string) => {
    const next = strategies.find((s) => s.key === key);
    if (!next || next.key === strategy.key) return;
    form.setValue("strategyKey", next.key);
    // O nome sorteado acompanha a estratégia; o digitado fica
    if (isDrawnName(nickname, strategy)) {
      form.setValue("nickname", drawBotName(next, takenNames), { shouldValidate: true });
    }
  };

  const setDraft = (next: BotFormValues["drafts"][string]) =>
    form.setValue("drafts", { ...drafts, [strategy.key]: next }, { shouldValidate: true });

  const submit = form.handleSubmit((formValues) => {
    if (!values) return;
    const refuseName = () => form.setError("nickname", { type: "server", message: nameTakenMessage });
    onSubmit(
      { ...formValues, nickname: formValues.nickname.trim(), strategyKey: strategy.key, params: values },
      { close: onClose, refuseName },
    );
  });

  return (
    <form onSubmit={(event) => void submit(event)} className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
      <div className="grid min-h-0 grid-cols-[340px_minmax(0,1fr)]">
        {/* Estratégias por grupo */}
        <div className="min-h-0 overflow-y-auto border-r bg-subtle px-4 pt-4 pb-5">
          <div className="px-0.5 pb-1.5 text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
            Estratégia
          </div>
          <RadioGroup value={strategy.key} onValueChange={pickStrategy} dense aria-label="Estratégia">
            {GROUPS.map((group) => {
              const items = strategies.filter((s) => s.group === group);
              if (items.length === 0) return null;
              return (
                <div key={group} className="grid gap-0.5">
                  <div className="flex items-center gap-1.5 pt-2 pb-0.5 pl-0.5 text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
                    {GROUP_SECTION[group].title}
                    <InfoHint label={`O que são as ${GROUP_SECTION[group].title.toLowerCase()}`}>
                      {GROUP_SECTION[group].hint}
                    </InfoHint>
                  </div>
                  {items.map((item) => {
                    const selected = item.key === strategy.key;
                    return (
                      <label
                        key={item.key}
                        className={cn(
                          "grid cursor-pointer grid-cols-[auto_1fr] items-center gap-x-2.5 gap-y-px rounded-lg border border-transparent px-3 py-2 text-[13px]",
                          selected ? "border-primary bg-info-soft ring-1 ring-primary" : "hover:bg-muted",
                        )}
                      >
                        <RadioGroupItem value={item.key} className="row-span-2" />
                        <span className={selected ? "font-semibold" : "font-medium"}>{item.name}</span>
                        <span className="col-start-2 text-xs text-muted-foreground">{item.summary}</span>
                      </label>
                    );
                  })}
                </div>
              );
            })}
          </RadioGroup>
        </div>

        {/* Prévia, nome, cor, campos extras e parâmetros */}
        <div className="min-h-0 overflow-y-auto px-6 py-5">
          <div className="grid min-w-0 content-start gap-4.5">
            {/* Prévia */}
            <div className="flex min-w-0 items-center gap-3 rounded-[10px] border border-muted bg-subtle p-3">
              <PlayerAvatar nickname={nickname} color={color} bot size="lg" />
              <div className="grid min-w-0 gap-0.5">
                <span className="flex min-w-0 items-center gap-2.5">
                  <span className="truncate font-semibold">{nickname.trim() || "Sem nome"}</span>
                  <Badge variant="secondary" size="tag">
                    Bot
                  </Badge>
                </span>
                <span className="truncate text-xs text-muted-foreground">{strategy.name}</span>
              </div>
              <span className="ml-auto shrink-0 text-xs text-muted-foreground">Assim ele aparece</span>
            </div>

            {/* Nome */}
            <Controller
              control={form.control}
              name="nickname"
              render={({ field, fieldState }) => (
                <BotNameField
                  id="bot-nickname"
                  value={field.value}
                  onChange={field.onChange}
                  onBlur={field.onBlur}
                  error={fieldState.error}
                  help={nameHelp}
                  onDraw={() =>
                    form.setValue("nickname", drawBotName(strategy, [...takenNames, nickname]), {
                      shouldValidate: true,
                    })
                  }
                />
              )}
            />

            {/* Cor */}
            <Field>
              <FieldLabel>Cor</FieldLabel>
              <BotColorSwatches owners={others} selected={color} onSelect={(next) => form.setValue("color", next)} />
              <FieldDescription>Já vem a próxima livre. As riscadas estão em uso.</FieldDescription>
            </Field>

            {extraFields?.(form, others)}

            {/* Parâmetros */}
            <StrategyParamsForm
              key={strategy.key}
              strategy={strategy}
              draft={draft}
              saved={saved?.strategyKey === strategy.key ? saved.params : {}}
              compareToDefault={compareToDefault}
              errors={errors}
              tickerOptions={tickerOptions}
              cash={startingCash}
              cashLabel={cashLabel}
              headerAction={
                <Button
                  type="button"
                  variant="link-muted"
                  size="sm"
                  onClick={() => setDraft(toDraft(defaultValues(strategy)))}
                >
                  Restaurar padrão
                </Button>
              }
              onChange={setDraft}
            />
          </div>
        </div>
      </div>

      {/* Rodapé */}
      <div className="flex justify-end gap-2 rounded-b-xl border-t bg-subtle px-6 py-3.5">
        <Button type="button" variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <Button type="submit" disabled={!canSave}>
          {saving ? <Spinner /> : submitIcon}
          {submitLabel}
        </Button>
      </div>
    </form>
  );
}
