import { useEffect, useRef, useState } from "react";
import { Bot, CircleCheck } from "lucide-react";
import { toast } from "sonner";
import { ErrorState } from "@/shared/components/error-state";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import { usePresidencyFreeze } from "@/shared/hooks/usePresidencyFreeze";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useStrategyRoute } from "@/shared/hooks/useStrategyRoute";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { useMyStrategy } from "@/shared/hooks/queries/useMyStrategy";
import { useSavedStrategyParams } from "@/shared/hooks/queries/useSavedStrategyParams";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { useVariableIncomeStocks } from "@/shared/hooks/queries/useVariableIncomeStocks";
import type { BotTicker, FundAccount, MyStrategy, SavedStrategyParams, StrategyInfo } from "@/types";
import { AccountHeader } from "../components/account-header";
import { ConfirmDialog, type ModeChange } from "../components/confirm-dialog";
import { ErrorBanner } from "../components/error-banner";
import { ModeCard, type Mode } from "../components/mode-card";
import { StrategiesSkeleton } from "../components/strategies-skeleton";
import { StrategyDetail } from "../components/strategy-detail";
import { StrategyList } from "@/shared/components/strategy-list";
import { StrategyLog } from "../components/strategy-log";
import { useMarkStrategyErrorSeen } from "../hooks/mutations/useMarkStrategyErrorSeen";
import { useSetMyStrategy } from "@/shared/hooks/mutations/useSetMyStrategy";
import { useStrategies } from "@/shared/hooks/queries/useStrategies";
import { fromDraft, profileValues, toDraft, type ParamDraft, type ParamValues } from "@/shared/lib/strategy-params";

export default function StrategiesPage() {
  usePageLabel("Estratégias");
  const route = useStrategyRoute();
  const { active, accountKey, switchAccount } = useActiveAccount();

  // A conta do topo só se conhece com a lista de contas na mão
  if (route.kind === "pending") return <StrategiesSkeleton />;

  // O Fundo Soberano investe pelas decisões do governo: não há estratégia para ligar nele
  if (route.kind === "sovereign") {
    return (
      <Card>
        <CardContent>
          <Empty variant="dashed">
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <Bot />
              </EmptyMedia>
              <EmptyTitle>O Fundo Soberano não tem automático</EmptyTitle>
              <EmptyDescription>
                Ele investe pelas decisões do governo. Para ligar uma estratégia, volte à sua carteira pessoal ou
                escolha uma gestora que você gere.
              </EmptyDescription>
            </EmptyHeader>
            <EmptyContent className="flex-row justify-center">
              <Button variant="outline" onClick={() => switchAccount(null)}>
                Usar minha carteira
              </Button>
            </EmptyContent>
          </Empty>
        </CardContent>
      </Card>
    );
  }

  // Cada conta tem a sua área de trabalho: rascunhos e estratégia escolhida não passam de uma conta para outra
  return <StrategiesLoader key={accountKey} account={active} fund={route.kind === "fund" ? (active ?? null) : null} />;
}

type LoaderProps = {
  /** A conta no topo; indefinida quando só existe a pessoal */
  account: FundAccount | undefined;
  /** A gestora que o automático opera; nulo na conta pessoal */
  fund: FundAccount | null;
};

function StrategiesLoader({ account, fund }: LoaderProps) {
  const strategies = useStrategies({ fund: fund !== null });
  const mine = useMyStrategy({ activeAccount: true });
  const saved = useSavedStrategyParams();
  const quotes = useVariableIncomeStocks();
  const portfolio = usePortfolio({ activeAccount: true });

  if (!strategies.data || !mine.data || !saved.data || !quotes.data || !portfolio.data) {
    const error = strategies.error ?? mine.error ?? saved.error ?? quotes.error ?? portfolio.error;
    return error ? (
      <Card>
        <CardContent>
          <ErrorState
            title="Não deu para carregar as estratégias"
            description="O servidor não respondeu. Se a sua estiver ligada, ela continua operando."
            error={error}
            onRetry={() => {
              void strategies.refetch();
              void mine.refetch();
              void saved.refetch();
              void quotes.refetch();
              void portfolio.refetch();
            }}
          />
        </CardContent>
      </Card>
    ) : (
      <StrategiesSkeleton />
    );
  }

  return (
    <StrategiesWorkspace
      account={account}
      fund={fund}
      strategies={strategies.data}
      mine={mine.data}
      saved={saved.data}
      tickerOptions={quotes.data.map(({ ticker, name }) => ({ ticker, name }))}
      heldTickers={portfolio.data.variable_income.map((position) => position.ticker)}
      cash={portfolio.data.cash}
    />
  );
}

type WorkspaceProps = {
  account: FundAccount | undefined;
  fund: FundAccount | null;
  strategies: StrategyInfo[];
  mine: MyStrategy;
  saved: SavedStrategyParams;
  /** As ações da partida: as opções do "Escolher" e o filtro das ações salvas no perfil */
  tickerOptions: BotTicker[];
  /** As ações da carteira da conta, para o atalho "Só as da carteira" */
  heldTickers: string[];
  /** O caixa da conta, em reais */
  cash: string;
};

