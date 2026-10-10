import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Copy, Play, Link, Database, Settings, ArrowLeftRight, FolderOpen, Grid3x3 } from "lucide-react";
import { z } from "zod";
import { useForm, useWatch } from "react-hook-form";
import { useQuery } from "@tanstack/react-query";
import { zodResolver } from "@hookform/resolvers/zod";
import { formatMoney } from "@/shared/lib/utils/format";
import { displayDecimal, toCentsString } from "@/shared/lib/utils/display";
import { normalizeNumberString } from "@/shared/lib/utils";
import { Label } from "@/shared/components/ui/label";
import { Input } from "@/shared/components/ui/input";
import { Button } from "@/shared/components/ui/button";
import type { SimulationInfo, SimulationSettingsData, VictoryCriterion } from "@/types";
import { toast } from "sonner";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useRealtimeSyncSimulationForm } from "../hooks/useRealtimeSyncSimulationForm";
import { useTunnel } from "@/shared/hooks/useTunnel";
import { LobbySettingsDialog } from "./lobby-settings-dialog";
import { LoadSimulationDialog } from "./load-simulation-dialog";
import { CoverageAlerts } from "./coverage-alerts";
import { checkCoverage } from "../lib/coverage";
import { seriesCoverageOptions } from "@/shared/lib/queries/seriesCoverageOptions";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";

const simulationFormSchema = z
  .object({
    name: z.string().min(1, "Informe um nome para a simulação"),
    startDate: z.string().min(1, "Selecione a data inicial"),
    endDate: z.string().min(1, "Selecione a data final"),
    startingCash: z
      .string()
      .min(1, "O saldo inicial deve ser maior que 0")
      .refine((val) => Number(normalizeNumberString(val)) > 0, "O saldo inicial deve ser maior que 0"),
    monthlyContribution: z
      .string()
      .refine((val) => Number(normalizeNumberString(val)) >= 0, "O aporte mensal não pode ser negativo"),
    priceImpactEnabled: z.boolean(),
    priceImpactK: z
      .string()
      .min(1, "Informe a intensidade")
      .refine((val) => Number(normalizeNumberString(val)) >= 0, "A intensidade não pode ser negativa"),
    priceImpactDecayDays: z
      .string()
      .refine((val) => Number.isInteger(Number(val)) && Number(val) >= 1, "Informe ao menos 1 pregão"),
    victoryCriterion: z.custom<VictoryCriterion>((value) => typeof value === "string" && value in VICTORY_CRITERIA),
  })
  .refine((data) => new Date(data.endDate) > new Date(data.startDate), {
    message: "A data final deve ser maior que a data inicial",
    path: ["endDate"],
  });

export type SimulationFormValues = z.infer<typeof simulationFormSchema>;

