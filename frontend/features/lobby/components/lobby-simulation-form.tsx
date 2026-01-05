import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCopy, faPlay } from "@fortawesome/free-solid-svg-icons";
import { z } from "zod";
import { useEffect, useRef } from "react";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import { Button } from "@/shared/components/ui/button";
import type { SimulationInfo, SimulationData } from "@/types";
import { toast } from "sonner";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useDebounce } from "use-debounce";

const simulationFormSchema = z
  .object({
    startDate: z.string().min(1, "Selecione a data inicial"),
    endDate: z.string().min(1, "Selecione a data final"),
  })
  .refine((data) => new Date(data.endDate) > new Date(data.startDate), {
    message: "A data final deve ser maior que a data inicial",
    path: ["endDate"],
  });

export type SimulationFormValues = z.infer<typeof simulationFormSchema>;

export function LobbySimulationForm({ simulationData, isHost }: { simulationData: SimulationData; isHost: boolean }) {
  const hostIP = window.location.host;

  const form = useForm<SimulationFormValues>({
    resolver: zodResolver(simulationFormSchema),
    defaultValues: {
      startDate: simulationData.start_date,
      endDate: simulationData.end_date,
    },
  });

  const { mutate: createSimulation, loading } = useMutationApi<
    SimulationInfo,
    { start_date: string; end_date: string }
  >("/api/simulation/create", {
    onSuccess: () => {
      toast.success("Simulação criada com sucesso!");
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  // Atualiza as settings com realtime
  const isRemoteSyncRef = useRef(false);
  useRealtime(
    "simulation_settings_update",
    (data) => {
      isRemoteSyncRef.current = true;

      form.reset({
        startDate: data.start_date,
        endDate: data.end_date,
      });

      // libera no próximo tick
      queueMicrotask(() => {
        isRemoteSyncRef.current = false;
      });
    },
    !isHost
  );

  // Atualiza as settings com debounce
  const { mutate: updateSettings, loading: updating } = useMutationApi<SimulationData, SimulationData>(
    "/api/simulation/settings",
    {
      method: "PUT",
      onSuccess: () => {
        toast.success("Configurações atualizadas");
      },
      onError: (err) => {
        toast.error(err.message);
      },
    }
  );

  // Watch fields individually and debounce them separately to avoid duplicate triggers
  const values = useWatch({
    control: form.control,
  });
  const [debouncedValues] = useDebounce(values, 700);
  const lastSentRef = useRef<{ start_date: string; end_date: string } | null>(simulationData);
  useEffect(() => {
    if (!isHost) return;
    if (isRemoteSyncRef.current) return;
    const { startDate, endDate } = debouncedValues;
    if (!startDate || !endDate) return;
    if (new Date(endDate) <= new Date(startDate)) return;

    const last = lastSentRef.current;
    if (last && last.start_date === startDate && last.end_date === endDate) return;
    lastSentRef.current = { start_date: startDate, end_date: endDate };

    void updateSettings({ start_date: startDate, end_date: endDate }).catch(() => {
      lastSentRef.current = null;
    });
  }, [debouncedValues, isHost, updateSettings]);

  const copyHostIP = () => {
    navigator.clipboard.writeText(hostIP);
    toast.success("IP do host copiado!");
  };

  const onSubmit = (values: SimulationFormValues) => {
    createSimulation({
      start_date: values.startDate,
      end_date: values.endDate,
    });
  };

  const disableFields = loading || updating || !isHost;
  return (
    <div className="space-y-6 border-t md:border-l md:border-t-0 border-gray-300 pt-6 md:pt-0 md:pl-6">
      <h2 className="text-lg font-semibold">Configurações da Simulação</h2>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="startDate"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Data Inicial</FormLabel>
                  <FormControl>
                    <Input type="date" {...field} disabled={disableFields} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="endDate"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Data Final</FormLabel>
                  <FormControl>
                    <Input type="date" {...field} disabled={disableFields} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          {/* Host IP */}
          <div>
            <FormLabel>IP do Host</FormLabel>
            <div className="flex mt-1">
              <Input value={hostIP} readOnly className="rounded-r-none bg-gray-50" />
              <Button type="button" variant="secondary" onClick={copyHostIP} className="rounded-l-none">
                <FontAwesomeIcon icon={faCopy} />
              </Button>
            </div>
          </div>

          <Button type="submit" disabled={loading || updating} className="w-full bg-green-600 hover:bg-green-700">
            <FontAwesomeIcon icon={faPlay} className="mr-2" />
            Iniciar Partida
          </Button>
        </form>
      </Form>
    </div>
  );
}
