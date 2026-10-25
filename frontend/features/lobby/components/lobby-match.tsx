import { useState } from "react";
import { z } from "zod";
import { useForm, useWatch } from "react-hook-form";
import { useQueryClient } from "@tanstack/react-query";
import { zodResolver } from "@hookform/resolvers/zod";
import { Clock, History, Play, RefreshCw, UserPlus, Users, Zap } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { GroupingBadge } from "@/shared/components/grouping-badge";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import { useBacktestStatus } from "@/shared/hooks/queries/useBacktestStatus";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import {
  displayDate,
  displayMoneyCompact,
  displayMoneyWhole,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import { normalizeNumberString } from "@/shared/lib/utils";
import { useSeriesCoverage } from "@/shared/hooks/queries/useSeriesCoverage";
import { useSimulationList } from "@/shared/hooks/queries/useSimulationList";
import {
  displayRatePercent,
  unexpectedLabel,
  UNEXPECTED_OPTIONS,
} from "@/shared/lib/financial-independence";
import { summarizeAssistances } from "@/shared/lib/assistance";
import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { EXPANSIONS } from "@/shared/lib/expansions";
import { GAME_TYPES } from "@/shared/lib/game-types";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type {
  ComputerDifficulty,
  GameType,
  PlayerGrouping,
  RoomPlayer,
  SimulationSettings,
  SimulationSettingsData,
  TeamNaming,
  VictoryCriterion,
} from "@/types";
import { useContinueSimulation } from "../hooks/mutations/useContinueSimulation";
import { useCreateSimulation } from "../hooks/mutations/useCreateSimulation";
import { useDistributeTeams } from "../hooks/mutations/useDistributeTeams";
import { useRealtimeSyncSimulationForm } from "../hooks/useRealtimeSyncSimulationForm";
import { toFormValues, toSettingsBody } from "../lib/simulation-form";
import { checkTeams } from "../lib/teams-check";
import { checkCoverage } from "../lib/coverage";
import {
  calculatedGoal,
  isPositiveMoney,
  isWithdrawalRate,
  WITHDRAWAL_RATE_MESSAGE,
  withdrawalRateFraction,
} from "../lib/life-rules";
import { dateFieldError, isIsoDate } from "@/shared/lib/utils/date-field";
import { PRICE_IMPACT_MODE_LABELS, priceImpactModeOf } from "@/shared/lib/price-impact";
import { COMPUTER_DIFFICULTIES, governmentRuleError } from "../lib/government-rules";
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
    gameType: z.custom<GameType>((value) => typeof value === "string" && value in GAME_TYPES),
    goalNetWorth: z
      .string()
      .min(1, "Informe a meta")
      .refine((val) => Number(normalizeNumberString(val)) > 0, "A meta tem que ser maior que zero"),
    monthlySalary: z
      .string()
      .min(1, "Informe o salário")
      .refine(isPositiveMoney, "O salário tem que ser maior que zero"),
    monthlyExpense: z
      .string()
      .min(1, "Informe a despesa")
      .refine(isPositiveMoney, "A despesa tem que ser maior que zero"),
    unexpectedPerYear: z.number().refine((value) => UNEXPECTED_OPTIONS.some((o) => o.perYear === value)),
    // Percentual ao ano como o jogador digita: "4" é 4%
    withdrawalRate: z
      .string()
      .min(1, "Informe a taxa")
      .refine((val) => isWithdrawalRate(withdrawalRateFraction(val)), WITHDRAWAL_RATE_MESSAGE),
    inflationAdjusted: z.boolean(),
    playerGrouping: z.custom<PlayerGrouping>((value) => value === "INDIVIDUAL" || value === "TEAMS"),
    teamNaming: z.custom<TeamNaming>((value) => value === "COLOR" || value === "NUMBER"),
    showEquivalentRate: z.boolean(),
    showMaturityProjection: z.boolean(),
    showChartHints: z.boolean(),
    governmentEnabled: z.boolean(),
    // ISO quando a data está completa; vazio com a expansão desligada
    firstElection: z.string().superRefine((value, ctx) => {
      const message = dateFieldError(value);
      if (message) ctx.addIssue({ code: "custom", message });
    }),
    computerDifficulty: z.custom<ComputerDifficulty>(
      (value) => value === "EASY" || value === "NORMAL" || value === "HARD",
    ),
  })
  .refine((data) => !isIsoDate(data.startDate) || !isIsoDate(data.endDate) || data.endDate > data.startDate, {
    message: "O fim precisa ser depois do início.",
    path: ["endDate"],
  })
  // A expansão pede 5 anos de partida e a primeira eleição dentro dela
  .superRefine((data, ctx) => {
    if (!data.governmentEnabled) return;
    const error = governmentRuleError({ start: data.startDate, end: data.endDate, firstElection: data.firstElection });
    if (error) ctx.addIssue({ code: "custom", message: error.message, path: [error.path] });
  })
  // A vitória política só existe no modo individual
  .superRefine((data, ctx) => {
    if (data.gameType !== "POLITICAL" || data.playerGrouping !== "TEAMS") return;
    ctx.addIssue({
      code: "custom",
      message: "A vitória política vale só no modo todos contra todos.",
      path: ["playerGrouping"],
    });
  })
  // Na corrida a meta fica acima do que o jogador já tem no primeiro dia
  .superRefine((data, ctx) => {
    if (data.gameType !== "GOAL_RACE") return;
    if (Number(normalizeNumberString(data.goalNetWorth)) > Number(normalizeNumberString(data.startingCash))) return;
    ctx.addIssue({
      code: "custom",
      message: `A meta precisa passar do saldo inicial (${data.startingCash}).`,
      path: ["goalNetWorth"],
    });
  })
  // No viver de renda a meta calculada fica acima do que o jogador já tem no primeiro dia
  .superRefine((data, ctx) => {
    if (data.gameType !== "FINANCIAL_INDEPENDENCE") return;
    const goal = calculatedGoal(data.monthlyExpense, data.withdrawalRate);
    if (goal === null || goal > Number(normalizeNumberString(data.startingCash))) return;
    ctx.addIssue({
      code: "custom",
      message: `A meta calculada (${displayMoneyWhole(goal)}) precisa passar do saldo inicial (${data.startingCash}).`,
      path: ["monthlyExpense"],
    });
  });

