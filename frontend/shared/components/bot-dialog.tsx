import type { ReactNode } from "react";
import { Controller, useForm, useWatch, type UseFormReturn } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { BotNameField } from "@/shared/components/bot-name-field";
import { ColorSwatchPicker } from "@/shared/components/color-swatch-picker";
import { ErrorState } from "@/shared/components/error-state";
import { InfoHint } from "@/shared/components/info-hint";
import { OptionSelect, type SelectOption } from "@/shared/components/option-select";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { StrategyParamsForm } from "@/shared/components/strategy-params-form";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/shared/components/ui/dialog";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import { useBotStrategies } from "@/shared/hooks/queries/useBotStrategies";
import { useBotTickers } from "@/shared/hooks/queries/useBotTickers";
import { RANDOM_STRATEGY, type BotFormValues, type TakenSlot } from "@/shared/lib/bot-form";
import { drawBotName, isDrawnName, nameTaken } from "@/shared/lib/bot-names";
import { NAME_MAX_LENGTH, NAME_TOO_LONG } from "@/shared/lib/name-limit";
import { PLAYER_SWATCHES, playerOwners } from "@/shared/lib/player-colors";
import { PROFESSIONS } from "@/shared/lib/professions";
import { GROUP_SECTION } from "@/shared/lib/strategy-groups";
import { defaultValues, draftErrors, fromDraft, toDraft, type ParamValues } from "@/shared/lib/strategy-params";
import { cn } from "@/shared/lib/utils";
import type { BotTicker, Profession, StrategyGroup, StrategyInfo } from "@/types";

const GROUPS: StrategyGroup[] = ["reference", "tactic"];

/** A opção da profissão que deixa o servidor sortear uma para o bot. */
const RANDOM_PROFESSION = "random";

/**
 * Os campos do diálogo: os do bot, a profissão (nula = sorteada, só em sala de profissões) e,
 * ao adicionar na sala, a quantidade de bots a criar.
 */
type BotDialogValues = BotFormValues & { quantity: number; profession: Profession | null };

/**
 * O que o diálogo entrega ao confirmar: os campos do formulário e os parâmetros já como números.
 * `strategyKey` é `RANDOM_STRATEGY` quando cada bot do lote leva uma estratégia sorteada (sem parâmetros).
 */
export type BotSubmit = BotDialogValues & { params: ParamValues };

