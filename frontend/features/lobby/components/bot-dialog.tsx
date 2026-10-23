import { Controller, useForm, useWatch } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Dices, UserPlus } from "lucide-react";
import { ErrorState } from "@/shared/components/error-state";
import { InfoHint } from "@/shared/components/info-hint";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { StrategyParamsForm } from "@/shared/components/strategy-params-form";
import { TeamGrid } from "@/shared/components/team-grid";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/shared/components/ui/dialog";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useSimulationSettings } from "@/shared/hooks/queries/useSimulationSettings";
import { GROUP_SECTION } from "@/shared/lib/strategy-groups";
import { defaultValues, draftErrors, fromDraft, toDraft } from "@/shared/lib/strategy-params";
import { cn } from "@/shared/lib/utils";
import type { PlayerGrouping, RoomPlayer, StrategyGroup, StrategyInfo, TeamNaming } from "@/types";
import { useAddBot } from "../hooks/mutations/useAddBot";
import { useUpdateBot } from "../hooks/mutations/useUpdateBot";
import { useBotStrategies } from "../hooks/queries/useBotStrategies";
import { useBotTickers } from "../hooks/queries/useBotTickers";
import { addValues, editValues, NAME_TAKEN_STATUS, type BotFormValues } from "../lib/bot-form";
import { drawBotName, isDrawnName, nameTaken } from "../lib/bot-names";
import { BotColorSwatches } from "./bot-color-swatches";

const GROUPS: StrategyGroup[] = ["reference", "tactic"];
const BOT_NAME_MAX = 30;
const NAME_TAKEN_MESSAGE = "Já tem um jogador com esse nome na sala. Sorteie outro ou mude.";

type BotDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** O bot a configurar; sem ele, o diálogo adiciona um */
  bot?: RoomPlayer;
  grouping: PlayerGrouping;
  naming: TeamNaming;
};

/** Adicionar ou configurar um bot: a estratégia à esquerda e, à direita, o nome, a cor, a equipe e os parâmetros. */
export function BotDialog({ open, onOpenChange, bot, grouping, naming }: BotDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent flush className="max-h-[calc(100vh-4rem)] grid-rows-[auto_minmax(0,1fr)] overflow-hidden sm:max-w-245">
        <BotDialogContent bot={bot} grouping={grouping} naming={naming} onClose={() => onOpenChange(false)} />
      </DialogContent>
    </Dialog>
  );
}

type BotDialogContentProps = Pick<BotDialogProps, "bot" | "grouping" | "naming"> & { onClose: () => void };

