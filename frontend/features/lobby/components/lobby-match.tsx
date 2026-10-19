import { useState } from "react";
import { z } from "zod";
import { useForm, useWatch } from "react-hook-form";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { zodResolver } from "@hookform/resolvers/zod";
import { Clock, History, Play, RefreshCw, UserPlus, Users, Zap } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { GroupingBadge } from "@/shared/components/grouping-badge";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { formatMoney } from "@/shared/lib/utils/format";
import { displayDate, displayDecimal, parseLocalDate, toCentsString } from "@/shared/lib/utils/display";
import { normalizeNumberString } from "@/shared/lib/utils";
import { seriesCoverageOptions } from "@/shared/lib/queries/seriesCoverageOptions";
import { simulationListOptions } from "@/shared/lib/queries/simulationListOptions";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type {
  PlayerGrouping,
  RoomPlayer,
  SimulationInfo,
  SimulationSettingsData,
  TeamNaming,
  VictoryCriterion,
} from "@/types";
import { useDistributeTeams } from "../hooks/useDistributeTeams";
import { useRealtimeSyncSimulationForm } from "../hooks/useRealtimeSyncSimulationForm";
import { checkTeams } from "../lib/teams-check";
import { checkCoverage } from "../lib/coverage";
import { dateFieldError, isIsoDate } from "../lib/date-field";
import { PRICE_IMPACT_MODE_LABELS, priceImpactModeOf } from "../lib/price-impact";
import { CoverageAlerts } from "./coverage-alerts";
import { joinNames } from "../lib/join-names";
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
    playerGrouping: z.custom<PlayerGrouping>((value) => value === "INDIVIDUAL" || value === "TEAMS"),
    teamNaming: z.custom<TeamNaming>((value) => value === "COLOR" || value === "NUMBER"),
  })
  .refine((data) => !isIsoDate(data.startDate) || !isIsoDate(data.endDate) || data.endDate > data.startDate, {
    message: "Tem que ser depois do início",
    path: ["endDate"],
  });

export type SimulationFormValues = z.infer<typeof simulationFormSchema>;

const NO_COVERAGE_ISSUES = { missingAtStart: [], endingBeforeEnd: [] };
const IDLE_SAVE_STATUS = { savedAt: null, saving: false, saveError: null };

type LobbyMatchProps = {
  simulationData: SimulationSettingsData;
  isHost: boolean;
  hostNickname: string;
  /** Partida salva que o host selecionou para continuar; nula quando a partida é nova */
  selectedSimulationId: number | null;
  /** Quem jogou a partida selecionada, com a cor guardada */
  savedPlayers: RoomPlayer[];
  onOpenSaved: () => void;
};

