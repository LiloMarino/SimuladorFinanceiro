import { useState } from "react";
import { Power } from "lucide-react";
import { InfoHint } from "@/shared/components/info-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Separator } from "@/shared/components/ui/separator";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { MyStrategy, StrategyInfo } from "@/types";
import { useStrategySignal } from "../hooks/queries/useStrategySignal";
import { GROUP_LABEL, TERM_HINT } from "../lib/strategy-display";
import {
  defaultValues,
  fromDraft,
  sameValues,
  toDraft,
  type ParamDraft,
  type ParamValues,
} from "../lib/strategy-params";
import { ActiveMark } from "./active-mark";
import { SignalChart, type SavedSignalLine } from "./signal-chart";
import { StrategyParamsForm } from "./strategy-params-form";

type StrategyDetailProps = {
  strategy: StrategyInfo;
  /** A configuração ligada desta estratégia; nulo se ela está desligada */
  active: MyStrategy["active"];
  draft: ParamDraft;
  /** Caixa de hoje, em reais */
  cash: string;
  /** Dia da partida; o gráfico acompanha */
  currentDate: string | undefined;
  tickerOptions: string[];
  saving: boolean;
  onDraftChange: (draft: ParamDraft) => void;
  onSave: (values: ParamValues) => void;
  onTurnOn: (values: ParamValues) => void;
};

const LEGEND_SWATCH = { price: "bg-faint-foreground", short: "bg-chart-1", long: "bg-chart-5" } as const;

