import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCopy, faPlay, faLink, faFileImport, faCog, faArrowsLeftRight } from "@fortawesome/free-solid-svg-icons";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { formatMoney } from "@/shared/lib/utils/format";
import { normalizeNumberString } from "@/shared/lib/utils";
import { Label } from "@/shared/components/ui/label";
import { Input } from "@/shared/components/ui/input";
import { Button } from "@/shared/components/ui/button";
import type { SimulationInfo, SimulationData } from "@/types";
import { toast } from "sonner";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { useRealtimeSyncSimulationForm } from "../hooks/useRealtimeSyncSimulationForm";
import { useTunnel } from "@/shared/hooks/useTunnel";
import { LobbySettingsDialog } from "./lobby-settings-dialog";

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
  const navigate = useNavigate();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const localIP = window.location.host;
  const { status: tunnelStatus, startTunnel, loading: tunnelLoading } = useTunnel();

  const shareableLink = tunnelStatus?.url ? tunnelStatus.url : `http://${localIP}`;
  const providerName = tunnelStatus?.provider ? tunnelStatus.provider.toUpperCase() : "LOCAL";

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

  const { mutate: createSimulation, loading: loadingCreate } = useMutationApi<
    SimulationInfo,
    { start_date: string; end_date: string; starting_cash: number; monthly_contribution: number }
  >("/api/simulation/create", {
    onSuccess: () => toast.success("Simulação criada com sucesso!"),
    onError: (err) => toast.error(err.message),
  });

  const { mutate: continueSimulation, loading: loadingContinue } = useMutationApi<
    SimulationInfo,
    { end_date: string; starting_cash: number; monthly_contribution: number }
  >("/api/simulation/continue", {
    onSuccess: () => toast.success("Simulação continuada com sucesso!"),
    onError: (err) => toast.error(err.message),
  });

  const copyHostIP = () => {
    navigator.clipboard.writeText(shareableLink);
    toast.success("Link copiado!");
  };

  const disableSimulationActions = loadingCreate || loadingContinue || !isHost;

  return (
    <div className="flex flex-col gap-3 border-t md:border-l md:border-t-0 border-gray-300 pt-6 md:pt-0 md:pl-6">
      <h2 className="text-lg font-semibold">Ações</h2>

      <LobbySettingsDialog
        open={settingsOpen}
        onOpenChange={setSettingsOpen}
        form={form}
        isHost={isHost}
        loading={loadingCreate || loadingContinue}
      />

      <Button
        type="button"
        className="w-full bg-green-600 hover:bg-green-700"
        disabled={disableSimulationActions}
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
        disabled={disableSimulationActions}
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

      <Button type="button" variant="secondary" className="w-full" onClick={() => navigate("/import-assets")}>
        <FontAwesomeIcon icon={faFileImport} className="mr-2" />
        Importar Ativos
      </Button>

      <Button type="button" variant="secondary" className="w-full" disabled>
        <FontAwesomeIcon icon={faArrowsLeftRight} className="mr-2" />
        Comparar Simulações
      </Button>

      <Button type="button" variant="outline" className="w-full" onClick={() => setSettingsOpen(true)}>
        <FontAwesomeIcon icon={faCog} className="mr-2" />
        Configurações
      </Button>

      <div className="mt-auto pt-4 border-t border-gray-200">
        <Label>Link Compartilhável (Via {providerName})</Label>
        <div className="flex mt-1">
          <Input value={shareableLink} readOnly className="rounded-r-none bg-gray-50" />
          <Button type="button" variant="secondary" onClick={copyHostIP} className="rounded-l-none">
            <FontAwesomeIcon icon={faCopy} />
          </Button>
        </div>

        {isHost && tunnelStatus && !tunnelStatus.active && (
          <Button
            type="button"
            variant="outline"
            className="w-full mt-2"
            onClick={startTunnel}
            disabled={tunnelLoading}
          >
            <FontAwesomeIcon icon={faLink} className="mr-2" />
            {tunnelLoading ? "Gerando..." : "Gerar Link Compartilhável"}
          </Button>
        )}
      </div>
    </div>
  );
}