export function LobbySimulationForm({ simulationData, isHost }: { simulationData: SimulationSettingsData; isHost: boolean }) {
  const navigate = useNavigate();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [loadOpen, setLoadOpen] = useState(false);
  const localIP = window.location.host;
  const { status: tunnelStatus, startTunnel, loading: tunnelLoading } = useTunnel();

  const shareableLink = tunnelStatus?.url ? tunnelStatus.url : `http://${localIP}`;
  const providerName = tunnelStatus?.provider ? tunnelStatus.provider.toUpperCase() : "LOCAL";

  const form = useForm<SimulationFormValues>({
    resolver: zodResolver(simulationFormSchema),
    mode: "onChange",
    defaultValues: {
      name: simulationData.name,
      startDate: simulationData.start_date,
      endDate: simulationData.end_date,
      startingCash: formatMoney(toCentsString(simulationData.starting_cash)),
      monthlyContribution: formatMoney(toCentsString(simulationData.monthly_contribution)),
      priceImpactEnabled: simulationData.price_impact_enabled,
      priceImpactK: displayDecimal(simulationData.price_impact_k),
      priceImpactDecayDays: String(simulationData.price_impact_decay_days),
      victoryCriterion: simulationData.victory_criterion,
    },
  });

  const { data: coverage } = useQuery(seriesCoverageOptions());
  const [startDate, endDate] = useWatch({ control: form.control, name: ["startDate", "endDate"] });
  const coverageCheck = checkCoverage(coverage ?? [], startDate, endDate);
  const blockedByCoverage = coverageCheck.missingAtStart.length > 0;

  useRealtimeSyncSimulationForm({
    form,
    initial: simulationData,
    isHost,
    debounceMs: 400,
  });

  const { mutate: createSimulation, isPending: loadingCreate } = useApiMutation({
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
    }) => apiFetch<SimulationInfo>("/api/simulation/create", { method: "POST", body }),
    onSuccess: () => toast.success("Simulação criada com sucesso!"),
    onError: (err) => toast.error(err.message),
  });

  const { mutate: continueSimulation, isPending: loadingContinue } = useApiMutation({
    mutationFn: () => apiFetch<SimulationInfo>("/api/simulation/continue", { method: "POST" }),
    onSuccess: () => toast.success("Simulação continuada com sucesso!"),
    onError: (err) => toast.error(err.message),
  });

  const copyHostIP = () => {
    navigator.clipboard.writeText(shareableLink);
    toast.success("Link copiado!");
  };

  const disableSimulationActions = loadingCreate || loadingContinue || !isHost;

  return (
    <div className="flex flex-col gap-3 border-t md:border-l md:border-t-0 border-border pt-6 md:pt-0 md:pl-6">
      <h2 className="text-lg font-semibold">Ações</h2>

      <LobbySettingsDialog
        open={settingsOpen}
        onOpenChange={setSettingsOpen}
        form={form}
        isHost={isHost}
        loading={loadingCreate || loadingContinue}
        coverageCheck={coverageCheck}
      />

      <LoadSimulationDialog open={loadOpen} onOpenChange={setLoadOpen} isHost={isHost} />

      <CoverageAlerts check={coverageCheck} />

      <Button
        type="button"
        className="w-full"
        disabled={disableSimulationActions || blockedByCoverage}
        onClick={() =>
          createSimulation({
            name: form.getValues("name"),
            start_date: form.getValues("startDate"),
            end_date: form.getValues("endDate"),
            starting_cash: normalizeNumberString(form.getValues("startingCash")),
            monthly_contribution: normalizeNumberString(form.getValues("monthlyContribution")),
            price_impact_enabled: form.getValues("priceImpactEnabled"),
            price_impact_k: Number(normalizeNumberString(form.getValues("priceImpactK"))),
            price_impact_decay_days: Number(form.getValues("priceImpactDecayDays")),
            victory_criterion: form.getValues("victoryCriterion"),
          })
        }
      >
        <Play fill="currentColor" />
        Iniciar Nova Simulação
      </Button>

      <Button
        type="button"
        variant="outline"
        className="w-full"
        disabled={disableSimulationActions}
        onClick={() => continueSimulation()}
      >
        <Play fill="currentColor" />
        Continuar Última Simulação
      </Button>

      <Button
        type="button"
        variant="outline"
        className="w-full"
        onClick={() => setLoadOpen(true)}
      >
        <FolderOpen />
        {isHost ? "Carregar Simulação" : "Simulações Salvas"}
      </Button>

      <Button type="button" variant="outline" className="w-full" onClick={() => navigate("/import-assets")}>
        <Database />
        Central de dados
      </Button>

      <Button type="button" variant="outline" className="w-full" onClick={() => navigate("/compare-simulations")}>
        <ArrowLeftRight />
        Comparar Simulações
      </Button>

      <Button type="button" variant="outline" className="w-full" onClick={() => navigate("/correlation")}>
        <Grid3x3 />
        Correlação entre ativos
      </Button>

      <Button type="button" variant="outline" className="w-full" onClick={() => setSettingsOpen(true)}>
        <Settings />
        Configurações
      </Button>

      <div className="mt-auto pt-4 border-t border-border">
        <Label>Link Compartilhável (Via {providerName})</Label>
        <div className="flex mt-1">
          <Input value={shareableLink} readOnly className="rounded-r-none" />
          <Button type="button" variant="secondary" onClick={copyHostIP} className="rounded-l-none">
            <Copy />
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
            <Link />
            {tunnelLoading ? "Gerando..." : "Gerar Link Compartilhável"}
          </Button>
        )}
      </div>
    </div>
  );
}
