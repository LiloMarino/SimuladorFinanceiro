import { useEffect, useRef, useState } from "react";
import { useWatch, type UseFormReturn } from "react-hook-form";
import { useDebounce } from "use-debounce";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { CreateSimulationRequest, SimulationSettingsData } from "@/types";
import type { SimulationFormValues } from "../components/lobby-match";
import { useAsyncLock } from "@/shared/hooks/useAsyncLock";
import { toFormValues, toSettingsBody } from "../lib/simulation-form";
import { useUpdateSimulationSettings } from "./mutations/useUpdateSimulationSettings";

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

  const {
    mutateAsync: updateSettings,
    isPending: saving,
    error: saveError,
  } = useUpdateSimulationSettings();

  /** 🔹 Realtime → Form */
  useRealtime(
    "simulation_settings_update",
    (data) => {
      void lock.runExclusive(async () => {
        form.reset(toFormValues(data));
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
      await updateSettings(payload, { onSuccess: () => setSavedAt(Date.now()) }).catch(() => undefined);
    });
  }, [debouncedValues, isHost, locked, updateSettings, form.formState.isValid, lock]);

  return { savedAt, saving, saveError };
}