function StrategiesWorkspace({
  account,
  fund,
  strategies,
  mine,
  saved,
  tickerOptions,
  heldTickers,
  cash,
}: WorkspaceProps) {
  const { data: state } = useSimulationState();
  const mandateEnd = usePresidencyFreeze();
  const setStrategy = useSetMyStrategy();
  const { mutate: markErrorSeen } = useMarkStrategyErrorSeen();

  const [pickedKey, setPickedKey] = useState<string | null>(null);
  const [drafts, setDrafts] = useState<Record<string, ParamDraft>>({});
  const [change, setChange] = useState<ModeChange | null>(null);
  const detailRef = useRef<HTMLDivElement>(null);

  // A escolhida abre primeiro na ligada, depois na que deu erro, depois na primeira da lista
  const errorKey = mine.error?.strategy_key ?? undefined;
  const selected =
    strategies.find((strategy) => strategy.key === (pickedKey ?? mine.active?.key ?? errorKey)) ?? strategies[0];
  const activeStrategy = strategies.find((strategy) => strategy.key === mine.active?.key);

  // O erro visto e o ponto vermelho do menu são da conta pessoal
  const errorUnseen = fund === null && !!mine.error && !mine.error.seen;
  // Abrir a página é ver o erro: o ponto vermelho do menu sai
  useEffect(() => {
    if (errorUnseen) markErrorSeen();
  }, [errorUnseen, markErrorSeen]);

  if (!selected) return null;

  // Sem rascunho, a estratégia abre nos parâmetros com que está ligada ou, desligada, nos salvos no perfil
  const initialValues = (strategy: StrategyInfo) =>
    mine.active?.key === strategy.key
      ? { values: mine.active.params, missing: [] }
      : profileValues(strategy, saved[strategy.key], tickerOptions);

  const activeHere = mine.active?.key === selected.key ? mine.active : null;
  const initial = initialValues(selected);
  const draft = drafts[selected.key] ?? toDraft(initial.values);

  const clearDraft = (key: string) =>
    setDrafts((current) => Object.fromEntries(Object.entries(current).filter(([draftKey]) => draftKey !== key)));

  // Valores do rascunho da estratégia; nulo enquanto algum campo não é um número inteiro
  const valuesOf = (strategy: StrategyInfo): ParamValues | null =>
    fromDraft(strategy.params, drafts[strategy.key] ?? toDraft(initialValues(strategy).values));

  const requestTurnOn = (strategy: StrategyInfo, params: ParamValues) =>
    setChange({ kind: mine.active ? "switch" : "turn-on", key: strategy.key, params });

  const changeMode = (mode: Mode) => {
    if (mode === "manual") return setChange({ kind: "manual" });
    const values = valuesOf(selected);
    if (!values) {
      toast.error("Corrija os parâmetros antes de ligar.");
      return;
    }
    requestTurnOn(selected, values);
  };

  const confirm = (pending: ModeChange) => {
    const body = pending.kind === "manual" ? { key: null, params: {} } : { key: pending.key, params: pending.params };
    setStrategy.mutate(body, {
      onSuccess: () => {
        setChange(null);
        if (pending.kind !== "manual") clearDraft(pending.key);
      },
    });
  };

  const errorStrategy = strategies.find((strategy) => strategy.key === errorKey);
  const editErrorParams = () => {
    setPickedKey(errorKey ?? null);
    detailRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };
  const turnOnAgain = () => {
    if (!errorStrategy) return;
    const values = valuesOf(errorStrategy);
    if (!values) {
      toast.error("Corrija os parâmetros antes de ligar.");
      return;
    }
    setPickedKey(errorStrategy.key);
    requestTurnOn(errorStrategy, values);
  };

  return (
    <div className="grid gap-5">
      {account && <AccountHeader fund={fund} />}

      {mine.error && (
        <ErrorBanner
          error={mine.error}
          canRetry={!!errorStrategy}
          onEditParams={editErrorParams}
          onTurnOnAgain={turnOnAgain}
        />
      )}

      {mine.resumed && activeStrategy && (
        <Alert variant="info">
          <CircleCheck />
          <AlertTitle>Partida retomada com o automático ligado</AlertTitle>
          <AlertDescription>
            {activeStrategy.name} voltou com os mesmos parâmetros e relê o histórico do mercado.
          </AlertDescription>
        </Alert>
      )}

      <ModeCard
        mine={mine}
        activeStrategy={activeStrategy}
        currentDate={state?.current_date}
        fund={fund}
        mandateEnd={mandateEnd}
        onModeChange={changeMode}
      />

      {/* Estratégias e o detalhe da escolhida */}
      <div className="grid items-start gap-5 xl:grid-cols-[340px_minmax(0,1fr)]">
        <Card size="sm">
          <CardContent>
            <StrategyList
              strategies={strategies}
              selectedKey={selected.key}
              activeKey={mine.active?.key}
              onSelect={setPickedKey}
            />
          </CardContent>
        </Card>
        <div ref={detailRef} className="min-w-0 scroll-mt-4">
          <StrategyDetail
            key={selected.key}
            strategy={selected}
            active={activeHere}
            draft={draft}
            missingTickers={drafts[selected.key] ? [] : initial.missing}
            cash={cash}
            {...(fund && { cashLabel: "o caixa da gestora hoje" })}
            currentDate={state?.current_date}
            tickerOptions={tickerOptions}
            heldTickers={heldTickers}
            saving={setStrategy.isPending}
            onDraftChange={(next) => setDrafts((current) => ({ ...current, [selected.key]: next }))}
            onSave={(values) =>
              setStrategy.mutate({ key: selected.key, params: values }, { onSuccess: () => clearDraft(selected.key) })
            }
            onTurnOn={(values) => requestTurnOn(selected, values)}
          />
        </div>
      </div>

      <StrategyLog />

      <ConfirmDialog
        change={change}
        strategies={strategies}
        activeKey={mine.active?.key}
        openOrders={mine.open_orders}
        fund={fund}
        mandateEnd={mandateEnd}
        pending={setStrategy.isPending}
        onCancel={() => setChange(null)}
        onConfirm={confirm}
      />
    </div>
  );
}
