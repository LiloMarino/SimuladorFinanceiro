import { useState } from "react";
import { z } from "zod";
import { useForm, useWatch } from "react-hook-form";
import { useQuery } from "@tanstack/react-query";
import { zodResolver } from "@hookform/resolvers/zod";
import { ChevronRight, Clock, Zap } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Spinner } from "@/shared/components/ui/spinner";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { formatMoney } from "@/shared/lib/utils/format";
import { displayDate, displayDecimal, parseLocalDate, toCentsString } from "@/shared/lib/utils/display";
import { normalizeNumberString } from "@/shared/lib/utils";
import { seriesCoverageOptions } from "@/shared/lib/queries/seriesCoverageOptions";
import { simulationListOptions } from "@/shared/lib/queries/simulationListOptions";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SimulationInfo, SimulationSettingsData, VictoryCriterion } from "@/types";
import { useRealtimeSyncSimulationForm } from "../hooks/useRealtimeSyncSimulationForm";
import { checkCoverage } from "../lib/coverage";
import { dateFieldError, isIsoDate } from "../lib/date-field";
import { PRICE_IMPACT_MODE_LABELS, priceImpactModeOf } from "../lib/price-impact";
import { CoverageAlerts } from "./coverage-alerts";
import { RulesSheet } from "./rules-sheet";

// O campo guarda ISO quando a data está completa e real; o texto em digitação é recusado aqui
const dateField = (emptyMessage: string) =>
  z
    .string()
    .min(1, emptyMessage)
    .superRefine((value, ctx) => {
      const message = dateFieldError(value);
      if (message) ctx.addIssue({ code: "custom", message });
    });