/** "Nova partida": as regras resumidas, os avisos de dado e o início da partida. */
export function LobbyMatch({
  simulationData,
  isHost,
  hostNickname,
  selectedSimulationId,
  savedPlayers,
  onOpenSaved,
}: LobbyMatchProps) {
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
      playerGrouping: simulationData.player_grouping,
      teamNaming: simulationData.team_naming,
    },
  });

  const saveStatus = useRealtimeSyncSimulationForm({
    form,
    initial: simulationData,
    isHost,
    locked: selectedSimulationId !== null,
    debounceMs: 400,
  });
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

  // A lista vem da mais recente para a mais antiga: a primeira é a que o atalho seleciona
  const queryClient = useQueryClient();
  const { data: savedSimulations, isPending: listPending } = useQuery(simulationListOptions());
  // Quem entra ou sai da sala muda quais partidas salvas ainda cabem
  const refreshFit = () => void queryClient.invalidateQueries({ queryKey: queryKeys.simulationList() });
  useRealtime("player_join", refreshFit);
  useRealtime("player_exit", refreshFit);
  const selectedSimulation = savedSimulations?.find((s) => s.id === selectedSimulationId);

  // Na sala e sem ter jogado a partida selecionada: entra ao continuar, com o saldo inicial
  const { data: roomPlayers } = useRoomPlayers();
  const newcomers = selectedSimulation
    ? (roomPlayers ?? []).filter((p) => !savedPlayers.some((saved) => saved.nickname === p.nickname))
    : [];

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
          player_grouping: values.playerGrouping,
          team_naming: values.teamNaming,
        },
      }),
    onError: (err) => toastApiError(err),
  });

  const { mutate: continueSimulation, isPending: continuing } = useApiMutation({
    mutationFn: () => apiFetch<SimulationInfo>("/api/simulation/continue", { method: "POST" }),
    onError: (err) => toastApiError(err),
  });

  const { mutate: distributeTeams, isPending: distributing } = useDistributeTeams();

  const busy = creating || continuing;
  // Em equipes todo mundo precisa estar numa e a partida, ter pelo menos duas
  const inTeams = (selectedSimulation?.player_grouping ?? values.playerGrouping) === "TEAMS";
  const teams = checkTeams(roomPlayers ?? [], savedPlayers, selectedSimulation?.team_naming ?? values.teamNaming);
  const teamsBlock = inTeams && !teams.ready;
  const canStart = isHost && !busy && !blockedByCoverage && form.formState.isValid && !teamsBlock;

  // Com partida selecionada o card mostra as regras dela, em só leitura; sem seleção, as da nova partida
  const rules = selectedSimulation
    ? {
        name: selectedSimulation.name,
        startDate: selectedSimulation.start_date,
        endDate: selectedSimulation.end_date,
        startingCash: formatMoney(toCentsString(selectedSimulation.starting_cash)),
        monthlyContribution: formatMoney(toCentsString(selectedSimulation.monthly_contribution)),
        victoryCriterion: selectedSimulation.victory_criterion,
        priceImpactEnabled: selectedSimulation.price_impact_enabled,
        priceImpactK: displayDecimal(selectedSimulation.price_impact_k),
        priceImpactDecayDays: String(selectedSimulation.price_impact_decay_days),
        playerGrouping: selectedSimulation.player_grouping,
        teamNaming: selectedSimulation.team_naming,
      }
    : values;
  // Painel "Ver regras" da salva: o formulário acompanha as regras gravadas nela, sem edição
  const savedRulesForm = useForm<SimulationFormValues>({
    resolver: zodResolver(simulationFormSchema),
    defaultValues: values,
    values: selectedSimulation ? rules : undefined,
  });
  const loadingSelection = selectedSimulationId !== null && !selectedSimulation && listPending;
  const rulesImpactMode = priceImpactModeOf(rules.priceImpactEnabled, rules.priceImpactK, rules.priceImpactDecayDays);

  const rows: { label: string; value: React.ReactNode }[] = [
    { label: "Nome", value: rules.name },
    {
      label: "Período",
      value: (
        <span className="font-mono">
          {isIsoDate(rules.startDate) ? displayDate(parseLocalDate(rules.startDate)) : "—"} →{" "}
          {isIsoDate(rules.endDate) ? displayDate(parseLocalDate(rules.endDate)) : "—"}
        </span>
      ),
    },
    { label: "Saldo inicial", value: <span className="font-mono">{rules.startingCash}</span> },
    { label: "Aporte mensal", value: <span className="font-mono">{rules.monthlyContribution}</span> },
    { label: "Modo", value: <GroupingBadge grouping={rules.playerGrouping} /> },
    { label: "Vitória por", value: <Badge variant="info">{VICTORY_CRITERIA[rules.victoryCriterion]?.label}</Badge> },
    {
      label: "Impacto de preço",
      value: (
        <span className="flex items-center gap-2">
          <Badge variant={rulesImpactMode === "OFF" ? "secondary" : "info"}>{PRICE_IMPACT_MODE_LABELS[rulesImpactMode]}</Badge>
          {rulesImpactMode !== "OFF" && (
            <span className="font-mono text-xs text-muted-foreground">
              k {rules.priceImpactK} · T {rules.priceImpactDecayDays}
            </span>
          )}
        </span>
      ),
    },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="grid gap-1">
          <CardTitle>{selectedSimulation || loadingSelection ? "Continuar partida" : "Nova partida"}</CardTitle>
          {(selectedSimulation || !loadingSelection) && (
            <CardDescription>
              {selectedSimulation?.resume_from
                ? `Parou em ${displayDate(parseLocalDate(selectedSimulation.resume_from))}`
                : "Ainda não começou"}
            </CardDescription>
          )}
        </div>
        {!loadingSelection && (
          <CardAction>
            <Button variant="outline" size="sm" onClick={() => setRulesOpen(true)}>
              {isHost && !selectedSimulation ? "Editar regras" : "Ver regras"}
            </Button>
          </CardAction>
        )}
      </CardHeader>

      <CardContent>
        {loadingSelection ? (
          <div className="flex flex-col gap-3">
            {/* Esqueleto das regras enquanto a seleção é aplicada */}
            <div>
              {rows.map((row) => (
                <div key={row.label} className="flex items-center justify-between border-t border-muted py-3">
                  <Skeleton className="h-3.5 w-[90px]" />
                  <Skeleton className="h-3.5 w-[140px]" />
                </div>
              ))}
            </div>
            {isHost && (
              <Button size="xl" disabled>
                <Spinner />
                Selecionando…
              </Button>
            )}
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {/* Regras resumidas */}
            <dl>
              {rows.map((row) => (
                <div key={row.label} className="flex items-center justify-between border-t border-muted py-2.5">
                  <dt className="shrink-0 text-muted-foreground">{row.label}</dt>
                  <dd className="min-w-0 truncate pl-3">{row.value}</dd>
                </div>
              ))}
            </dl>

            {!selectedSimulation && (
              <CoverageAlerts
                check={coverageCheck}
                startDate={values.startDate}
                onChangeDate={isHost ? () => setRulesOpen(true) : undefined}
              />
            )}

            {/* Quem nunca jogou a partida selecionada entra ao continuar */}
            {selectedSimulation && newcomers.length > 0 && (
              <Alert variant="info">
                <UserPlus />
                <AlertTitle>
                  {joinNames(newcomers.map((p) => p.nickname))} nunca {newcomers.length === 1 ? "jogou" : "jogaram"}{" "}
                  esta partida
                </AlertTitle>
                <AlertDescription>
                  {newcomers.length === 1 ? "Entra" : "Entram"} agora, com o saldo inicial de {rules.startingCash} e a
                  cor{inTeams && " e a equipe"} que {newcomers.length === 1 ? "escolheu" : "escolheram"}.
                </AlertDescription>
              </Alert>
            )}

            {/* Equipes: o que falta para iniciar e o atalho do host */}
            {inTeams && teamsBlock && (
              <div className="grid gap-2">
                <span className="text-[13px] text-muted-foreground">
                  {teams.missing.length > 0
                    ? "Para iniciar, todo mundo precisa estar numa equipe"
                    : "Todos na mesma equipe: não dá pra iniciar"}
                </span>
                {isHost && teams.missing.length > 0 && (
                  <Button variant="outline" disabled={distributing} onClick={() => distributeTeams()}>
                    {distributing ? <Spinner /> : <Users />}
                    Distribuir quem falta
                  </Button>
                )}
              </div>
            )}

            {/* Início da partida */}
            {isHost ? (
              selectedSimulation ? (
                <div className="grid gap-2">
                  <Button size="xl" className="min-w-0" disabled={busy || teamsBlock} onClick={() => continueSimulation()}>
                    {continuing ? <Spinner /> : <Play />}
                    <span className="min-w-0 truncate">Continuar {selectedSimulation.name}</span>
                  </Button>
                  <Button variant="outline" disabled={busy} onClick={onOpenSaved}>
                    <RefreshCw />
                    Trocar partida
                  </Button>
                </div>
              ) : (
                <>
                  <Button size="xl" disabled={!canStart} onClick={() => createSimulation()}>
                    {creating ? <Spinner /> : <Zap />}
                    Iniciar nova simulação
                  </Button>
                  {/* Sem partida salva não há o que escolher */}
                  {savedSimulations && savedSimulations.length > 0 && (
                    <Button variant="outline" disabled={busy} onClick={onOpenSaved}>
                      <History />
                      Escolher partida salva
                    </Button>
                  )}
                </>
              )
            ) : (
              <div className="flex items-center justify-center gap-2 rounded-[10px] bg-background px-4 py-3.5 text-muted-foreground">
                <Clock className="size-4" />
                {selectedSimulation
                  ? `Esperando ${hostNickname} continuar ${selectedSimulation.name}`
                  : `Esperando ${hostNickname} iniciar`}
              </div>
            )}
          </div>
        )}
      </CardContent>

      <RulesSheet
        open={rulesOpen && !selectedSimulation}
        onOpenChange={setRulesOpen}
        form={form}
        isHost={isHost}
        hostNickname={hostNickname}
        coverageCheck={coverageCheck}
        exampleTicker={exampleTicker}
        saveStatus={saveStatus}
      />
      {/* Regras da partida salva: as gravadas nela, só leitura */}
      <RulesSheet
        open={rulesOpen && !!selectedSimulation}
        onOpenChange={setRulesOpen}
        form={savedRulesForm}
        isHost={isHost}
        locked
        hostNickname={hostNickname}
        coverageCheck={NO_COVERAGE_ISSUES}
        exampleTicker={exampleTicker}
        saveStatus={IDLE_SAVE_STATUS}
      />
    </Card>
  );
}
