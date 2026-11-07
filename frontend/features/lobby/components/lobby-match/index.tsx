import { useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { useQueryClient } from "@tanstack/react-query";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import { useBacktestStatus } from "@/shared/hooks/queries/useBacktestStatus";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useSeriesCoverage } from "@/shared/hooks/queries/useSeriesCoverage";
import { useSimulationList } from "@/shared/hooks/queries/useSimulationList";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import { isIsoDate } from "@/shared/lib/utils/date-field";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { RoomPlayer, SimulationSettings, SimulationSettingsData } from "@/types";
import { useRunningChallenge } from "@/features/lobby/candle-challenge/hooks/queries/useRunningChallenge";
import { useContinueSimulation } from "../../hooks/mutations/useContinueSimulation";
import { useCreateSimulation } from "../../hooks/mutations/useCreateSimulation";
import { useDistributeTeams } from "../../hooks/mutations/useDistributeTeams";
import { usePreparations } from "../../hooks/queries/usePreparations";
import { useRealtimeSyncSimulationForm } from "../../hooks/useRealtimeSyncSimulationForm";
import { checkCoverage } from "../../lib/coverage";
import {
  simulationFormSchema,
  toFormValues,
  toSettingsBody,
  type SimulationFormValues,
} from "../../lib/simulation-form";
import { checkTeams } from "../../lib/teams-check";
import { CoverageAlerts } from "../coverage-alerts";
import { RoomPreparationSummary } from "../preparation/room-preparation";
import { RulesSheet } from "../rules-sheet";
import { NewcomersAlert } from "./newcomers-alert";
import { ContinueActions, NewGameActions, WaitingForHost } from "./start-actions";
import { summaryRows } from "./summary-rows";
import { TeamsBlock } from "./teams-block";

const NO_COVERAGE_ISSUES = { missingAtStart: [], endingBeforeEnd: [] };
const IDLE_SAVE_STATUS = {
  savedAt: null,
  saving: false,
  restoring: false,
  saveError: null,
  rejectedAssistances: false,
  retryAssistances: () => undefined,
};

