import { QueryClient } from "@tanstack/react-query";
import { describe, expect, it } from "vitest";
import type {
  CandlePatterns,
  IndicatorPoint,
  OrderPreview,
  OrderPreviewRequest,
  SimulationEvents,
  TechnicalIndicators,
} from "@/types";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import { outcomeOfPreviewEvent, type PreviewOutcome } from "@/shared/lib/realtime/preview-outcome";
import { mergeIndicatorsUpdate, mergePatternsUpdate, previewMatchesDraft } from "./asset-feed";

type PreviewEvent = SimulationEvents[`order_preview:${string}`];
type IndicatorsEvent = SimulationEvents[`indicators_update:${string}`];
type PatternsEvent = SimulationEvents[`candle_patterns_update:${string}`];

const point = (date: string, value: number): IndicatorPoint => ({ date, value });

const summary = (date: string | null) => ({
  date,
  readings: [],
  buys: 0,
  sells: 0,
  counted: 0,
  sided: 0,
  score: null,
  verdict: null,
});

const emptySeries: TechnicalIndicators["series"] = {
  averages: null,
  bollinger: null,
  rsi: null,
  macd: null,
  stochastic: null,
  atr: null,
  obv: null,
};

const indicators = (date: string, rsi: IndicatorPoint[]): TechnicalIndicators => ({
  series: { ...emptySeries, rsi },
  summary: summary(date),
});

const indicatorsEvent = (previous: string | null, date: string, rsi: IndicatorPoint[]): IndicatorsEvent => ({
  request: { params: {} as IndicatorsEvent["request"]["params"], series: ["rsi"] },
  previous_date: previous,
  update: indicators(date, rsi),
});

describe("prévia da ordem do aviso", () => {
  const draft: OrderPreviewRequest = { action: "buy", quantity: "100", max_size: false, limit_price: 10 };
  const event = (patch: Partial<PreviewEvent["request"]>, account: number | null = null): PreviewEvent => ({
    request: { action: "buy", quantity: "100", max_size: null, limit_price: 10, ...patch },
    account,
    preview: null,
    refused: null,
  });

  it("vale quando é o pedido do rascunho na mesma conta", () => {
    expect(previewMatchesDraft(event({}), draft, "personal")).toBe(true);
    expect(previewMatchesDraft(event({ quantity: "100.0" }), draft, "personal")).toBe(true);
  });

  it("não vale para outro pedido nem para outra conta", () => {
    expect(previewMatchesDraft(event({ quantity: "50" }), draft, "personal")).toBe(false);
    expect(previewMatchesDraft(event({ action: "sell" }), draft, "personal")).toBe(false);
    expect(previewMatchesDraft(event({ limit_price: null }), draft, "personal")).toBe(false);
    expect(previewMatchesDraft(event({}, 7), draft, "personal")).toBe(false);
    expect(previewMatchesDraft(event({}, 7), draft, 7)).toBe(true);
  });
});

describe("desfecho da prévia do aviso", () => {
  const refusedEvent: PreviewEvent = {
    request: { action: "buy", quantity: "100", max_size: null, limit_price: 10 },
    account: null,
    preview: null,
    refused: "O valor não paga uma unidade",
  };

  it("leva o motivo da recusa e nenhuma prévia", () => {
    expect(outcomeOfPreviewEvent(refusedEvent)).toEqual({ preview: null, refused: "O valor não paga uma unidade" });
  });

  it("a recusa do aviso troca a prévia que a chave guardava", async () => {
    const client = new QueryClient();
    const key = ["prévia"];
    const previous = { preview: { quantity: "100" }, refused: null } as unknown as PreviewOutcome<OrderPreview>;
    client.setQueryData(key, previous);
    await applyRealtime(client, key, outcomeOfPreviewEvent(refusedEvent));
    expect(client.getQueryData<PreviewOutcome<OrderPreview>>(key)).toEqual({
      preview: null,
      refused: "O valor não paga uma unidade",
    });
  });
});

describe("indicadores do aviso", () => {
  it("acrescenta o ponto do pregão novo e leva o resumo", () => {
    const current = indicators("2024-01-02", [point("2024-01-01", 40), point("2024-01-02", 50)]);
    const merged = mergeIndicatorsUpdate(
      current,
      indicatorsEvent("2024-01-02", "2024-01-03", [point("2024-01-03", 55)]),
    );
    expect(merged?.series.rsi).toEqual([point("2024-01-01", 40), point("2024-01-02", 50), point("2024-01-03", 55)]);
    expect(merged?.summary.date).toBe("2024-01-03");
  });

  it("um aviso que não continua o pregão anterior manda ler tudo de novo", () => {
    const current = indicators("2024-01-02", [point("2024-01-02", 50)]);
    expect(
      mergeIndicatorsUpdate(current, indicatorsEvent("2024-01-04", "2024-01-05", [point("2024-01-05", 1)])),
    ).toBeNull();
  });

  it("um aviso de pregão já visto não muda nada", () => {
    const current = indicators("2024-01-03", [point("2024-01-03", 50)]);
    expect(mergeIndicatorsUpdate(current, indicatorsEvent("2024-01-02", "2024-01-03", [point("2024-01-03", 99)]))).toBe(
      current,
    );
  });

  it("não acrescenta a série que a tela não pediu", () => {
    const current = indicators("2024-01-02", [point("2024-01-02", 50)]);
    const event = indicatorsEvent("2024-01-02", "2024-01-03", [point("2024-01-03", 55)]);
    event.update.series.atr = [point("2024-01-03", 2)];
    expect(mergeIndicatorsUpdate(current, event)?.series.atr).toBeNull();
  });
});

describe("padrões de vela do aviso", () => {
  type Pattern = CandlePatterns["patterns"][number];
  const pattern = (end: string, hit: boolean | null = null): Pattern => ({
    code: "doji",
    start: end,
    end,
    direction: "neutral",
    change_5d: null,
    hit,
  });

  it("troca os padrões do período reavaliado e leva as estatísticas", () => {
    const current: CandlePatterns = {
      patterns: [pattern("2024-01-01", true), pattern("2024-01-04"), pattern("2024-01-05")],
      stats: [],
    };
    const update: PatternsEvent = {
      from_date: "2024-01-04",
      patterns: [pattern("2024-01-04", true), pattern("2024-01-08")],
      stats: [{ code: "doji", checked: 3, hits: 2 }],
    };
    const merged = mergePatternsUpdate(current, update);
    expect(merged.patterns.map((p) => p.end)).toEqual(["2024-01-01", "2024-01-04", "2024-01-08"]);
    expect(merged.patterns[1]?.hit).toBe(true);
    expect(merged.stats).toEqual(update.stats);
  });

  it("sem data de corte o aviso traz tudo", () => {
    const current: CandlePatterns = { patterns: [pattern("2024-01-01")], stats: [] };
    const merged = mergePatternsUpdate(current, { from_date: null, patterns: [], stats: [] });
    expect(merged.patterns).toEqual([]);
  });
});
