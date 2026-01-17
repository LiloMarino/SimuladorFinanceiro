import { useEffect, useRef } from "react";
import { useWatch, type UseFormReturn } from "react-hook-form";
import { useDebounce } from "use-debounce";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { SimulationData } from "@/types";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { toast } from "sonner";
import type { SimulationFormValues } from "../components/lobby-simulation-form";
import { useAsyncLock } from "@/shared/hooks/useAsyncLock";

export function useRealtimeSyncSimulationForm<TForm extends SimulationFormValues>({
  form,
  initial,
  isHost,
  debounceMs,
}: {
  form: UseFormReturn<TForm>;
  initial: SimulationData;
  isHost: boolean;
  debounceMs: number;
}) {
  const lock = useAsyncLock();
  const lastSentRef = useRef<SimulationData | null>(initial);

  const { mutate: updateSettings } = useMutationApi<
    SimulationData,
    { start_date: string; end_date: string; starting_cash: number }
  >("/api/simulation/settings", {
    method: "PUT",
    onSuccess: () => {
      toast.success("Configurações sincronizadas");
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  /** 🔹 Realtime → Form */
  useRealtime(
    "simulation_settings_update",
    (data) => {
      lock.runExclusive(async () => {
        form.reset({
          startDate: data.start_date,
          endDate: data.end_date,
          startingCash: data.starting_cash,
        } as TForm);
      });
    },
    !isHost,
  );

  /** 🔹 Form → API */
  const values = useWatch({ control: form.control }) as TForm;
  const [debouncedValues] = useDebounce(values, debounceMs);

  useEffect(() => {
    if (!isHost) return;
    if (!form.formState.isValid) return;
    if (!debouncedValues) return;
    if (lock.isLocked()) return;

    const { startDate, endDate, startingCash } = debouncedValues;

    // Descarta duplicatas
    const current = { start_date: startDate, end_date: endDate, starting_cash: startingCash };
    const last = lastSentRef.current;
    if (last && JSON.stringify(last) === JSON.stringify(current)) return;
    lastSentRef.current = current;

    void lock.runExclusive(async () => {
      await updateSettings({ start_date: startDate, end_date: endDate, starting_cash: startingCash });
    });
  }, [debouncedValues, isHost, updateSettings, form.formState.isValid, lock]);
}
