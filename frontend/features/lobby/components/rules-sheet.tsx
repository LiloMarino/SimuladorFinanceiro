import { useEffect, useState, type CSSProperties } from "react";
import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { CircleCheck, Flag, Info, RefreshCw, Shield, Swords, TriangleAlert, Users, type LucideIcon } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldError,
  FieldLabel,
  FieldLegend,
  FieldSet,
  FieldTitle,
} from "@/shared/components/ui/field";
import { InfoHint } from "@/shared/components/info-hint";
import { Input } from "@/shared/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/shared/components/ui/sheet";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { normalizeNumberString } from "@/shared/lib/utils";
import { formatMoney, formatPositiveInteger } from "@/shared/lib/utils/format";
import { displayDecimal, toCentsString } from "@/shared/lib/utils/display";
import { LIFE_DEFAULTS, withdrawalRateToField } from "@/shared/lib/financial-independence";
import { GAME_TYPE_OPTIONS } from "@/shared/lib/game-types";
import { DEFAULT_GOAL_MULTIPLE, GOAL_SHORTCUTS } from "@/shared/lib/goal";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import { teamColor, teamShortName } from "@/shared/lib/teams";
import type { GameType, PlayerGrouping, TeamNaming, VictoryCriterion } from "@/types";
import type { CoverageCheck } from "../lib/coverage";
import { isPositiveMoney, isWithdrawalRate, withdrawalRateFraction } from "../lib/life-rules";
import {
  PRICE_IMPACT_MODE_LABELS,
  PRICE_IMPACT_PRESETS,
  priceImpactModeOf,
  type PriceImpactMode,
} from "../lib/price-impact";
import { AssistanceFields } from "./assistance-fields";
import { CoverageAlerts } from "./coverage-alerts";
import { LifeFields } from "./life-fields";
import { PeriodPicker } from "./period-picker";
import type { SimulationFormValues } from "./lobby-match";
import { PriceImpactExample } from "./price-impact-example";

// Os campos da vida real somem fora do viver de renda; um valor inutilizável neles volta ao padrão do servidor
const LIFE_FIELD_FALLBACKS = {
  monthlySalary: {
    usable: isPositiveMoney,
    fallback: formatMoney(toCentsString(LIFE_DEFAULTS.monthlySalary).replace(".", "")),
  },
  monthlyExpense: {
    usable: isPositiveMoney,
    fallback: formatMoney(toCentsString(LIFE_DEFAULTS.monthlyExpense).replace(".", "")),
  },
  withdrawalRate: {
    usable: (value: string) => isWithdrawalRate(withdrawalRateFraction(value)),
    fallback: withdrawalRateToField(LIFE_DEFAULTS.withdrawalRate),
  },
} as const;

const GROUPING_OPTIONS: { value: PlayerGrouping; label: string; description: string; icon: LucideIcon }[] = [
  {
    value: "INDIVIDUAL",
    label: "Todos contra todos",
    description: "Cada um por si: vence a melhor carteira.",
    icon: Swords,
  },
  {
    value: "TEAMS",
    label: "Em equipes",
    description: "Cada um opera a própria carteira, mas vence a equipe com a melhor média.",
    icon: Users,
  },
];

type RulesSheetProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  form: UseFormReturn<SimulationFormValues>;
  isHost: boolean;
  hostNickname: string;
  coverageCheck: CoverageCheck;
  /** Ativo citado no exemplo do impacto; vazio quando a base não tem ação */
  exampleTicker: string | undefined;
  saveStatus: { savedAt: number | null; saving: boolean; saveError: Error | null };
  onRestoreDefaults?: () => void;
  /** Regras gravadas numa partida salva: valem como estão, ninguém edita */
  locked?: boolean;
};