const simulationFormSchema = z
  .object({
    name: z.string().min(1, "Dê um nome para a partida"),
    startDate: dateField("Escolha a data de início"),
    endDate: dateField("Escolha a data de fim"),
    startingCash: z
      .string()
      .min(1, "O saldo inicial tem que ser maior que zero")
      .refine((val) => Number(normalizeNumberString(val)) > 0, "O saldo inicial tem que ser maior que zero"),
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
  .refine((data) => !isIsoDate(data.startDate) || !isIsoDate(data.endDate) || data.endDate > data.startDate, {
    message: "Tem que ser depois do início",
    path: ["endDate"],
  });

export type SimulationFormValues = z.infer<typeof simulationFormSchema>;

type LobbyMatchProps = {
  simulationData: SimulationSettingsData;
  isHost: boolean;
  hostNickname: string;
};

/** "Nova partida": as regras resumidas, os avisos de dado e o início da partida. */
export function LobbyMatch({ simulationData, isHost, hostNickname }: LobbyMatchProps) {
  const [rulesOpen, setRulesOpen] = useState(false);

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

  const saveStatus = useRealtimeSyncSimulationForm({ form, initial: simulationData, isHost, debounceMs: 400 });
  const values = useWatch({ control: form.control }) as SimulationFormValues;

  const { data: coverage } = useQuery(seriesCoverageOptions());
  // A cobertura só se confere com as duas datas completas; digitando, o campo mostra o erro
  const datesComplete = isIsoDate(values.startDate) && isIsoDate(values.endDate);
  const coverageCheck = datesComplete
    ? checkCoverage(coverage ?? [], values.startDate, values.endDate)
    : { missingAtStart: [], endingBeforeEnd: [] };
  const blockedByCoverage = coverageCheck.missingAtStart.length > 0;

  // Ativo do exemplo de impacto: PETR4 se existir na base, senão a primeira ação cadastrada
  const stocks = (coverage ?? []).filter((s) => s.kind === "STOCK");
  const exampleTicker = (stocks.find((s) => s.key === "PETR4") ?? stocks[0])?.key;

  // A lista vem da mais recente para a mais antiga: a primeira é a que "Continuar" retoma
  const { data: savedSimulations } = useQuery(simulationListOptions());
  const lastSimulation = savedSimulations?.[0];

  const { mutate: createSimulation, isPending: creating } = useApiMutation({
    mutationFn: () =>
      apiFetch<SimulationInfo>("/api/simulation/create", {
        method: "POST",
        body: {
          name: values.name,
          start_date: values.startDate,
          end_date: values.endDate,
          starting_cash: normalizeNumberString(values.startingCash),
          monthly_contribution: normalizeNumberString(values.monthlyContribution),
          price_impact_enabled: values.priceImpactEnabled,
          price_impact_k: Number(normalizeNumberString(values.priceImpactK)),
          price_impact_decay_days: Number(values.priceImpactDecayDays),
          victory_criterion: values.victoryCriterion,
        },
      }),
    onError: (err) => toastApiError(err),
  });

  const { mutate: continueSimulation, isPending: continuing } = useApiMutation({
    mutationFn: () => apiFetch<SimulationInfo>("/api/simulation/continue", { method: "POST" }),
    onError: (err) => toastApiError(err),
  });

  const impactMode = priceImpactModeOf(values.priceImpactEnabled, values.priceImpactK, values.priceImpactDecayDays);
  const busy = creating || continuing;
  const canStart = isHost && !busy && !blockedByCoverage && form.formState.isValid;

  const rows: { label: string; value: React.ReactNode }[] = [
    { label: "Nome", value: values.name },
    {
      label: "Período",
      value: (
        <span className="font-mono">
          {isIsoDate(values.startDate) ? displayDate(parseLocalDate(values.startDate)) : "—"} →{" "}
          {isIsoDate(values.endDate) ? displayDate(parseLocalDate(values.endDate)) : "—"}
        </span>
      ),
    },
    { label: "Saldo inicial", value: <span className="font-mono">{values.startingCash}</span> },
    { label: "Aporte mensal", value: <span className="font-mono">{values.monthlyContribution}</span> },
    { label: "Vitória por", value: <Badge variant="info">{VICTORY_CRITERIA[values.victoryCriterion]?.label}</Badge> },
    {
      label: "Impacto de preço",
      value: (
        <span className="flex items-center gap-2">
          <Badge variant={impactMode === "OFF" ? "secondary" : "info"}>{PRICE_IMPACT_MODE_LABELS[impactMode]}</Badge>
          {impactMode !== "OFF" && (
            <span className="font-mono text-xs text-muted-foreground">
              k {values.priceImpactK} · T {values.priceImpactDecayDays}
            </span>
          )}
        </span>
      ),
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Nova partida</CardTitle>
        <CardAction>
          <Button variant="outline" size="sm" onClick={() => setRulesOpen(true)}>
            {isHost ? "Editar regras" : "Ver regras"}
          </Button>
        </CardAction>
      </CardHeader>

      <CardContent>
        <div className="flex flex-col gap-3">
          {/* Regras resumidas */}
          <dl>
            {rows.map((row) => (
              <div key={row.label} className="flex items-center justify-between border-t border-muted py-2.5">
                <dt className="text-muted-foreground">{row.label}</dt>
                <dd>{row.value}</dd>
              </div>
            ))}
          </dl>

          <CoverageAlerts
            check={coverageCheck}
            startDate={values.startDate}
            onChangeDate={isHost ? () => setRulesOpen(true) : undefined}
          />

          {/* Início da partida */}
          {isHost ? (
            <>
              <Button size="xl" disabled={!canStart} onClick={() => createSimulation()}>
                {creating ? <Spinner /> : <Zap />}
                Iniciar nova simulação
              </Button>
              {lastSimulation && lastSimulation.status === "PAUSED" && (
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => continueSimulation()}
                  className="flex w-full items-center justify-between rounded-[10px] border border-input bg-card px-3.5 py-3 text-left transition-colors hover:bg-subtle disabled:opacity-50"
                >
                  <span className="grid">
                    <span className="font-semibold">Continuar última simulação</span>
                    <span className="text-xs text-muted-foreground">
                      {lastSimulation.name}
                      {lastSimulation.resume_from &&
                        ` · parou em ${displayDate(parseLocalDate(lastSimulation.resume_from))}`}
                    </span>
                  </span>
                  {continuing ? <Spinner /> : <ChevronRight className="size-4 text-faint-foreground" />}
                </button>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center gap-2 rounded-[10px] bg-background px-4 py-3.5 text-muted-foreground">
              <Clock className="size-4" />
              Esperando {hostNickname} iniciar
            </div>
          )}
        </div>
      </CardContent>

      <RulesSheet
        open={rulesOpen}
        onOpenChange={setRulesOpen}
        form={form}
        isHost={isHost}
        hostNickname={hostNickname}
        coverageCheck={coverageCheck}
        exampleTicker={exampleTicker}
        saveStatus={saveStatus}
      />
    </Card>
  );
}