type LobbyMatchProps = {
  simulationData: SimulationSettingsData;
  /** O preset de onde vieram as regras da nova partida; nulo quando foram montadas à mão */
  appliedPreset: SimulationSettings["applied_preset"];
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
  appliedPreset,
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
    defaultValues: toFormValues(simulationData),
  });

  const saveStatus = useRealtimeSyncSimulationForm({
    form,
    initial: simulationData,
    isHost,
    locked: selectedSimulationId !== null,
    debounceMs: 400,
  });
  const values = useWatch({ control: form.control }) as SimulationFormValues;

  const { data: coverage } = useSeriesCoverage();
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
  const { data: savedSimulations, isPending: listPending } = useSimulationList();
  // Quem entra ou sai da sala muda quais partidas salvas ainda cabem; uma partida excluída sai da lista
  const refreshFit = () => void queryClient.invalidateQueries({ queryKey: queryKeys.simulationList() });
  useRealtime("player_join", refreshFit);
  useRealtime("player_exit", refreshFit);
  useRealtime("simulation_deleted", refreshFit);
  const selectedSimulation = savedSimulations?.find((s) => s.id === selectedSimulationId);

  // Na sala e sem ter jogado a partida selecionada: entra ao continuar, com o saldo inicial
  const { data: roomPlayers } = useRoomPlayers();
  const newcomers = selectedSimulation
    ? (roomPlayers ?? []).filter((p) => !savedPlayers.some((saved) => saved.nickname === p.nickname))
    : [];

  const createSimulationBody = toSettingsBody(values);
  const { mutate: createSimulation, isPending: creating } = useCreateSimulation();
  const { mutate: continueSimulation, isPending: continuing } = useContinueSimulation();

  const { mutate: distributeTeams, isPending: distributing } = useDistributeTeams();

  // Uma partida por vez: com backtest rodando o servidor recusa iniciar ou continuar
  const { data: backtest } = useBacktestStatus();
  const backtestRunning = !!backtest?.progress;
  const busy = creating || continuing;
  // Em equipes todo mundo precisa estar numa e a partida, ter pelo menos duas
  const inTeams = (selectedSimulation?.player_grouping ?? values.playerGrouping) === "TEAMS";
  const teams = checkTeams(roomPlayers ?? [], savedPlayers, selectedSimulation?.team_naming ?? values.teamNaming);
  const teamsBlock = inTeams && !teams.ready;
  // Iniciar a partida encerra o desafio da vela que estiver rolando; o host é avisado antes
  const challengeQuestion = useRunningChallenge();
  // Partidos preparados que repetem sigla, nome ou cor bloqueiam o início, como as equipes
  const { data: preparations } = usePreparations();
  const preparationBlock = (preparations?.conflicts.length ?? 0) > 0;
  const pendingInvites = preparations?.pending_invites ?? 0;
  const canStart =
    isHost &&
    !busy &&
    !backtestRunning &&
    !blockedByCoverage &&
    form.formState.isValid &&
    !teamsBlock &&
    !preparationBlock;

  // Com partida selecionada o card mostra as regras dela, em só leitura; sem seleção, as da nova partida
  const rules = selectedSimulation ? toFormValues(selectedSimulation) : values;
  // Painel "Ver regras" da salva: o formulário acompanha as regras gravadas nela, sem edição
  const savedRulesForm = useForm<SimulationFormValues>({
    resolver: zodResolver(simulationFormSchema),
    defaultValues: values,
    ...(selectedSimulation ? { values: rules } : {}),
  });
  const loadingSelection = selectedSimulationId !== null && !selectedSimulation && listPending;

  // O preset vale para a nova partida; as regras de uma salva não vêm dele
  const rows = summaryRows(rules, selectedSimulation ? null : appliedPreset);

  return (
    <Card>
      <CardHeader>
        <div className="grid gap-1">
          <CardTitle>
            {selectedSimulation
              ? `Continuar · ${selectedSimulation.name}`
              : loadingSelection
                ? "Continuar partida"
                : "Nova partida"}
          </CardTitle>
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
              <NewcomersAlert newcomers={newcomers} inTeams={inTeams} startingCash={rules.startingCash} />
            )}

            {/* Preparação da sala */}
            {isHost && rules.governmentEnabled && !selectedSimulation && preparations && (
              <RoomPreparationSummary preparations={preparations} />
            )}

            {/* Equipes: o que falta para iniciar e o atalho do host */}
            {inTeams && teamsBlock && (
              <TeamsBlock
                teams={teams}
                isHost={isHost}
                distributing={distributing}
                onDistribute={() => distributeTeams()}
              />
            )}

            {/* Início da partida */}
            {isHost ? (
              selectedSimulation ? (
                <ContinueActions
                  simulationName={selectedSimulation.name}
                  challengeQuestion={challengeQuestion}
                  continuing={continuing}
                  busy={busy}
                  disabled={busy || teamsBlock || backtestRunning}
                  onContinue={() => continueSimulation()}
                  onOpenSaved={onOpenSaved}
                />
              ) : (
                <NewGameActions
                  challengeQuestion={challengeQuestion}
                  creating={creating}
                  busy={busy}
                  canStart={canStart}
                  pendingInvites={rules.governmentEnabled ? pendingInvites : 0}
                  hasSavedSimulations={!!savedSimulations && savedSimulations.length > 0}
                  onCreate={() => createSimulation(createSimulationBody)}
                  onOpenSaved={onOpenSaved}
                />
              )
            ) : (
              <WaitingForHost hostNickname={hostNickname} simulationName={selectedSimulation?.name} />
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
        onRestoreDefaults={() => void saveStatus.restoreDefaults()}
        appliedPreset={appliedPreset}
        onPresetLoaded={(settings) => void saveStatus.applyServerSettings(settings)}
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
        appliedPreset={null}
        onPresetLoaded={() => undefined}
      />
    </Card>
  );
}
