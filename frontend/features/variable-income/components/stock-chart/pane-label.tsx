import { displayCompactNumber, displayMoney, displayNumber } from "@/shared/lib/utils/display";
import type { IndicatorKey, IndicatorSettings, StockCandle } from "@/types";
import { INDICATOR_BY_KEY, displaySignedCompact } from "../../lib/indicators";
import { Swatch } from "../indicator-selector";
import type { Series } from "./chart-config";
import { formatOrMissing, valueOn } from "./chart-helpers";

interface PaneLabelProps {
  indicator: IndicatorKey;
  settings: IndicatorSettings;
  series: Series;
  day: string | null;
  candles: StockCandle[];
}

/** Nome, parâmetros e valor do dia de um painel. */
export function PaneLabel({ indicator, settings, series, day, candles }: PaneLabelProps) {
  const { params } = settings;
  const sessions = candles.length;
  const info = INDICATOR_BY_KEY[indicator];
  const number = (value: number) => displayNumber(value, 1);
  let text: string;
  switch (indicator) {
    case "volume": {
      const candle = day === null ? candles[candles.length - 1] : candles.find((c) => c.price_date.startsWith(day));
      text = `Volume · ${candle ? displayCompactNumber(candle.volume) : "—"}`;
      break;
    }
    case "rsi":
      text = `IFR ${params.rsi_period} · ${formatOrMissing(valueOn(series.rsi, day), params.rsi_period + 1, sessions, number)}`;
      break;
    case "macd": {
      const needed = params.macd_slow + params.macd_signal - 1;
      const line = valueOn(series.macd?.line, day);
      const signal = valueOn(series.macd?.signal, day);
      text = `MACD ${params.macd_fast}, ${params.macd_slow}, ${params.macd_signal} · ${
        line !== null && signal !== null
          ? `${displayNumber(line)} · sinal ${displayNumber(signal)}`
          : formatOrMissing(null, needed, sessions, number)
      }`;
      break;
    }
    case "stochastic":
      text = `Estocástico ${params.stochastic_k}, ${params.stochastic_d} · ${formatOrMissing(
        valueOn(series.stochastic?.k, day),
        params.stochastic_k,
        sessions,
        number,
      )}`;
      break;
    case "atr":
      text = `ATR ${params.atr_period} · ${formatOrMissing(valueOn(series.atr, day), params.atr_period, sessions, displayMoney)}`;
      break;
    default:
      text = `OBV · ${formatOrMissing(valueOn(series.obv, day), 1, sessions, displaySignedCompact)}`;
  }
  return (
    <span className="flex items-center gap-1.5">
      {info.color && <Swatch token={info.color} shape="line" />}
      {text}
    </span>
  );
}
