import { Bot, Hand } from "lucide-react";
import { useState } from "react";
import { CardState } from "@/shared/components/card-state";
import { StrategyList } from "@/shared/components/strategy-list";
import { Card, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { useVariableIncomeStocks } from "@/shared/hooks/queries/useVariableIncomeStocks";
import { defaultValues, toDraft, type ParamDraft } from "@/shared/lib/strategy-params";
import type { BotTicker, FundDetails, MyStrategy, StrategyInfo } from "@/types";
import { useSetFundStrategy } from "../hooks/mutations/useSetFundStrategy";
import { useFundStrategies } from "../hooks/queries/useFundStrategies";
import { useFundStrategy } from "../hooks/queries/useFundStrategy";
import { FundStrategyDetail } from "./fund-strategy-detail";

type Mode = "manual" | "automatic";

const TITLE = "Automático da carteira";

/** O card "Automático da carteira": resolve a lista, a estratégia ligada e as ações antes de abrir o painel. */
export function FundAutomaticCard({ fund }: { fund: FundDetails }) {
  const strategies = useFundStrategies();
  const mine = useFundStrategy(fund.id);
  const stocks = useVariableIncomeStocks();

  if (!strategies.data || !mine.data || !stocks.data) {
    const error = strategies.error ?? mine.error ?? stocks.error;
    return (
      <CardState
        title={TITLE}
        label="Carregando o automático da carteira"
        error={error}
        onRetry={() => {
          void strategies.refetch();
          void mine.refetch();
          void stocks.refetch();
        }}
        errorTitle="Não deu para carregar o automático"
      >
        <Skeleton className="h-64" />
      </CardState>
    );
  }

  return (
    <FundAutomaticPanel
      fund={fund}
      strategies={strategies.data}
      mine={mine.data}
      tickerOptions={stocks.data.map(({ ticker, name }) => ({ ticker, name }))}
    />
  );
}

type PanelProps = {
  fund: FundDetails;
  strategies: StrategyInfo[];
  mine: MyStrategy;
  tickerOptions: BotTicker[];
};

function FundAutomaticPanel({ fund, strategies, mine, tickerOptions }: PanelProps) {
  const { data: state } = useSimulationState();
  const setStrategy = useSetFundStrategy(fund.id);
  const [wantsAutomatic, setWantsAutomatic] = useState(false);
  const [pickedKey, setPickedKey] = useState<string | null>(null);
  const [drafts, setDrafts] = useState<Record<string, ParamDraft>>({});

  // Na presidência o congelamento das decisões vale o mandato todo; só a carteira se solta com o automático
  const presidency = fund.frozen_until !== null;
  const mode: Mode = mine.active || wantsAutomatic ? "automatic" : "manual";
  const selected = strategies.find((strategy) => strategy.key === (pickedKey ?? mine.active?.key)) ?? strategies[0];
  const cash = fund.composition.find((item) => item.asset_class === "cash")?.value ?? "0";

  const changeMode = (next: Mode) => {
    if (next === "automatic") return setWantsAutomatic(true);
    setWantsAutomatic(false);
    if (mine.active) setStrategy.mutate({ key: null, params: {} });
  };

  const clearDraft = (key: string) =>
    setDrafts((current) => Object.fromEntries(Object.entries(current).filter(([draftKey]) => draftKey !== key)));

  return (
    <Card>
      {/* Título e modo */}
      <CardHeader>
        <CardTitle>{TITLE}</CardTitle>
        <CardDescription>
          A mesma lista da página Estratégias e da aba Minha preparação: uma estratégia opera a carteira da gestora no
          lugar do gestor.
        </CardDescription>
        <ToggleGroup
          variant="segmented"
          aria-label="Como a carteira é operada"
          value={[mode]}
          onValueChange={(values) => values[0] && changeMode(values[0] as Mode)}
        >
          <ToggleGroupItem value="manual" disabled={setStrategy.isPending}>
            <Hand />
            Manual
          </ToggleGroupItem>
          <ToggleGroupItem value="automatic" disabled={setStrategy.isPending}>
            <Bot />
            Automático
          </ToggleGroupItem>
        </ToggleGroup>
      </CardHeader>

      {/* Lista e detalhe */}
      {mode === "automatic" && selected && (
        <div className="grid border-y xl:grid-cols-[340px_minmax(0,1fr)]">
          <div className="border-r bg-subtle px-2.5 pt-1.5 pb-3">
            <StrategyList
              strategies={strategies}
              selectedKey={selected.key}
              activeKey={mine.active?.key}
              surface="panel"
              onSelect={setPickedKey}
            />
          </div>
          <FundStrategyDetail
            key={selected.key}
            fundId={fund.id}
            strategy={selected}
            active={mine.active?.key === selected.key ? mine.active : null}
            otherActive={!!mine.active}
            draft={
              drafts[selected.key] ??
              toDraft(mine.active?.key === selected.key ? mine.active.params : defaultValues(selected))
            }
            cash={cash}
            currentDate={state?.current_date}
            tickerOptions={tickerOptions}
            heldTickers={(fund.positions ?? []).flatMap((position) => (position.ticker ? [position.ticker] : []))}
            saving={setStrategy.isPending}
            onDraftChange={(next) => setDrafts((current) => ({ ...current, [selected.key]: next }))}
            onSave={(values) =>
              setStrategy.mutate({ key: selected.key, params: values }, { onSuccess: () => clearDraft(selected.key) })
            }
            onTurnOn={(values) =>
              setStrategy.mutate({ key: selected.key, params: values }, { onSuccess: () => clearDraft(selected.key) })
            }
          />
        </div>
      )}

      {/* Nota */}
      <p className="bg-subtle px-5.5 py-3 text-xs text-muted-foreground">
        {presidency && mine.active
          ? "Desligar o automático congela a carteira até o fim do mandato."
          : "Ligado, as boletas da gestora travam e a estratégia opera a cada pregão; sua conta pessoal segue à mão, com a estratégia dela à parte."}
      </p>
    </Card>
  );
}