/** A estratégia escolhida: regra, o que ela olha no gráfico e os parâmetros em rascunho. */
export function StrategyDetail({
  strategy,
  active,
  draft,
  cash,
  currentDate,
  tickerOptions,
  saving,
  onDraftChange,
  onSave,
  onTurnOn,
}: StrategyDetailProps) {
  const [pickedTicker, setPickedTicker] = useState<string | null>(null);

  const defaults = defaultValues(strategy);
  const saved = active ? active.params : defaults;
  const values = fromDraft(strategy.params, draft);
  const changed = values === null || !sameValues(values, saved);
  const previewing = !!active && changed && values !== null;

  const tickersParam = strategy.params.find((param) => param.kind === "tickers");
  const hasChart = !!tickersParam;
  const tickersEntry = tickersParam ? draft[tickersParam.key] : undefined;
  const tickers = Array.isArray(tickersEntry) ? tickersEntry : [];
  const watched = pickedTicker && tickers.includes(pickedTicker) ? pickedTicker : (tickers[0] ?? null);

  const signal = useStrategySignal(strategy.key, hasChart && values ? watched : null, values ?? saved, currentDate);
  const savedSignal = useStrategySignal(strategy.key, previewing ? watched : null, saved, currentDate);
  const signalReady = !!signal.data && !signal.isPlaceholderData;

  // Erro do servidor (por campo) e o que a digitação ainda não permite
  const errors: Record<string, string> = signalReady ? { ...signal.data?.errors } : {};
  for (const param of strategy.params) {
    const entry = draft[param.key];
    if (param.kind === "tickers" && Array.isArray(entry) && entry.length === 0)
      errors[param.key] = "Escolha ao menos uma ação.";
    if (param.kind !== "tickers" && typeof entry === "string" && !/^\d+$/.test(entry.trim()))
      errors[param.key] = "Digite um número inteiro.";
  }
  const valid = values !== null && Object.keys(errors).length === 0 && (!hasChart || signalReady);

  const savedLines: SavedSignalLine[] = [];
  if (previewing && signalReady && savedSignal.data && !savedSignal.isPlaceholderData) {
    for (const line of savedSignal.data.lines) {
      const current = signal.data?.lines.find((candidate) => candidate.key === line.key);
      if (line.key !== "price" && current && current.label !== line.label)
        savedLines.push({ ...line, legend: `${line.label.replace(/ dias$/, "")} (salva)` });
    }
  }

  // O gráfico anterior fica na tela enquanto o novo chega; a validade só vale com o dado novo
  const lines = signal.data?.lines ?? [];
  const shortHistory =
    signalReady && signal.data!.available_days < signal.data!.needed_days
      ? `${watched} tem ${signal.data!.available_days} dias de histórico nesta partida, e a estratégia pede ${signal.data!.needed_days}.`
      : null;

  return (
    <Card>
      {/* Cabeçalho */}
      <CardContent>
        <div className="grid gap-1">
          <span className="flex items-center gap-2">
            <Badge variant={strategy.group === "tactic" ? "info" : "secondary"} size="tag">
              {GROUP_LABEL[strategy.group]}
            </Badge>
            {active ? (
              <ActiveMark since={displayDayMonth(active.since)} />
            ) : (
              <span className="text-[11px] text-muted-foreground">Desligada</span>
            )}
          </span>
          <h2 className="text-lg font-semibold">{strategy.name}</h2>
          <p className="flex items-start gap-1.5 text-[13px] text-muted-foreground">
            <span>{strategy.description}</span>
            {TERM_HINT[strategy.key] && <InfoHint label="O que isso quer dizer">{TERM_HINT[strategy.key]}</InfoHint>}
          </p>
        </div>
      </CardContent>

      {/* O que ela olha */}
      {hasChart && (
        <CardContent>
          <div className="grid gap-2.5">
            <div className="flex items-center justify-between gap-3">
              <span className="flex items-center gap-2 text-sm font-medium">
                O que ela olha
                {previewing && (
                  <Badge variant="warning" size="sm">
                    Prévia · ainda não salva
                  </Badge>
                )}
              </span>
              <Select value={watched} onValueChange={setPickedTicker} disabled={tickers.length === 0}>
                <SelectTrigger size="sm" aria-label="Ação do gráfico">
                  <SelectValue placeholder="Sem ações" />
                </SelectTrigger>
                <SelectContent>
                  {tickers.map((ticker) => (
                    <SelectItem key={ticker} value={ticker}>
                      <span className="font-mono font-semibold">{ticker}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {lines.length > 0 ? (
              <SignalChart lines={lines} markers={signal.data?.markers ?? []} savedLines={savedLines} />
            ) : (
              <div className="grid h-52.5 place-items-center rounded-lg bg-subtle text-sm text-muted-foreground">
                {Object.keys(errors).length > 0 ? "Corrija os parâmetros para ver o gráfico." : "Carregando o gráfico…"}
              </div>
            )}

            {/* Legenda */}
            <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
              {lines.map((line) => (
                <span key={line.key} className="inline-flex items-center gap-1.5">
                  <i className={`inline-block h-0.75 w-3.5 rounded-sm ${LEGEND_SWATCH[line.key]}`} />
                  {line.label}
                </span>
              ))}
              {savedLines.map((line) => (
                <span key={line.key} className="inline-flex items-center gap-1.5">
                  <i className={`inline-block h-0.75 w-3.5 rounded-sm opacity-50 ${LEGEND_SWATCH[line.key]}`} />
                  {line.legend}
                </span>
              ))}
              <span className="text-success">▲ compra</span>
              <span className="text-destructive">▼ venda</span>
            </div>
            {shortHistory && <p className="text-xs text-warning">{shortHistory}</p>}
          </div>
        </CardContent>
      )}

      <Separator />

      {/* Parâmetros */}
      <CardContent>
        <div className="grid gap-4">
          {strategy.params.length > 0 ? (
            <StrategyParamsForm
              strategy={strategy}
              draft={draft}
              saved={saved}
              errors={errors}
              tickerOptions={tickerOptions}
              cash={cash}
              onChange={onDraftChange}
            />
          ) : (
            <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs text-muted-foreground">
              Esta estratégia não tem parâmetros: é ligar ou deixar desligada.
            </p>
          )}

          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs text-muted-foreground">
              {active && !previewing && strategy.params.length > 0 ? "Vale a partir do próximo dia da partida." : ""}
            </span>
            <div className="flex gap-2">
              {strategy.params.length > 0 &&
                (previewing ? (
                  <Button variant="outline" size="sm" onClick={() => onDraftChange(toDraft(saved))}>
                    Descartar
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={values !== null && sameValues(values, defaults)}
                    onClick={() => onDraftChange(toDraft(defaults))}
                  >
                    Restaurar padrão
                  </Button>
                ))}
              {active ? (
                strategy.params.length > 0 && (
                  <Button size="sm" disabled={!valid || !changed || saving} onClick={() => values && onSave(values)}>
                    Salvar parâmetros
                  </Button>
                )
              ) : (
                <Button disabled={!valid || saving} onClick={() => values && onTurnOn(values)}>
                  <Power />
                  Ligar esta estratégia
                </Button>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
