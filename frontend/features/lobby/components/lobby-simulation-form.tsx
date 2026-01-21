import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCopy, faPlay, faLink } from "@fortawesome/free-solid-svg-icons";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { formatMoney } from "@/shared/lib/utils/format";
import { normalizeNumberString } from "@/shared/lib/utils";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import { Button } from "@/shared/components/ui/button";
import type { SimulationInfo, SimulationData } from "@/types";
import { toast } from "sonner";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { useRealtimeSyncSimulationForm } from "../hooks/useRealtimeSyncSimulationForm";
import { useTunnel } from "@/shared/hooks/useTunnel";

const simulationFormSchema = z
  .object({
    startDate: z.string().min(1, "Selecione a data inicial"),
    endDate: z.string().min(1, "Selecione a data final"),
    startingCash: z
      .string()
      .min(1, "O saldo inicial deve ser maior que 0")
      .refine((val) => Number(normalizeNumberString(val)) > 0, "O saldo inicial deve ser maior que 0"),
    monthlyContribution: z
      .string()
      .refine((val) => Number(normalizeNumberString(val)) >= 0, "O aporte mensal não pode ser negativo"),
  })
  .refine((data) => new Date(data.endDate) > new Date(data.startDate), {
    message: "A data final deve ser maior que a data inicial",
    path: ["endDate"],
  });

export type SimulationFormValues = z.infer<typeof simulationFormSchema>;

export function LobbySimulationForm({ simulationData, isHost }: { simulationData: SimulationData; isHost: boolean }) {
  const localIP = window.location.host;
  const { status: tunnelStatus, startTunnel, loading: tunnelLoading } = useTunnel();

  // Usa URL do túnel se ativo, senão usa IP local
  const shareableLink = tunnelStatus?.active && tunnelStatus.url ? tunnelStatus.url : `http://${localIP}`;

  const form = useForm<SimulationFormValues>({
    resolver: zodResolver(simulationFormSchema),
    mode: "onChange",
    defaultValues: {
      startDate: simulationData.start_date,
      endDate: simulationData.end_date,
      startingCash: formatMoney(String(simulationData.starting_cash * 100)),
      monthlyContribution: formatMoney(String(simulationData.monthly_contribution * 100)),
    },
  });

  useRealtimeSyncSimulationForm({
    form,
    initial: simulationData,
    isHost,
    debounceMs: 400,
  });

  // Mutação de criação
  const { mutate: createSimulation, loading: loadingCreate } = useMutationApi<
    SimulationInfo,
    { start_date: string; end_date: string; starting_cash: number; monthly_contribution: number }
  >("/api/simulation/create", {
    onSuccess: () => {
      toast.success("Simulação criada com sucesso!");
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  // Mutação de continuação
  const { mutate: continueSimulation, loading: loadingContinue } = useMutationApi<
    SimulationInfo,
    { end_date: string; starting_cash: number; monthly_contribution: number }
  >("/api/simulation/continue", {
    onSuccess: () => {
      toast.success("Simulação continuada com sucesso!");
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  const copyHostIP = () => {
    navigator.clipboard.writeText(shareableLink);
    toast.success("Link copiado!");
  };

  const disableFields = loadingCreate || loadingContinue || !isHost;
  return (
    <div className="space-y-6 border-t md:border-l md:border-t-0 border-gray-300 pt-6 md:pt-0 md:pl-6">
      <h2 className="text-lg font-semibold">Configurações da Simulação</h2>

      <Form {...form}>
        <form className="space-y-6">
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

          <FormField
            control={form.control}
            name="startingCash"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Saldo Inicial (R$)</FormLabel>
                <FormControl>
                  <Input
                    inputMode="decimal"
                    placeholder="Saldo inicial da simulação"
                    {...field}
                    onChange={(e) => field.onChange(formatMoney(e.target.value))}
                    disabled={disableFields}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="monthlyContribution"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Aporte Mensal (R$)</FormLabel>
                <FormControl>
                  <Input
                    inputMode="decimal"
                    placeholder="Aporte mensal da simulação"
                    {...field}
                    onChange={(e) => field.onChange(formatMoney(e.target.value))}
                    disabled={disableFields}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Link Compartilhável */}
          <div>
            <FormLabel>{tunnelStatus?.active ? "Link Compartilhável (Túnel Ativo)" : "IP do Host (Local)"}</FormLabel>
            <div className="flex mt-1">
              <Input value={shareableLink} readOnly className="rounded-r-none bg-gray-50" />
              <Button type="button" variant="secondary" onClick={copyHostIP} className="rounded-l-none">
                <FontAwesomeIcon icon={faCopy} />
              </Button>
            </div>
            {tunnelStatus?.active && (
              <p className="text-xs text-green-600 mt-1">✅ Túnel ativo via {tunnelStatus.provider}</p>
            )}
          </div>

          {/* Botão de Gerar Link Compartilhável (apenas host) */}
          {isHost && tunnelStatus?.enabled && !tunnelStatus.active && (
            <Button type="button" variant="outline" className="w-full" onClick={startTunnel} disabled={tunnelLoading}>
              <FontAwesomeIcon icon={faLink} className="mr-2" />
              {tunnelLoading ? "Gerando..." : "Gerar Link Compartilhável"}
            </Button>
          )}

          {/* Botões */}
          <div className="space-y-2">
            <Button
              type="button"
              className="w-full bg-green-600 hover:bg-green-700"
              onClick={() =>
                createSimulation({
                  start_date: form.getValues("startDate"),
                  end_date: form.getValues("endDate"),
                  starting_cash: Number(normalizeNumberString(form.getValues("startingCash"))),
                  monthly_contribution: Number(normalizeNumberString(form.getValues("monthlyContribution"))),
                })
              }
            >
              <FontAwesomeIcon icon={faPlay} className="mr-2" />
              Iniciar Simulação
            </Button>

            <Button
              type="button"
              className="w-full bg-blue-600 hover:bg-blue-700"
              onClick={() =>
                continueSimulation({
                  end_date: form.getValues("endDate"),
                  starting_cash: Number(normalizeNumberString(form.getValues("startingCash"))),
                  monthly_contribution: Number(normalizeNumberString(form.getValues("monthlyContribution"))),
                })
              }
            >
              <FontAwesomeIcon icon={faPlay} className="mr-2" />
              Continuar Simulação
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
