import { useState } from "react";
import { useWatch, type UseFormReturn } from "react-hook-form";
import { RefreshCw } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/shared/components/ui/sheet";
import { Tabs, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { normalizeNumberString } from "@/shared/lib/utils";
import { formatMoney } from "@/shared/lib/utils/format";
import { displayDecimal, toCentsString } from "@/shared/lib/utils/display";
import { LIFE_DEFAULTS, withdrawalRateToField } from "@/shared/lib/financial-independence";
import { POLITICAL_GAME_TYPE } from "@/shared/lib/game-types";
import { DEFAULT_GOAL_MULTIPLE } from "@/shared/lib/goal";
import { PRICE_IMPACT_PRESETS, priceImpactModeOf, type PriceImpactMode } from "@/shared/lib/price-impact";
import type { AppliedPreset, GameType, SimulationSettingsData } from "@/types";
import type { CoverageCheck } from "../../lib/coverage";
import { isPositiveMoney, isWithdrawalRate, withdrawalRateFraction } from "../../lib/life-rules";
import type { SimulationFormValues } from "../../lib/simulation-form";
import { AssistanceFields } from "../assistance-fields";
import { ExpansionFields } from "../expansion-fields";
import { LifeFields } from "../life-fields";
import { PresetBar } from "../preset-bar";
import { BasicsFields } from "./basics-fields";
import { GameTypeFields } from "./game-type-fields";
import { GoalFields } from "./goal-fields";
import { GroupingFields } from "./grouping-fields";
import { PriceImpactFields } from "./price-impact-fields";
import { SaveStatus, type RulesSaveStatus } from "./save-status";
import { VictoryFields } from "./victory-fields";

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

type RulesTab = "rules" | "expansions";

type RulesSheetProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  form: UseFormReturn<SimulationFormValues>;
  isHost: boolean;
  hostNickname: string;
  coverageCheck: CoverageCheck;
  /** Ativo citado no exemplo do impacto; vazio quando a base não tem ação */
  exampleTicker: string | undefined;
  saveStatus: RulesSaveStatus;
  onRestoreDefaults?: () => void;
  /** O preset de onde vieram as regras da nova partida, com o que mudou desde que foi carregado */
  appliedPreset: AppliedPreset | null;
  /** As regras que o servidor gravou ao carregar um preset entram no formulário */
  onPresetLoaded: (settings: SimulationSettingsData) => void;
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
  appliedPreset,
  onPresetLoaded,
  locked = false,
}: RulesSheetProps) {
  const [
    startDate,
    impactEnabled,
    impactK,
    impactT,
    grouping,
    gameType,
    startingCash,
    goalNetWorth,
    governmentEnabled,
  ] = useWatch({
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
      "governmentEnabled",
    ],
  });
  const [tab, setTab] = useState<RulesTab>("rules");
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
    if (value === "POLITICAL") form.setValue("playerGrouping", "INDIVIDUAL");
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

        {/* Preset */}
        <PresetBar form={form} isHost={isHost} locked={locked} applied={appliedPreset} onApplyLoaded={onPresetLoaded} />

        {/* Regras e expansões */}
        <div className="px-6">
          <Tabs value={tab} onValueChange={(value) => setTab(value as RulesTab)}>
            <TabsList variant="line">
              <TabsTrigger value="rules">Regras</TabsTrigger>
              <TabsTrigger value="expansions">
                Expansões
                {governmentEnabled && (
                  <Badge variant="info" size="tag">
                    1 ligada
                  </Badge>
                )}
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {tab === "rules" && (
          <form className="flex flex-1 flex-col gap-7 overflow-y-auto px-6 py-5" onSubmit={(e) => e.preventDefault()}>
            {/* Básico */}
            <BasicsFields
              form={form}
              readOnly={readOnly}
              coverageCheck={coverageCheck}
              startDate={startDate}
              gameType={gameType}
            />

            {/* Modo de jogo */}
            <GroupingFields form={form} readOnly={readOnly} grouping={grouping} gameType={gameType} />

            {/* Tipo de partida */}
            <GameTypeFields
              form={form}
              readOnly={readOnly}
              governmentEnabled={governmentEnabled}
              grouping={grouping}
              onSelect={selectGameType}
            />

            {/* Meta */}
            {gameType === "GOAL_RACE" && (
              <GoalFields
                form={form}
                readOnly={readOnly}
                startingCashAmount={startingCashAmount}
                goalAmount={goalAmount}
              />
            )}

            {/* Vida real */}
            {gameType === "FINANCIAL_INDEPENDENCE" && <LifeFields form={form} readOnly={readOnly} />}

            {/* Vitória política */}
            {gameType === "POLITICAL" && (
              <Alert variant="info">
                <POLITICAL_GAME_TYPE.icon />
                <AlertTitle>Quem vence já está definido</AlertTitle>
                <AlertDescription>
                  O partido com mais capital político: 1 ponto por cadeira a cada mês fechado, a aprovação do governo
                  para o partido do presidente e 100 pontos por promessa cumprida. A partida joga até a data final, e
                  todos os filiados do partido vencedor vencem juntos.
                </AlertDescription>
              </Alert>
            )}

            {/* Quem vence */}
            {gameType === "CLASSIC" && <VictoryFields form={form} readOnly={readOnly} grouping={grouping} />}

            {/* Assistências */}
            <AssistanceFields
              form={form}
              readOnly={readOnly}
              loading={saveStatus.restoring}
              rejected={saveStatus.rejectedAssistances}
              onRetry={saveStatus.retryAssistances}
              lockNote={locked ? "Regras da partida salva não mudam" : isHost ? null : "Só o host muda as regras"}
            />

            {/* Impacto de preço */}
            <PriceImpactFields
              form={form}
              readOnly={readOnly}
              mode={impactMode}
              enabled={impactEnabled}
              k={impactK}
              decayDays={impactT}
              exampleTicker={exampleTicker}
              onSelectMode={selectImpactMode}
            />
          </form>
        )}

        {/* Expansões */}
        {tab === "expansions" && (
          <div className="flex-1 overflow-y-auto px-6 py-5">
            <ExpansionFields form={form} readOnly={readOnly} />
          </div>
        )}

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