type BotSubmitControls = {
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
  saved?: { strategyKey: string; params: ParamValues } | undefined;
  nameTakenMessage: string;
  nameHelp: string;
  submitLabel: string;
  submitIcon?: ReactNode;
  saving: boolean;
  /** Sala de profissões: as que o bot pode ter e a dele ao configurar (nula ao adicionar, quando o servidor sorteia) */
  profession?: { available: Profession[]; initial: Profession | null } | undefined;
  /** Campos a mais depois da cor, como a equipe da sala */
  extraFields?: (form: UseFormReturn<BotDialogValues>, others: TakenSlot[]) => ReactNode;
  /** Quantos bots o diálogo cria de uma vez, no máximo; sem ele o diálogo cria um só */
  maxQuantity?: number | undefined;
  /** Compara os parâmetros com o padrão da estratégia, em vez de com o salvo */
  compareToDefault?: boolean | undefined;
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

  const ready = strategies.data && strategies.data.length > 0 && tickers.data && !loading;
  const failed = strategies.error ?? tickers.error;

  return (
    <>
      {/* Cabeçalho */}
      <div className="border-b px-6 py-5 pr-14">
        <DialogTitle large>{title}</DialogTitle>
        <DialogDescription>{description}</DialogDescription>
      </div>

      {failed ? (
        <div className="p-6">
          <ErrorState
            title="Não deu para carregar as estratégias"
            description="Sem a lista, não dá para escolher o tipo do bot."
            error={failed}
            onRetry={() => {
              void strategies.refetch();
              void tickers.refetch();
            }}
          />
        </div>
      ) : ready ? (
        <BotForm strategies={strategies.data} tickerOptions={tickers.data} onClose={onClose} {...form} />
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

type StrategyOptionProps = { value: string; name: string; summary: string; selected: boolean };

/** Uma estratégia da lista: o rádio com o nome e o resumo. */
function StrategyOption({ value, name, summary, selected }: StrategyOptionProps) {
  return (
    <label
      className={cn(
        "grid cursor-pointer grid-cols-[auto_1fr] items-center gap-x-2.5 gap-y-px rounded-lg border border-transparent px-3 py-2 text-[13px]",
        selected ? "border-primary bg-info-soft ring-1 ring-primary" : "hover:bg-muted",
      )}
    >
      <RadioGroupItem value={value} className="row-span-2" />
      <span className={selected ? "font-semibold" : "font-medium"}>{name}</span>
      <span className="col-start-2 text-xs text-muted-foreground">{summary}</span>
    </label>
  );
}

type BotFormProps = Omit<BotDialogContentProps, "title" | "description" | "startDate" | "loading"> & {
  strategies: StrategyInfo[];
  tickerOptions: BotTicker[];
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
  profession: professionField,
  maxQuantity = 1,
  compareToDefault,
  onSubmit,
  onClose,
}: BotFormProps) {
  const takenNames = others.map((p) => p.nickname);

  // O nome vale contra quem ocupa nomes agora: a validação roda a cada digitação.
  // Em lote os nomes saem sorteados da lista de cada estratégia, então o campo só vale com um bot.
  const schema = z
    .object({
      nickname: z.string(),
      strategyKey: z.string(),
      color: z.string(),
      team: z.number().nullable(),
      profession: z.custom<Profession>().nullable(),
      drafts: z.record(z.string(), z.any()),
      quantity: z
        .number({ error: `Informe de 1 a ${maxQuantity}.` })
        .int()
        .min(1, `Informe de 1 a ${maxQuantity}.`)
        .max(maxQuantity, `Só há ${maxQuantity} vagas livres na sala.`),
    })
    .superRefine(({ nickname: typed, quantity: count }, ctx) => {
      if (count > 1) return;
      const name = typed.trim();
      const message = !name
        ? "Dê um nome ao bot."
        : name.length > NAME_MAX_LENGTH
          ? NAME_TOO_LONG
          : nameTaken(name, takenNames)
            ? nameTakenMessage
            : null;
      if (message) ctx.addIssue({ code: "custom", path: ["nickname"], message });
    });

  const form = useForm<BotDialogValues>({
    resolver: zodResolver(schema),
    mode: "onChange",
    defaultValues: { ...initial(strategies), quantity: 1, profession: professionField?.initial ?? null },
  });
  const { strategyKey, nickname, color, drafts, quantity, profession } = useWatch({
    control: form.control,
  }) as BotDialogValues;

  const strategy = strategies.find((s) => s.key === strategyKey) ?? strategies[0];
  if (!strategy) return null;

  // Vários bots: nome, cor e equipe são automáticos; "Sortear" dispensa os parâmetros
  const batch = quantity > 1;
  const random = batch && strategyKey === RANDOM_STRATEGY;

  const draft = drafts[strategy.key] ?? toDraft(defaultValues(strategy));
  const errors = draftErrors(strategy.params, draft);
  const values = fromDraft(strategy.params, draft);
  const canSave =
    (random || (values !== null && Object.keys(errors).length === 0)) && form.formState.isValid && !saving;

  const pickStrategy = (key: string) => {
    if (key === strategyKey) return;
    if (key === RANDOM_STRATEGY) {
      form.setValue("strategyKey", RANDOM_STRATEGY);
      return;
    }
    const next = strategies.find((s) => s.key === key);
    if (!next) return;
    form.setValue("strategyKey", next.key);
    // O nome sorteado acompanha a estratégia; o digitado fica
    if (isDrawnName(nickname, strategy)) {
      form.setValue("nickname", drawBotName(next, takenNames), { shouldValidate: true });
    }
  };

  // Ao adicionar o servidor sorteia; ao configurar o bot já tem a sua profissão
  const professionOptions: SelectOption<Profession | typeof RANDOM_PROFESSION>[] = professionField
    ? [
        ...(professionField.initial === null
          ? [{ value: RANDOM_PROFESSION, label: batch ? "Sortear para cada bot" : "Sortear" } as const]
          : []),
        ...professionField.available.map((key) => ({ value: key, label: PROFESSIONS[key].name })),
      ]
    : [];

  const pickQuantity = (next: number) => {
    // "Sortear para cada bot" só existe em lote: com um bot a estratégia volta à primeira
    if (next <= 1 && strategyKey === RANDOM_STRATEGY) form.setValue("strategyKey", strategies[0]?.key ?? "");
    form.setValue("quantity", next, { shouldValidate: true });
  };

  const setDraft = (next: BotFormValues["drafts"][string]) =>
    form.setValue("drafts", { ...drafts, [strategy.key]: next }, { shouldValidate: true });

  const submit = form.handleSubmit((formValues) => {
    const params = random ? {} : values;
    if (!params) return;
    const refuseName = () => form.setError("nickname", { type: "server", message: nameTakenMessage });
    onSubmit(
      {
        ...formValues,
        nickname: formValues.nickname.trim(),
        strategyKey: random ? RANDOM_STRATEGY : strategy.key,
        params,
      },
      { close: onClose, refuseName },
    );
  });

  return (
    <form onSubmit={(event) => void submit(event)} className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
      <div className="grid min-h-0 grid-cols-[340px_minmax(0,1fr)]">
        {/* Estratégias por grupo */}
        <div className="min-h-0 overflow-y-auto border-r bg-subtle px-4 pt-4 pb-5">
          <div className="px-0.5 pb-1.5 text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">
            Estratégia
          </div>
          <RadioGroup
            value={random ? RANDOM_STRATEGY : strategy.key}
            onValueChange={pickStrategy}
            dense
            aria-label="Estratégia"
          >
            {/* Sorteio por bot */}
            {batch && (
              <StrategyOption
                value={RANDOM_STRATEGY}
                name="Sortear para cada bot"
                summary="Cada bot joga uma estratégia do catálogo, com os parâmetros padrão."
                selected={random}
              />
            )}
            {GROUPS.map((group) => {
              const items = strategies.filter((s) => s.group === group);
              if (items.length === 0) return null;
              return (
                <div key={group} className="grid gap-0.5">
                  <div className="flex items-center gap-1.5 pt-2 pb-0.5 pl-0.5 text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">
                    {GROUP_SECTION[group].title}
                    <InfoHint label={`O que são as ${GROUP_SECTION[group].title.toLowerCase()}`}>
                      {GROUP_SECTION[group].hint}
                    </InfoHint>
                  </div>
                  {items.map((item) => (
                    <StrategyOption
                      key={item.key}
                      value={item.key}
                      name={item.name}
                      summary={item.summary}
                      selected={!random && item.key === strategy.key}
                    />
                  ))}
                </div>
              );
            })}
          </RadioGroup>
        </div>

        {/* Prévia, nome, cor, campos extras e parâmetros */}
        <div className="min-h-0 overflow-y-auto px-6 py-5">
          <div className="grid min-w-0 content-start gap-4.5">
            {/* Quantidade */}
            {maxQuantity > 1 && (
              <Controller
                control={form.control}
                name="quantity"
                render={({ field, fieldState }) => (
                  <Field data-invalid={!!fieldState.error}>
                    <FieldLabel htmlFor="bot-quantity">Quantidade</FieldLabel>
                    <Input
                      id="bot-quantity"
                      type="number"
                      numeric
                      min={1}
                      max={maxQuantity}
                      className="w-28"
                      value={Number.isNaN(field.value) ? "" : field.value}
                      aria-invalid={!!fieldState.error}
                      onChange={(event) => pickQuantity(event.target.valueAsNumber)}
                      onBlur={field.onBlur}
                    />
                    {fieldState.error ? (
                      <FieldError errors={[fieldState.error]} />
                    ) : (
                      <FieldDescription>
                        De 1 até {maxQuantity}, as vagas livres da sala. Com mais de um, o nome sai da lista da
                        estratégia e a cor, a profissão e a equipe são automáticas.
                      </FieldDescription>
                    )}
                  </Field>
                )}
              />
            )}

            {/* Profissão */}
            {professionField && (
              <Field>
                <FieldLabel htmlFor="bot-profession">Profissão</FieldLabel>
                <OptionSelect
                  id="bot-profession"
                  options={professionOptions}
                  value={profession ?? RANDOM_PROFESSION}
                  onChange={(next) => form.setValue("profession", next === RANDOM_PROFESSION ? null : next)}
                  search={false}
                />
                <FieldDescription>
                  A renda e os riscos do bot seguem a profissão. Sorteando, cada bot recebe uma entre as disponíveis na
                  sala.
                </FieldDescription>
              </Field>
            )}

            {/* Prévia */}
            {!batch && (
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
            )}

            {/* Nome */}
            {!batch && (
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
            )}

            {/* Cor */}
            {!batch && (
              <Field>
                <FieldLabel>Cor</FieldLabel>
                <ColorSwatchPicker
                  colors={PLAYER_SWATCHES}
                  taken={playerOwners(others)}
                  value={color}
                  onChange={(next) => form.setValue("color", next)}
                  columns={6}
                  label="Cor do bot"
                />
                <FieldDescription>Já vem a próxima livre. As esmaecidas estão em uso.</FieldDescription>
              </Field>
            )}

            {!batch && extraFields?.(form, others)}

            {/* Parâmetros */}
            {!random && (
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
            )}
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
          {batch ? `Adicionar ${quantity} bots` : submitLabel}
        </Button>
      </div>
    </form>
  );
}