/** Regras da partida num painel lateral, com o lobby atrás. Mudanças salvam sozinhas. */
export function RulesSheet({
  open,
  onOpenChange,
  form,
  isHost,
  hostNickname,
  coverageCheck,
  exampleTicker,
  saveStatus,
  onRestoreDefaults,
  locked = false,
}: RulesSheetProps) {
  const [startDate, impactEnabled, impactK, impactT, grouping, gameType, startingCash, goalNetWorth] = useWatch({
    control: form.control,
    name: [
      "startDate",
      "priceImpactEnabled",
      "priceImpactK",
      "priceImpactDecayDays",
      "playerGrouping",
      "gameType",
      "startingCash",
      "goalNetWorth",
    ],
  });
  // Personalizado fica aberto mesmo quando k e T coincidem com um preset
  const [customOpen, setCustomOpen] = useState(false);
  const derivedMode = priceImpactModeOf(impactEnabled, impactK, impactT);
  const impactMode: PriceImpactMode = customOpen && impactEnabled ? "CUSTOM" : derivedMode;
  const readOnly = !isHost || locked;
  const startingCashAmount = Number(normalizeNumberString(startingCash));
  const goalAmount = Number(normalizeNumberString(goalNetWorth));

  // A meta segue no formulário em todos os tipos e o servidor a exige positiva:
  // sair da corrida com a meta vazia devolve o valor padrão, já que o campo some da tela.
  // O que foi digitado em cada tipo fica guardado; só o valor inutilizável de um campo escondido volta ao padrão
  const selectGameType = (value: GameType, onChange: (value: GameType) => void) => {
    onChange(value);
    if (value === "CLASSIC" && !(goalAmount > 0)) {
      form.setValue("goalNetWorth", formatMoney(String(Math.round(startingCashAmount * DEFAULT_GOAL_MULTIPLE * 100))), {
        shouldValidate: true,
      });
    }
    if (value !== "FINANCIAL_INDEPENDENCE") {
      for (const [name, { usable, fallback }] of Object.entries(LIFE_FIELD_FALLBACKS)) {
        const field = name as keyof typeof LIFE_FIELD_FALLBACKS;
        if (!usable(form.getValues(field))) form.setValue(field, fallback);
      }
    }
    void form.trigger();
  };

  const selectImpactMode = (mode: PriceImpactMode) => {
    setCustomOpen(mode === "CUSTOM");
    form.setValue("priceImpactEnabled", mode !== "OFF", { shouldValidate: true });
    if (mode === "REALISTIC" || mode === "STRONG") {
      const preset = PRICE_IMPACT_PRESETS[mode];
      form.setValue("priceImpactK", displayDecimal(preset.k), { shouldValidate: true });
      form.setValue("priceImpactDecayDays", String(preset.decayDays), { shouldValidate: true });
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent size="lg">
        <SheetHeader>
          <SheetTitle>Regras da partida</SheetTitle>
          <SheetDescription>
            {locked
              ? "São as regras gravadas na partida salva: não mudam."
              : isHost
                ? "Mudanças salvam sozinhas e aparecem pra todos."
                : "Modo visualização."}
          </SheetDescription>
        </SheetHeader>

        <form className="flex flex-1 flex-col gap-7 overflow-y-auto px-6 py-5" onSubmit={(e) => e.preventDefault()}>
          {/* Básico */}
          <FieldSet disabled={readOnly}>
            <FieldLegend variant="caption">Básico</FieldLegend>
            <Controller
              control={form.control}
              name="name"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="rules-name">Nome</FieldLabel>
                  <Input {...field} id="rules-name" aria-invalid={fieldState.invalid} />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
            <PeriodPicker form={form} readOnly={readOnly} coverageCheck={coverageCheck} />
            <CoverageAlerts check={coverageCheck} startDate={startDate} />
            <div className="grid grid-cols-2 gap-3">
              {(
                [
                  ["startingCash", "Saldo inicial"],
                  ["monthlyContribution", "Aporte mensal"],
                ] as const
              )
                .filter(([name]) => !(gameType === "FINANCIAL_INDEPENDENCE" && name === "monthlyContribution"))
                .map(([name, label]) => (
                  <Controller
                    key={name}
                    control={form.control}
                    name={name}
                    render={({ field, fieldState }) => (
                      <Field data-invalid={fieldState.invalid}>
                        <FieldLabel htmlFor={`rules-${name}`}>{label}</FieldLabel>
                        <Input
                          {...field}
                          id={`rules-${name}`}
                          inputMode="decimal"
                          numeric
                          aria-invalid={fieldState.invalid}
                          onChange={(e) => field.onChange(formatMoney(e.target.value))}
                        />
                        <FieldError errors={[fieldState.error]} />
                      </Field>
                    )}
                  />
                ))}
            </div>
          </FieldSet>

          {/* Modo de jogo */}
          <FieldSet disabled={readOnly}>
            <FieldLegend variant="caption">Modo de jogo</FieldLegend>
            <Controller
              control={form.control}
              name="playerGrouping"
              render={({ field }) => (
                <RadioGroup
                  value={field.value}
                  onValueChange={(value) => field.onChange(value as PlayerGrouping)}
                  disabled={readOnly}
                  className="grid-cols-2"
                >
                  {GROUPING_OPTIONS.map((option) => (
                    <FieldLabel key={option.value} htmlFor={`grouping-${option.value}`}>
                      <Field orientation="horizontal">
                        <RadioGroupItem value={option.value} id={`grouping-${option.value}`} />
                        <FieldContent>
                          <FieldTitle>
                            <option.icon className="size-3.5 text-muted-foreground" />
                            {option.label}
                          </FieldTitle>
                          <FieldDescription>{option.description}</FieldDescription>
                        </FieldContent>
                      </Field>
                    </FieldLabel>
                  ))}
                </RadioGroup>
              )}
            />
            {grouping === "TEAMS" && (
              <>
                <Controller
                  control={form.control}
                  name="teamNaming"
                  render={({ field }) => (
                    <div className="grid grid-cols-[1fr_auto] items-center gap-3 rounded-[10px] border p-3">
                      <FieldContent>
                        <FieldTitle>Nome das equipes</FieldTitle>
                        <FieldDescription>Muda só o rótulo; a cor é a mesma.</FieldDescription>
                      </FieldContent>
                      <ToggleGroup
                        variant="segmented"
                        aria-label="Nome das equipes"
                        value={[field.value]}
                        onValueChange={(values) => values[0] && field.onChange(values[0] as TeamNaming)}
                        disabled={readOnly}
                      >
                        {(["COLOR", "NUMBER"] as const).map((naming) => (
                          <ToggleGroupItem key={naming} value={naming} style={{ "--team": teamColor(2) } as CSSProperties}>
                            <Shield className="fill-(--team) stroke-(--team)" />
                            {teamShortName(2, naming)}
                          </ToggleGroupItem>
                        ))}
                      </ToggleGroup>
                    </div>
                  )}
                />
                <Alert variant="info">
                  <Info />
                  <AlertTitle>Cada jogador escolhe a equipe no próprio card</AlertTitle>
                  <AlertDescription>Começa todo mundo sem equipe. Equipes desiguais valem: conta a média.</AlertDescription>
                </Alert>
              </>
            )}
          </FieldSet>

          {/* Tipo de partida */}
          <FieldSet disabled={readOnly}>
            <FieldLegend variant="caption">Tipo de partida</FieldLegend>
            <Controller
              control={form.control}
              name="gameType"
              render={({ field }) => (
                <RadioGroup
                  value={field.value}
                  onValueChange={(value) => selectGameType(value as GameType, field.onChange)}
                  disabled={readOnly}
                  className="grid-flow-col auto-cols-fr"
                >
                  {GAME_TYPE_OPTIONS.map(([value, type]) => (
                    <FieldLabel key={value} htmlFor={`game-type-${value}`}>
                      <Field>
                        <div className="flex items-center justify-between">
                          <type.icon className="size-[18px] text-muted-foreground" />
                          <RadioGroupItem value={value} id={`game-type-${value}`} />
                        </div>
                        <FieldContent>
                          <FieldTitle>{type.label}</FieldTitle>
                          <FieldDescription>{type.description}</FieldDescription>
                        </FieldContent>
                      </Field>
                    </FieldLabel>
                  ))}
                </RadioGroup>
              )}
            />
          </FieldSet>

          {/* Meta */}
          {gameType === "GOAL_RACE" && (
            <FieldSet disabled={readOnly}>
              <FieldLegend variant="caption">Meta</FieldLegend>
              <Controller
                control={form.control}
                name="goalNetWorth"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="rules-goalNetWorth">
                      Meta de patrimônio
                      <InfoHint label="Como funciona a meta">
                        <div className="space-y-1 text-left">
                          <p>É o patrimônio (caixa, renda fixa e ações) que um jogador precisa atingir para vencer.</p>
                          <p>Ex.: com saldo inicial de R$ 100.000, a meta de 10× é R$ 1.000.000.</p>
                          <p>Meta alta demais pode não ser alcançada até a data final; nesse caso vence quem chegar mais perto.</p>
                        </div>
                      </InfoHint>
                    </FieldLabel>
                    <Input
                      {...field}
                      id="rules-goalNetWorth"
                      inputMode="decimal"
                      numeric
                      aria-invalid={fieldState.invalid}
                      onChange={(e) => field.onChange(formatMoney(e.target.value))}
                    />
                    <div className="flex flex-wrap gap-1.5">
                      {GOAL_SHORTCUTS.map((multiple) => (
                        <Button
                          key={multiple}
                          type="button"
                          size="xs"
                          variant={startingCashAmount > 0 && goalAmount === startingCashAmount * multiple ? "info" : "outline"}
                          onClick={() => field.onChange(formatMoney(String(Math.round(startingCashAmount * multiple * 100))))}
                        >
                          {multiple}× o saldo inicial
                        </Button>
                      ))}
                    </div>
                    <div className="flex items-center gap-1">
                      <FieldDescription>Em reais do dia, sem descontar a inflação</FieldDescription>
                      <InfoHint label="Meta e inflação">
                        Numa partida longa, R$ 1 milhão no fim compra bem menos do que no começo: o valor da meta não
                        acompanha os preços.
                      </InfoHint>
                    </div>
                    <FieldError errors={[fieldState.error]} />
                  </Field>
                )}
              />
              <Alert variant="info">
                <Flag />
                <AlertTitle>Quem vence já está definido</AlertTitle>
                <AlertDescription>
                  A partida termina no dia em que alguém chega à meta. Chegando dois no mesmo dia, vence o maior
                  patrimônio. Se ninguém chegar até a data final, vence quem ficou mais perto. Em equipes, conta a média
                  do patrimônio dos membros.
                </AlertDescription>
              </Alert>
            </FieldSet>
          )}

          {/* Vida real */}
          {gameType === "FINANCIAL_INDEPENDENCE" && <LifeFields form={form} readOnly={readOnly} />}

          {/* Quem vence */}
          {gameType === "CLASSIC" && (
            <FieldSet disabled={readOnly}>
              <FieldLegend variant="caption">
                Quem vence{grouping === "TEAMS" ? " (em equipes: a média dos membros)" : ""}
              </FieldLegend>
              <Controller
                control={form.control}
                name="victoryCriterion"
                render={({ field }) => (
                  <RadioGroup
                    value={field.value}
                    onValueChange={(value) => field.onChange(value as VictoryCriterion)}
                    disabled={readOnly}
                    className="grid-cols-2"
                  >
                    {Object.entries(VICTORY_CRITERIA).map(([value, criterion]) => (
                      <FieldLabel key={value} htmlFor={`criterion-${value}`}>
                        <Field orientation="horizontal">
                          <RadioGroupItem value={value} id={`criterion-${value}`} />
                          <FieldContent>
                            <FieldTitle>{criterion.label}</FieldTitle>
                            <FieldDescription>{criterion.description}</FieldDescription>
                          </FieldContent>
                        </Field>
                      </FieldLabel>
                    ))}
                  </RadioGroup>
                )}
              />
            </FieldSet>
          )}

          {/* Assistências */}
          <AssistanceFields
            form={form}
            readOnly={readOnly}
            lockNote={locked ? "Regras da partida salva não mudam" : isHost ? null : "Só o host muda as regras"}
          />

          {/* Impacto de preço */}
          <FieldSet disabled={readOnly}>
            <FieldLegend variant="caption">Mercado · impacto de preço das ordens</FieldLegend>
            <ToggleGroup
              variant="segmented"
              aria-label="Impacto de preço"
              value={[impactMode]}
              onValueChange={(values) => values[0] && selectImpactMode(values[0] as PriceImpactMode)}
              disabled={readOnly}
              className="w-full"
            >
              {(Object.keys(PRICE_IMPACT_MODE_LABELS) as PriceImpactMode[]).map((mode) => (
                <ToggleGroupItem key={mode} value={mode} className="flex-1">
                  {PRICE_IMPACT_MODE_LABELS[mode]}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>

            {impactMode === "CUSTOM" && (
              <div className="grid grid-cols-2 gap-3">
                <Controller
                  control={form.control}
                  name="priceImpactK"
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="rules-k">Intensidade (k)</FieldLabel>
                      <Input {...field} id="rules-k" inputMode="decimal" numeric aria-invalid={fieldState.invalid} />
                      <FieldError errors={[fieldState.error]} />
                    </Field>
                  )}
                />
                <Controller
                  control={form.control}
                  name="priceImpactDecayDays"
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="rules-t">Volta ao histórico (T, em pregões)</FieldLabel>
                      <Input
                        {...field}
                        id="rules-t"
                        inputMode="numeric"
                        numeric
                        aria-invalid={fieldState.invalid}
                        onChange={(e) => field.onChange(formatPositiveInteger(e.target.value))}
                      />
                      <FieldError errors={[fieldState.error]} />
                    </Field>
                  )}
                />
              </div>
            )}

            {impactEnabled && <PriceImpactExample k={impactK} decayDays={impactT} ticker={exampleTicker} />}
          </FieldSet>
        </form>

        <SheetFooter>
          <SaveStatus
            isHost={isHost}
            locked={locked}
            hostNickname={hostNickname}
            invalidFields={Object.keys(form.formState.errors).length}
            {...saveStatus}
          />
          {isHost && !locked && onRestoreDefaults && (
            <Button variant="outline" disabled={saveStatus.saving} onClick={onRestoreDefaults}>
              <RefreshCw />
              Restaurar padrões
            </Button>
          )}
          <SheetClose render={<Button variant="outline" />}>Fechar</SheetClose>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}