export type SimulationFormValues = z.infer<typeof simulationFormSchema>;

const NO_COVERAGE_ISSUES = { missingAtStart: [], endingBeforeEnd: [] };
const IDLE_SAVE_STATUS = { savedAt: null, saving: false, saveError: null };

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
  const canStart = isHost && !busy && !backtestRunning && !blockedByCoverage && form.formState.isValid && !teamsBlock;

  // Com partida selecionada o card mostra as regras dela, em só leitura; sem seleção, as da nova partida
  const rules = selectedSimulation ? toFormValues(selectedSimulation) : values;
  // Painel "Ver regras" da salva: o formulário acompanha as regras gravadas nela, sem edição
  const savedRulesForm = useForm<SimulationFormValues>({
    resolver: zodResolver(simulationFormSchema),
    defaultValues: values,
    values: selectedSimulation ? rules : undefined,
  });
  const loadingSelection = selectedSimulationId !== null && !selectedSimulation && listPending;
  const rulesImpactMode = priceImpactModeOf(rules.priceImpactEnabled, rules.priceImpactK, rules.priceImpactDecayDays);
  const assistances = summarizeAssistances([rules.showEquivalentRate, rules.showMaturityProjection, rules.showChartHints]);

  // A meta com o múltiplo do saldo inicial quando ele é redondo: "R$ 1.000.000,00 · 10× o saldo"
  const startingCashAmount = Number(normalizeNumberString(rules.startingCash));
  const goalMultiple = startingCashAmount > 0 ? Number(normalizeNumberString(rules.goalNetWorth)) / startingCashAmount : NaN;
  const goalSummary = Number.isInteger(goalMultiple)
    ? `${rules.goalNetWorth} · ${goalMultiple}× o saldo`
    : rules.goalNetWorth;

  // O que só existe no tipo escolhido: o critério, a meta fixa ou a vida real
  const independence = rules.gameType === "FINANCIAL_INDEPENDENCE";
  const independenceGoalValue = calculatedGoal(rules.monthlyExpense, rules.withdrawalRate);
  const typeRows: { label: string; value: React.ReactNode }[] = independence
    ? [
        {
          label: "Salário · despesa",
          value: (
            <span className="font-mono">
              {displayMoneyWhole(Number(normalizeNumberString(rules.monthlySalary)))} ·{" "}
              {displayMoneyWhole(Number(normalizeNumberString(rules.monthlyExpense)))}
            </span>
          ),
        },
        {
          label: "Meta",
          value: (
            <span>
              <span className="font-mono">
                {independenceGoalValue === null ? "—" : displayMoneyCompact(independenceGoalValue)}
              </span>{" "}
              · {displayRatePercent(withdrawalRateFraction(rules.withdrawalRate))} ao ano
            </span>
          ),
        },
        {
          label: "Imprevistos",
          value: `${unexpectedLabel(rules.unexpectedPerYear)} · ${rules.unexpectedPerYear} por ano`,
        },
        {
          label: "Inflação",
          value: rules.inflationAdjusted ? "Corrigido pelo IPCA" : "Reais fixos",
        },
      ]
    : rules.gameType === "CLASSIC"
      ? [
          {
            label: "Vitória por",
            value: <Badge variant="info">{VICTORY_CRITERIA[rules.victoryCriterion]?.label}</Badge>,
          },
        ]
      : rules.gameType === "POLITICAL"
        ? [
            {
              label: "Vitória por",
              value: <Badge variant="info">Partido com mais patrimônio</Badge>,
            },
          ]
        : [
            {
              label: "Meta",
              value: <span className="font-mono">{goalSummary}</span>,
            },
          ];

  const rows: { label: string; value: React.ReactNode }[] = [
    // O preset vale para a nova partida; as regras de uma salva não vêm dele
    ...(appliedPreset && !selectedSimulation
      ? [
          {
            label: "Preset",
            value: (
              <span className="flex items-center justify-end gap-1.5">
                <Badge variant="info" className="min-w-0">
                  <span className="truncate">{appliedPreset.name}</span>
                </Badge>
                {appliedPreset.changed.length > 0 && <Badge variant="warning">modificado</Badge>}
              </span>
            ),
          },
        ]
      : []),
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
    ...(independence
      ? []
      : [{ label: "Aporte mensal", value: <span className="font-mono">{rules.monthlyContribution}</span> }]),
    { label: "Modo", value: <GroupingBadge grouping={rules.playerGrouping} /> },
    { label: "Tipo de partida", value: <Badge variant="info">{GAME_TYPES[rules.gameType]?.label}</Badge> },
    ...typeRows,
    {
      label: "Expansões",
      value: rules.governmentEnabled ? (
        <Badge variant="outline">
          <ExpansionEmblem expansion="government" size="xs" />
          {EXPANSIONS.government.label}
        </Badge>
      ) : (
        <span className="text-muted-foreground">—</span>
      ),
    },
    ...(rules.governmentEnabled && isIsoDate(rules.firstElection)
      ? [
          {
            label: "Primeira eleição",
            value: (
              <span>
                <span className="font-mono">{displayDate(parseLocalDate(rules.firstElection))}</span> · computador{" "}
                {COMPUTER_DIFFICULTIES.find((d) => d.value === rules.computerDifficulty)?.label.toLowerCase()}
              </span>
            ),
          },
        ]
      : []),
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
    {
      label: "Assistências",
      value: (
        <Badge variant={assistances.mode === "NORMAL" ? "secondary" : assistances.mode === "EXPERT" ? "inverse" : "info"}>
          {assistances.mode === "NORMAL" && "Normal"}
          {assistances.mode === "EXPERT" && "Especialista"}
          {assistances.mode === "CUSTOM" && `Personalizado · ${assistances.shown} de ${assistances.total} ligadas`}
        </Badge>
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
                  {inTeams && (
                    <>
                      {" "}
                      {newcomers.length === 1 ? "Escolhe" : "Escolhem"} uma equipe antes de entrar. Vale também para
                      quem entra com a partida já rodando: a equipe se escolhe na tela de entrada.
                    </>
                  )}
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
                  <Button size="xl" className="min-w-0" disabled={busy || teamsBlock || backtestRunning} onClick={() => continueSimulation()}>
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
                  <Button size="xl" disabled={!canStart} onClick={() => createSimulation(createSimulationBody)}>
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
