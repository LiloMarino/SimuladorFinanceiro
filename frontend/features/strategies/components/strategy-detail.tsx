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
import { useStrategyView } from "../hooks/queries/useStrategyView";
import { LEGEND_SWATCH } from "../lib/signal-style";
import { GROUP_LABEL } from "../lib/strategy-display";
import {
  defaultValues,
  draftErrors,
  fromDraft,
  sameValues,
  toDraft,
  type ParamDraft,
  type ParamValues,
} from "@/shared/lib/strategy-params";
import { ActiveMark } from "./active-mark";
import { SignalChart, type SavedSignalLine } from "./signal-chart";
import { StrategyDataBlock } from "./strategy-data-block";
import { StrategyParamsForm } from "@/shared/components/strategy-params-form";

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

  // O gráfico olha uma ação: a escolhida na lista, ou o ativo único da estratégia
  const hasChart = strategy.view === "signal";
  const dataKind = strategy.view === "ranking" || strategy.view === "allocation" ? strategy.view : null;
  const tickersParam = strategy.params.find((param) => param.kind === "tickers");
  const assetParam = strategy.params.find((param) => param.kind === "ticker");
  const tickersEntry = tickersParam ? draft[tickersParam.key] : undefined;
  const tickers = Array.isArray(tickersEntry) ? tickersEntry : [];
  const assetEntry = assetParam ? draft[assetParam.key] : undefined;
  const watched = assetParam
    ? typeof assetEntry === "string" && assetEntry !== ""
      ? assetEntry
      : null
    : pickedTicker && tickers.includes(pickedTicker)
      ? pickedTicker
      : (tickers[0] ?? null);

  const signal = useStrategySignal(strategy.key, hasChart && values ? watched : null, values ?? saved, currentDate);
  const savedSignal = useStrategySignal(strategy.key, previewing ? watched : null, saved, currentDate);
  const signalReady = !!signal.data && !signal.isPlaceholderData;
  const dataView = useStrategyView(strategy.key, dataKind && values ? values : null, currentDate);
  const dataReady = !!dataView.data && !dataView.isPlaceholderData;

  // Erro do servidor (por campo) e o que a digitação ainda não permite
  const errors: Record<string, string> = signalReady
    ? { ...signal.data?.errors }
    : dataReady
      ? { ...dataView.data?.errors }
      : {};
  Object.assign(errors, draftErrors(strategy.params, draft));
  const valid =
    values !== null && Object.keys(errors).length === 0 && (!hasChart || signalReady) && (!dataKind || dataReady);

  const savedLines: SavedSignalLine[] = [];
  if (previewing && signalReady && savedSignal.data && !savedSignal.isPlaceholderData) {
    for (const line of savedSignal.data.lines) {
      const current = signal.data?.lines.find((candidate) => candidate.key === line.key);
      if (line.style !== "price" && current && current.label !== line.label)
        savedLines.push({ ...line, legend: `${line.label.replace(/ dias$/, "")} (salva)` });
    }
  }

  // O gráfico anterior fica na tela enquanto o novo chega; a validade só vale com o dado novo
  const lines = signal.data?.lines ?? [];
  const levels = signal.data?.levels ?? [];
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
            {strategy.term_hint && <InfoHint label="O que isso quer dizer">{strategy.term_hint}</InfoHint>}
          </p>
        </div>
      </CardContent>

      {/* O que ela olha */}
      {(hasChart || dataKind) && (
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
              {hasChart && tickersParam && (
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
              )}
              {hasChart && assetParam && watched && (
                <Badge variant="secondary" size="tag" numeric>
                  {watched}
                </Badge>
              )}
            </div>

            {dataKind && <StrategyDataBlock kind={dataKind} query={dataView} />}

            {hasChart && (
              <>
                {lines.length > 0 ? (
                  <SignalChart
                    lines={lines}
                    levels={levels}
                    markers={signal.data?.markers ?? []}
                    savedLines={savedLines}
                  />
                ) : (
                  <div className="grid h-52.5 place-items-center rounded-lg bg-subtle text-sm text-muted-foreground">
                    {Object.keys(errors).length > 0
                      ? "Corrija os parâmetros para ver o gráfico."
                      : "Carregando o gráfico…"}
                  </div>
                )}

                {/* Legenda */}
                <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
                  {lines.map((line) => (
                    <span key={line.key} className="inline-flex items-center gap-1.5">
                      <i className={`inline-block h-0.75 w-3.5 rounded-sm ${LEGEND_SWATCH[line.style]}`} />
                      {line.label}
                    </span>
                  ))}
                  {savedLines.map((line) => (
                    <span key={line.key} className="inline-flex items-center gap-1.5">
                      <i className={`inline-block h-0.75 w-3.5 rounded-sm opacity-50 ${LEGEND_SWATCH[line.style]}`} />
                      {line.legend}
                    </span>
                  ))}
                  <span className="text-success">▲ compra</span>
                  <span className="text-destructive">▼ venda</span>
                </div>
                {shortHistory && <p className="text-xs text-warning">{shortHistory}</p>}
              </>
            )}
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