type SaveStatusProps = RulesSheetProps["saveStatus"] & {
  isHost: boolean;
  locked: boolean;
  hostNickname: string;
  invalidFields: number;
};

/** Rodapé do painel: o que aconteceu com a última mudança, no lugar do toast repetido. */
function SaveStatus({ isHost, locked, hostNickname, invalidFields, savedAt, saving, saveError }: SaveStatusProps) {
  const now = useNow(1000);

  if (locked) {
    return <span className="text-[13px] text-muted-foreground">Regras de uma partida salva não mudam.</span>;
  }

  if (!isHost) {
    return (
      <span className="text-[13px] text-muted-foreground">
        Só {hostNickname} (host) edita. Você vê as mudanças na hora.
      </span>
    );
  }
  if (invalidFields > 0 || saveError) {
    return (
      <span className="flex items-center gap-1.5 text-[13px] text-destructive">
        <TriangleAlert className="size-3.5" />
        {invalidFields > 0
          ? `${invalidFields} ${invalidFields === 1 ? "campo com problema" : "campos com problema"}: nada foi salvo`
          : `Não salvou: ${saveError?.message}`}
      </span>
    );
  }
  if (saving) return <span className="text-[13px] text-muted-foreground">Salvando…</span>;
  if (savedAt) {
    const seconds = Math.max(0, Math.round((now - savedAt) / 1000));
    return (
      <span className="flex items-center gap-1.5 text-xs text-success">
        <CircleCheck className="size-3.5" />
        Salvo há {seconds} s · todos já veem
      </span>
    );
  }
  return <span className="text-[13px] text-muted-foreground">Mudanças salvam sozinhas.</span>;
}

/** Relógio que avança a cada `intervalMs`, para textos como "há 3 s". */
function useNow(intervalMs: number) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), intervalMs);
    return () => clearInterval(timer);
  }, [intervalMs]);
  return now;
}
