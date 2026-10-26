import { useMemo, useState } from "react";
import { useFieldArray, useForm, useWatch } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { zodResolver } from "@hookform/resolvers/zod";
import { LayoutGrid, List, Play, Plus, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import { Spinner } from "@/shared/components/ui/spinner";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { useBotTickers } from "@/shared/hooks/queries/useBotTickers";
import { addValues, nextFreeColor, type BotFormValues } from "@/shared/lib/bot-form";
import { drawBotName } from "@/shared/lib/bot-names";
import { isIsoDate } from "@/shared/lib/utils/date-field";
import { displayMonthSlashYear } from "@/shared/lib/utils/display";
import type ApiError from "@/shared/lib/models/ApiError";
import type { BacktestSetup, StrategyInfo } from "@/types";
import { useStartBacktest } from "../hooks/mutations/useStartBacktest";
import { backtestSchema, MAX_PARTICIPANTS, toRequest, type BacktestFormValues } from "../lib/form";
import { displayEstimate, displaySpan, weekdaysBetween } from "../lib/period";
import { loadViewPreference, saveViewPreference, type ParticipantsView } from "../lib/view-preference";
import { BacktestBotDialog } from "./backtest-bot-dialog";
import { ParticipantCards } from "./participant-cards";
import { ParticipantList } from "./participant-list";
import { PeriodCard } from "./period-card";
import { ReferenceLegend } from "./reference-legend";

/** A estratégia de referência que o estado vazio sugere: é o que faz quem só compra e espera. */
const REFERENCE_STRATEGY = "buy_and_hold";

type BacktestFormProps = {
  setup: BacktestSetup;
  strategies: StrategyInfo[];
  /** O formulário já resolvido com a configuração de partida */
  values: BacktestFormValues;
  /** Data de início que fixa a faixa dos parâmetros das estratégias */
  startDate: string;
};

/** A tela de novo backtest: período e dinheiro, as estratégias participantes e o botão que roda. */
export function BacktestForm({ setup, strategies, values, startDate }: BacktestFormProps) {
  const navigate = useNavigate();
  const startBacktest = useStartBacktest();
  const { data: tickerOptions } = useBotTickers();
  const [view, setView] = useState<ParticipantsView>(loadViewPreference);
  const [selected, setSelected] = useState(0);
  const [dialog, setDialog] = useState<{ open: boolean; index: number | null }>({ open: false, index: null });

  const schema = useMemo(() => backtestSchema(setup.coverage, strategies), [setup.coverage, strategies]);
  const form = useForm<BacktestFormValues>({ resolver: zodResolver(schema), mode: "onChange", values });
  const participants = useFieldArray({ control: form.control, name: "participants" });
  const watched = useWatch({ control: form.control });
  const list = (watched.participants ?? []) as BotFormValues[];
  const wide = view === "cards";

  const changeView = (next: ParticipantsView) => {
    setView(next);
    saveViewPreference(next);
  };

  // O nome e a cor da estratégia nova saem dos que ainda estão livres
  const addParticipant = (strategyKey?: string) => {
    if (list.length >= MAX_PARTICIPANTS) return;
    participants.append(addValues(strategies, list, strategyKey), { shouldFocus: false });
    setSelected(list.length);
  };

  const duplicate = (index: number) => {
    const source = list[index];
    const strategy = strategies.find((s) => s.key === source?.strategyKey) ?? strategies[0];
    if (!source || !strategy || list.length >= MAX_PARTICIPANTS) return;
    participants.insert(index + 1, {
      ...structuredClone(source),
      nickname: drawBotName(
        strategy,
        list.map((p) => p.nickname),
      ),
      color: nextFreeColor(list),
    });
    setSelected(index + 1);
  };

  const remove = (index: number) => {
    participants.remove(index);
    setSelected((current) => Math.max(Math.min(current, list.length - 2), 0));
  };

  const saveFromDialog = (next: BotFormValues) => {
    if (dialog.index === null) {
      participants.append(next);
      setSelected(list.length);
    } else {
      participants.update(dialog.index, next);
    }
  };

  const request = toRequest(form.getValues(), strategies);
  const submit = form.handleSubmit((formValues) => {
    const body = toRequest(formValues, strategies);
    if (!body) return;
    startBacktest.mutate(body, { onSuccess: () => void navigate("/backtest/running") });
  });

  const { startDate: periodStart = "", endDate: periodEnd = "" } = watched;
  const bothDates = isIsoDate(periodStart) && isIsoDate(periodEnd);
  const tradingDays = bothDates ? weekdaysBetween(periodStart, periodEnd) : 0;
  const errors = form.formState.errors;
  const periodWrong = !!errors.startDate || !!errors.endDate;
  const canRun = form.formState.isValid && list.length > 0 && !!request && !startBacktest.isPending;

  return (
    <form onSubmit={(event) => void submit(event)} className="grid gap-5">
      <div className={wide ? "grid gap-5" : "grid grid-cols-[360px_minmax(0,1fr)] items-start gap-5"}>
        <PeriodCard form={form} coverage={setup.coverage} layout={wide ? "wide" : "side"} />

        {/* Estratégias participantes */}
        <Card>
          <CardHeader>
            <CardTitle>Estratégias participantes</CardTitle>
            <CardDescription>
              {wide
                ? "Editar abre o mesmo diálogo de adicionar bot da sala. Em azul, o parâmetro que mudou do padrão."
                : "Cada uma vira um jogador sem pessoa, com carteira própria. A mesma estratégia pode entrar mais de uma vez."}
            </CardDescription>
            <CardAction>
              <div className="flex items-center gap-3">
                <span className="grid justify-items-end gap-1">
                  <span className="text-xs text-muted-foreground">Ver estratégias como</span>
                  <ToggleGroup
                    variant="segmented"
                    aria-label="Ver estratégias como"
                    value={[view]}
                    onValueChange={(values) => values[0] && changeView(values[0] as ParticipantsView)}
                  >
                    <ToggleGroupItem value="list">
                      <List />
                      Lista
                    </ToggleGroupItem>
                    <ToggleGroupItem value="cards">
                      <LayoutGrid />
                      Cartões
                    </ToggleGroupItem>
                  </ToggleGroup>
                </span>
                <span
                  className={`font-mono text-sm ${list.length >= MAX_PARTICIPANTS ? "font-semibold text-warning" : "text-muted-foreground"}`}
                >
                  {list.length} / {MAX_PARTICIPANTS}
                </span>
              </div>
            </CardAction>
          </CardHeader>

          <CardContent>
            <div className="grid gap-4">
              {list.length === 0 ? (
                <Empty variant="dashed">
                  <EmptyHeader>
                    <EmptyMedia>
                      <Plus />
                    </EmptyMedia>
                    <EmptyTitle>Nenhuma estratégia ainda</EmptyTitle>
                    <EmptyDescription>
                      Adicione pelo menos uma. Para ter com o que comparar, comece por Comprar e segurar: é o que faz
                      quem só compra e espera.
                    </EmptyDescription>
                  </EmptyHeader>
                  <EmptyContent className="flex-row justify-center">
                    <Button
                      type="button"
                      size="sm"
                      onClick={() => (wide ? setDialog({ open: true, index: null }) : addParticipant())}
                    >
                      <Plus />
                      Adicionar estratégia
                    </Button>
                    {strategies.some((s) => s.key === REFERENCE_STRATEGY) && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => addParticipant(REFERENCE_STRATEGY)}
                      >
                        Adicionar Comprar e segurar
                      </Button>
                    )}
                  </EmptyContent>
                </Empty>
              ) : wide ? (
                <ParticipantCards
                  participants={list}
                  strategies={strategies}
                  onAdd={() => setDialog({ open: true, index: null })}
                  onEdit={(index) => setDialog({ open: true, index })}
                  onDuplicate={duplicate}
                  onRemove={remove}
                />
              ) : (
                <ParticipantList
                  form={form}
                  strategies={strategies}
                  tickerOptions={tickerOptions ?? []}
                  selected={Math.min(selected, list.length - 1)}
                  onSelect={setSelected}
                  onAdd={() => addParticipant()}
                  onDuplicate={duplicate}
                  onRemove={remove}
                />
              )}
              {wide && <ReferenceLegend compact />}
            </div>
          </CardContent>
        </Card>
      </div>

      {startBacktest.error && <StartError error={startBacktest.error} onRetry={() => void submit()} />}

      {/* Rodapé */}
      <div className="flex items-center justify-between gap-4 rounded-xl bg-sidebar px-5 py-4 text-sidebar-foreground">
        <div className="grid gap-0.5 text-sm">
          {list.length === 0 ? (
            <span>Falta pelo menos 1 estratégia</span>
          ) : periodWrong || !bothDates ? (
            <span>Corrija o período</span>
          ) : (
            <>
              <span>
                <b className="text-white">
                  {list.length} {list.length === 1 ? "estratégia" : "estratégias"}
                </b>{" "}
                · {displaySpan(periodStart, periodEnd)}, de {displayMonthSlashYear(periodStart)} a{" "}
                {displayMonthSlashYear(periodEnd)} · CDI e Ibovespa de referência
              </span>
              <span className="text-xs opacity-70">
                Roda sem esperar: {displayEstimate(tradingDays, list.length)}. A sala espera enquanto isso.
              </span>
            </>
          )}
        </div>
        <Button type="submit" size="lg" disabled={!canRun}>
          {startBacktest.isPending ? <Spinner /> : <Play />}
          Rodar backtest
        </Button>
      </div>

      <BacktestBotDialog
        key={`${dialog.open}-${dialog.index}`}
        open={dialog.open}
        onOpenChange={(open) => setDialog((current) => ({ ...current, open }))}
        participant={dialog.index === null ? undefined : list[dialog.index]}
        others={list.filter((_, index) => index !== dialog.index)}
        startDate={startDate}
        startingCash={watched.startingCash ?? values.startingCash}
        onSubmit={saveFromDialog}
      />
    </form>
  );
}

type StartErrorProps = {
  error: ApiError;
  onRetry: () => void;
};

/** O servidor recusou ou não respondeu: a configuração continua na tela. */
function StartError({ error, onRetry }: StartErrorProps) {
  return (
    <Alert variant="destructive">
      <TriangleAlert />
      <AlertTitle>Não deu para começar o backtest</AlertTitle>
      <AlertDescription>
        {error.message} Nada foi salvo e a configuração continua aqui.
        <div className="mt-2">
          <Button type="button" size="sm" onClick={onRetry}>
            Tentar de novo
          </Button>
        </div>
      </AlertDescription>
    </Alert>
  );
}
