import { useCallback, useEffect, useRef, useState } from "react";
import { useWatch, type UseFormReturn } from "react-hook-form";
import { useDebounce } from "use-debounce";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { CreateSimulationRequest, SimulationSettingsData } from "@/types";
import type { SimulationFormValues } from "../components/lobby-match";
import { useAsyncLock } from "@/shared/hooks/useAsyncLock";
import { ASSISTANCES, type AssistanceField } from "@/shared/lib/assistance";
import { toFormValues, toSettingsBody } from "../lib/simulation-form";
import { useRestoreSimulationSettings } from "./mutations/useRestoreSimulationSettings";
import { useUpdateSimulationSettings } from "./mutations/useUpdateSimulationSettings";

type AssistanceChoice = Record<AssistanceField, boolean>;

const assistancesOf = (values: SimulationFormValues): AssistanceChoice =>
  Object.fromEntries(ASSISTANCES.map(({ field }) => [field, values[field]])) as AssistanceChoice;

export function useRealtimeSyncSimulationForm({
  form,
  initial,
  isHost,
  locked,
  debounceMs,
}: {
  form: UseFormReturn<SimulationFormValues>;
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
  const lastSentRef = useRef<CreateSimulationRequest | null>(toSettingsBody(toFormValues(initial)));
  // As assistências que o servidor confirmou: a escolha recusada volta para elas
  const confirmedAssistancesRef = useRef(assistancesOf(toFormValues(initial)));
  // A escolha de assistências que o servidor recusou; some quando um salvamento é confirmado
  const [rejectedAssistances, setRejectedAssistances] = useState<AssistanceChoice | null>(null);

  const {
    mutateAsync: updateSettings,
    isPending: saving,
    error: saveError,
    reset: resetUpdate,
  } = useUpdateSimulationSettings();
  const {
    mutateAsync: requestRestoreDefaults,
    isPending: restoring,
    error: restoreError,
  } = useRestoreSimulationSettings();

  /** Aplica a confirmação do servidor sem deixá-la voltar pelo autosave. */
  const applySettings = (settings: SimulationSettingsData) => {
    const formValues = toFormValues(settings);
    lastSentRef.current = toSettingsBody(formValues);
    confirmedAssistancesRef.current = assistancesOf(formValues);
    form.reset(formValues);
  };

  /** O interruptor volta ao valor confirmado e a escolha fica guardada para "Tentar de novo". */
  const rejectAssistances = useCallback(
    (attempted: SimulationFormValues) => {
      const chosen = assistancesOf(attempted);
      const confirmed = confirmedAssistancesRef.current;
      if (ASSISTANCES.every(({ field }) => chosen[field] === confirmed[field])) return;
      setRejectedAssistances(chosen);
      for (const { field } of ASSISTANCES) form.setValue(field, confirmed[field], { shouldValidate: true });
    },
    [form],
  );

  const retryAssistances = () => {
    if (!rejectedAssistances) return;
    for (const { field } of ASSISTANCES) form.setValue(field, rejectedAssistances[field], { shouldValidate: true });
    setRejectedAssistances(null);
  };

  /** 🔹 Realtime → Form */
  useRealtime(
    "simulation_settings_update",
    (data) => {
      void lock.runExclusive(async () => {
        applySettings(data);
      });
    },
    !isHost,
  );

  /** 🔹 Form → API */
  const values = useWatch({ control: form.control }) as SimulationFormValues;
  const [debouncedValues] = useDebounce(values, debounceMs);

  useEffect(() => {
    if (!isHost || locked) return;
    if (!form.formState.isValid) return;
    if (!debouncedValues) return;
    if (lock.isLocked()) return;

    // O corpo anterior e o novo saem do toSettingsBody: o JSON compara as chaves na mesma ordem
    const payload = toSettingsBody(debouncedValues);

    // Descarta duplicatas reais
    const last = lastSentRef.current;
    if (last && JSON.stringify(last) === JSON.stringify(payload)) return;
    lastSentRef.current = payload;

    void lock.runExclusive(async () => {
      // A falha fica em `saveError`, mostrada no rodapé do painel de regras
      await updateSettings(payload, {
        onSuccess: () => {
          confirmedAssistancesRef.current = assistancesOf(debouncedValues);
          setRejectedAssistances(null);
          setSavedAt(Date.now());
        },
      }).catch(() => rejectAssistances(debouncedValues));
    });
  }, [debouncedValues, isHost, locked, updateSettings, form.formState.isValid, lock, rejectAssistances]);

  const restoreDefaults = () =>
    lock.runExclusive(async () => {
      try {
        const settings = await requestRestoreDefaults();
        resetUpdate();
        applySettings(settings);
        setSavedAt(Date.now());
      } catch {
        // A mutação guarda o erro para o rodapé do painel.
      }
    });

  /** Regras que o servidor já gravou (um preset carregado): entram no formulário sem voltar pelo autosave. */
  const applyServerSettings = (settings: SimulationSettingsData) =>
    lock.runExclusive(async () => {
      resetUpdate();
      applySettings(settings);
      setSavedAt(Date.now());
    });

  return {
    savedAt,
    saving: saving || restoring,
    restoring,
    saveError: saveError ?? restoreError,
    rejectedAssistances: rejectedAssistances !== null,
    retryAssistances,
    restoreDefaults,
    applyServerSettings,
  };
}
