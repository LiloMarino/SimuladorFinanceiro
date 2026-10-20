import { useEffect, useRef, useState } from "react";
import { useWatch, type UseFormReturn } from "react-hook-form";
import { useDebounce } from "use-debounce";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { GameType, PlayerGrouping, SimulationSettingsData, TeamNaming, VictoryCriterion } from "@/types";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { SimulationFormValues } from "../components/lobby-match";
import { useAsyncLock } from "@/shared/hooks/useAsyncLock";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayDecimal, displayMoney, toCentsString } from "@/shared/lib/utils/display";

export function useRealtimeSyncSimulationForm<TForm extends SimulationFormValues>({
  form,
  initial,
  isHost,
  locked,
  debounceMs,
}: {
  form: UseFormReturn<TForm>;
  initial: SimulationSettingsData;
  isHost: boolean;
  /** Com partida salva selecionada as regras são as gravadas nela: o servidor recusa a edição */
  locked: boolean;
  debounceMs: number;
}) {
  const lock = useAsyncLock();
  // Momento do último salvamento confirmado: vira o "Salvo há N s" do painel de regras
  const [savedAt, setSavedAt] = useState<number | null>(null);

  /** Mantém o último payload REAL enviado à API */
  const lastSentRef = useRef<SimulationSettingsData | null>({
    ...initial,
    starting_cash: toCentsString(initial.starting_cash),
    monthly_contribution: toCentsString(initial.monthly_contribution),
    goal_net_worth: toCentsString(initial.goal_net_worth),
  });

  const {
    mutateAsync: updateSettings,
    isPending: saving,
    error: saveError,
  } = useApiMutation({
    mutationFn: (body: {
      name: string;
      start_date: string;
      end_date: string;
      starting_cash: string;
      monthly_contribution: string;
      price_impact_enabled: boolean;
      price_impact_k: number;
      price_impact_decay_days: number;
      victory_criterion: VictoryCriterion;
      game_type: GameType;
      goal_net_worth: string;
      player_grouping: PlayerGrouping;
      team_naming: TeamNaming;
    }) => apiFetch<SimulationSettingsData>("/api/simulation/settings", { method: "PUT", body }),
    onSuccess: () => setSavedAt(Date.now()),
  });

  /** 🔹 Realtime → Form */
  useRealtime(
    "simulation_settings_update",
    (data) => {
      lock.runExclusive(async () => {
        form.reset({
          name: data.name,
          startDate: data.start_date,
          endDate: data.end_date,
          startingCash: displayMoney(data.starting_cash),
          monthlyContribution: displayMoney(data.monthly_contribution),
          priceImpactEnabled: data.price_impact_enabled,
          priceImpactK: displayDecimal(data.price_impact_k),
          priceImpactDecayDays: String(data.price_impact_decay_days),
          victoryCriterion: data.victory_criterion,
          gameType: data.game_type,
          goalNetWorth: displayMoney(data.goal_net_worth),
          playerGrouping: data.player_grouping,
          teamNaming: data.team_naming,
        } as TForm);
      });
    },
    !isHost,
  );

  /** 🔹 Form → API */
  const values = useWatch({ control: form.control }) as TForm;
  const [debouncedValues] = useDebounce(values, debounceMs);

  useEffect(() => {
    if (!isHost || locked) return;
    if (!form.formState.isValid) return;
    if (!debouncedValues) return;
    if (lock.isLocked()) return;

    const {
      name,
      startDate,
      endDate,
      startingCash,
      monthlyContribution,
      priceImpactEnabled,
      priceImpactK,
      priceImpactDecayDays,
      victoryCriterion,
      gameType,
      goalNetWorth,
      playerGrouping,
      teamNaming,
    } = debouncedValues;

    // Mesma ordem de chaves do SimulationSettingsData: o descarte de duplicata compara o JSON
    const payload = {
      name,
      start_date: startDate,
      end_date: endDate,
      starting_cash: toCentsString(normalizeNumberString(startingCash)),
      monthly_contribution: toCentsString(normalizeNumberString(monthlyContribution)),
      price_impact_enabled: priceImpactEnabled,
      price_impact_k: Number(normalizeNumberString(priceImpactK)),
      price_impact_decay_days: Number(priceImpactDecayDays),
      victory_criterion: victoryCriterion,
      game_type: gameType,
      goal_net_worth: toCentsString(normalizeNumberString(goalNetWorth)),
      player_grouping: playerGrouping,
      team_naming: teamNaming,
    };

    // Descarta duplicatas reais
    const last = lastSentRef.current;
    if (last && JSON.stringify(last) === JSON.stringify(payload)) return;
    lastSentRef.current = payload;

    void lock.runExclusive(async () => {
      // A falha fica em `saveError`, mostrada no rodapé do painel de regras
      await updateSettings(payload).catch(() => undefined);
    });
  }, [debouncedValues, isHost, locked, updateSettings, form.formState.isValid, lock]);

  return { savedAt, saving, saveError };
}