/** Cabeçalho e a lista de estratégias resolvida: o formulário só monta com o dado pronto. */
function BotDialogContent({ bot, grouping, naming, onClose }: BotDialogContentProps) {
  const strategies = useBotStrategies();
  const tickers = useBotTickers();
  const { data: players } = useRoomPlayers();
  const { data: settings } = useSimulationSettings();

  const ready = strategies.data && strategies.data.length > 0 && players && settings;

  return (
    <>
      {/* Cabeçalho */}
      <div className="border-b px-6 py-5 pr-14">
        <DialogTitle large>{bot ? "Configurar bot" : "Adicionar bot"}</DialogTitle>
        <DialogDescription>Joga sozinho, com carteira própria e as mesmas regras de dinheiro de todos.</DialogDescription>
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
        <BotForm
          strategies={strategies.data}
          tickerOptions={tickers.data ?? []}
          players={players}
          startingCash={settings.simulation.starting_cash}
          bot={bot}
          grouping={grouping}
          naming={naming}
          onClose={onClose}
        />
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

type BotFormProps = Pick<BotDialogProps, "bot" | "grouping" | "naming"> & {
  strategies: StrategyInfo[];
  tickerOptions: string[];
  players: RoomPlayer[];
  startingCash: string;
  onClose: () => void;
};

function BotForm({ strategies, tickerOptions, players, startingCash, bot, grouping, naming, onClose }: BotFormProps) {
  // Cor, nome e equipe dos outros jogadores: o bot em edição não conta contra si mesmo
  const others = players.filter((p) => p.nickname !== bot?.nickname);
  const takenNames = others.map((p) => p.nickname);

  // O nome vale contra quem está na sala agora: a validação roda a cada digitação
  const schema = z.object({
    nickname: z
      .string()
      .trim()
      .min(1, "Dê um nome ao bot.")
      .max(BOT_NAME_MAX, `Use até ${BOT_NAME_MAX} letras.`)
      .refine((name) => !nameTaken(name, takenNames), NAME_TAKEN_MESSAGE),
    strategyKey: z.string(),
    color: z.string(),
    team: z.number().nullable(),
    drafts: z.record(z.string(), z.any()),
  });

  const form = useForm<BotFormValues>({
    resolver: zodResolver(schema),
    mode: "onChange",
    defaultValues: bot ? editValues(strategies, bot) : addValues(strategies, players),
  });
  const { strategyKey, nickname, color, team, drafts } = useWatch({ control: form.control }) as BotFormValues;

  const add = useAddBot();
  const update = useUpdateBot(bot?.nickname ?? "");
  const saving = add.isPending || update.isPending;

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
    const request = {
      nickname: formValues.nickname.trim(),
      strategy_key: strategy.key,
      params: values,
      color: formValues.color,
      team: grouping === "TEAMS" ? formValues.team : null,
    };
    const refuseName = (status: number) => {
      if (status === NAME_TAKEN_STATUS) form.setError("nickname", { type: "server", message: NAME_TAKEN_MESSAGE });
    };
    const options = { onSuccess: onClose, onError: (err: { status: number }) => refuseName(err.status) };
    if (bot) update.mutate(request, options);
    else add.mutate(request, options);
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

        {/* Prévia, nome, cor, equipe e parâmetros */}
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
              <span className="ml-auto shrink-0 text-xs text-muted-foreground">Assim ele aparece na sala</span>
            </div>

            {/* Nome */}
            <Controller
              control={form.control}
              name="nickname"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="bot-nickname">Nome</FieldLabel>
                  <div className="flex gap-2">
                    <Input
                      {...field}
                      id="bot-nickname"
                      autoComplete="off"
                      aria-invalid={fieldState.invalid}
                    />
                    <Button
                      type="button"
                      variant="outline"
                      className="shrink-0"
                      onClick={() =>
                        form.setValue("nickname", drawBotName(strategy, [...takenNames, nickname]), {
                          shouldValidate: true,
                        })
                      }
                    >
                      <Dices className="size-[15px]" />
                      Sortear
                    </Button>
                  </div>
                  {fieldState.invalid ? (
                    <FieldError errors={[fieldState.error]} />
                  ) : (
                    <FieldDescription>Da lista da estratégia; é o nome no ranking.</FieldDescription>
                  )}
                </Field>
              )}
            />

            {/* Cor */}
            <Field>
              <FieldLabel>Cor</FieldLabel>
              <BotColorSwatches
                owners={others}
                selected={color}
                onSelect={(next) => form.setValue("color", next)}
              />
              <FieldDescription>Já vem a próxima livre. As riscadas estão em uso.</FieldDescription>
            </Field>

            {/* Equipe */}
            {grouping === "TEAMS" && (
              <Field>
                <FieldLabel>Equipe</FieldLabel>
                <TeamGrid
                  players={others}
                  naming={naming}
                  selected={team}
                  onSelect={(next) => form.setValue("team", next)}
                />
                <FieldDescription>
                  No modo em equipes, o host escolhe a equipe do bot. “Distribuir quem falta” também distribui os bots.
                </FieldDescription>
              </Field>
            )}

            {/* Parâmetros */}
            <StrategyParamsForm
              key={strategy.key}
              strategy={strategy}
              draft={draft}
              saved={bot?.bot?.strategy_key === strategy.key ? bot.bot.params : {}}
              errors={errors}
              tickerOptions={tickerOptions}
              cash={startingCash}
              cashLabel="o saldo inicial"
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
          {saving ? <Spinner /> : bot ? null : <UserPlus className="size-3.5" />}
          {bot ? "Salvar" : "Adicionar bot"}
        </Button>
      </div>
    </form>
  );
}
