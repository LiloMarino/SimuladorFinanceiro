import type {
  CandlePatterns,
  IndicatorPoint,
  OrderPreviewRequest,
  SimulationEvents,
  TechnicalIndicators,
} from "@/types";
import { eventAccountKey, type AccountKey } from "@/shared/lib/active-account";

type PreviewEvent = SimulationEvents[`order_preview:${string}`];
type IndicatorsEvent = SimulationEvents[`indicators_update:${string}`];
type PatternsEvent = SimulationEvents[`candle_patterns_update:${string}`];

/** O que a chave da prévia guarda, vindo da leitura HTTP ou do aviso: a prévia ou o motivo da recusa. */
export type OrderPreviewOutcome = Pick<PreviewEvent, "preview" | "refused">;

/** O desfecho que o aviso entrega à chave da prévia. */
export const outcomeOfPreviewEvent = ({ preview, refused }: PreviewEvent): OrderPreviewOutcome => ({
  preview,
  refused,
});

const sameNumber = (sent: string | number | null | undefined, draft: string | number | null | undefined) =>
  sent === null || sent === undefined || draft === null || draft === undefined
    ? (sent ?? null) === (draft ?? null)
    : Number(sent) === Number(draft);

/** A prévia do aviso é a do rascunho que a boleta mostra: mesmo pedido, na mesma conta. */
export function previewMatchesDraft(event: PreviewEvent, draft: OrderPreviewRequest, account: AccountKey): boolean {
  const { request } = event;
  return (
    eventAccountKey(event.account) === account &&
    request.action === draft.action &&
    sameNumber(request.quantity, draft.quantity) &&
    sameNumber(request.amount, draft.amount) &&
    Boolean(request.max_size) === Boolean(draft.max_size) &&
    sameNumber(request.limit_price, draft.limit_price)
  );
}

/** Soma à ponta da série o ponto do último pregão: o mesmo dia substitui, um dia anterior é ignorado. */
function mergePoints(current: IndicatorPoint[], incoming: IndicatorPoint[]): IndicatorPoint[] {
  let merged = current;
  for (const point of incoming) {
    const last = merged.at(-1);
    if (last === undefined || point.date > last.date) merged = [...merged, point];
    else if (point.date === last.date) merged = [...merged.slice(0, -1), point];
  }
  return merged;
}

function mergeSeries(current: TechnicalIndicators["series"], update: TechnicalIndicators["series"]) {
  const merged = { ...current };
  if (current.averages && update.averages) {
    merged.averages = current.averages.map((average) => {
      const incoming = update.averages?.find((a) => a.kind === average.kind && a.period === average.period);
      return incoming ? { ...average, points: mergePoints(average.points, incoming.points) } : average;
    });
  }
  if (current.bollinger && update.bollinger) {
    merged.bollinger = {
      upper: mergePoints(current.bollinger.upper, update.bollinger.upper),
      middle: mergePoints(current.bollinger.middle, update.bollinger.middle),
      lower: mergePoints(current.bollinger.lower, update.bollinger.lower),
    };
  }
  if (current.macd && update.macd) {
    merged.macd = {
      line: mergePoints(current.macd.line, update.macd.line),
      signal: mergePoints(current.macd.signal, update.macd.signal),
      histogram: mergePoints(current.macd.histogram, update.macd.histogram),
    };
  }
  if (current.stochastic && update.stochastic) {
    merged.stochastic = {
      k: mergePoints(current.stochastic.k, update.stochastic.k),
      d: mergePoints(current.stochastic.d, update.stochastic.d),
    };
  }
  if (current.rsi && update.rsi) merged.rsi = mergePoints(current.rsi, update.rsi);
  if (current.atr && update.atr) merged.atr = mergePoints(current.atr, update.atr);
  if (current.obv && update.obv) merged.obv = mergePoints(current.obv, update.obv);
  return merged;
}

/**
 * Acrescenta o último pregão aos indicadores que a tela já tem: o ponto novo de cada série e o
 * resumo inteiro. Devolve `null` quando as séries não terminam no pregão anterior ao do aviso
 * (um aviso se perdeu): a tela lê tudo de novo.
 */
export function mergeIndicatorsUpdate(
  current: TechnicalIndicators,
  event: IndicatorsEvent,
): TechnicalIndicators | null {
  const have = current.summary.date;
  const next = event.update.summary.date;
  if (have === null || next === null) return null;
  if (next <= have) return current;
  if (event.previous_date !== have) return null;
  return { series: mergeSeries(current.series, event.update.series), summary: event.update.summary };
}

/** Troca os padrões que terminam do `from_date` em diante pelos do aviso e leva as estatísticas inteiras. */
export function mergePatternsUpdate(current: CandlePatterns, update: PatternsEvent): CandlePatterns {
  const { from_date: from } = update;
  const kept = from === null ? [] : current.patterns.filter((pattern) => pattern.end < from);
  return { patterns: [...kept, ...update.patterns], stats: update.stats };
}
