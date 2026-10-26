import { useState, type ReactNode } from "react";
import { ChartLine, ChevronDown, ChevronRight, Plus, X } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";
import { Switch } from "@/shared/components/ui/switch";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { MetricHint } from "@/shared/components/metric-hint";
import { ScaleRuler } from "@/shared/components/scale-ruler";
import { cn } from "@/shared/lib/utils";
import { displayNumber } from "@/shared/lib/utils/display";
import type { IndicatorKey, IndicatorParams, IndicatorSettings, MovingAverage, TechnicalSummary } from "@/types";
import {
  averageColor,
  DEFAULT_PARAMS,
  INDICATORS,
  MAX_AVERAGES,
  PARAM_LIMITS,
  countShown,
  isShown,
  scaleBands,
  toggled,
  withParams,
  type IndicatorInfo,
} from "../lib/indicators";

interface IndicatorSelectorProps {
  settings: IndicatorSettings;
  summary: TechnicalSummary | undefined;
  onChange: (next: IndicatorSettings) => void;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  expanded: IndicatorKey | null;
  onExpandedChange: (key: IndicatorKey | null) => void;
}

/** Liga e desliga cada indicador e edita os parâmetros; o gráfico atrás muda na hora. */
export function IndicatorSelector({
  settings,
  summary,
  onChange,
  open,
  onOpenChange,
  expanded,
  onExpandedChange,
}: IndicatorSelectorProps) {
  const shown = countShown(settings);
  const setParams = (params: Partial<IndicatorParams>) => onChange(withParams(settings, params));

  const editors: Partial<Record<IndicatorKey, ReactNode>> = {
    averages: <AveragesEditor averages={settings.params.averages} onChange={(averages) => setParams({ averages })} />,
    bollinger: (
      <ParamList>
        <ParamField
          label="Período"
          unit="pregões"
          value={settings.params.bollinger_period}
          limits={PARAM_LIMITS.bollinger_period}
          onCommit={(bollinger_period) => setParams({ bollinger_period })}
        />
        <ParamField
          label="Desvios"
          unit="desvios-padrão"
          step={0.5}
          value={settings.params.bollinger_deviations}
          limits={PARAM_LIMITS.bollinger_deviations}
          onCommit={(bollinger_deviations) => setParams({ bollinger_deviations })}
        />
      </ParamList>
    ),
    rsi: (
      <ParamList>
        <ParamField
          label="Período"
          unit="pregões"
          value={settings.params.rsi_period}
          limits={PARAM_LIMITS.rsi_period}
          onCommit={(rsi_period) => setParams({ rsi_period })}
        />
        <ParamField
          label="Sobrecomprado acima de"
          value={settings.params.rsi_overbought}
          limits={{
            min: Math.max(PARAM_LIMITS.rsi_overbought.min, settings.params.rsi_oversold + 1),
            max: PARAM_LIMITS.rsi_overbought.max,
          }}
          onCommit={(rsi_overbought) => setParams({ rsi_overbought })}
        />
        <ParamField
          label="Sobrevendido abaixo de"
          value={settings.params.rsi_oversold}
          limits={{
            min: PARAM_LIMITS.rsi_oversold.min,
            max: Math.min(PARAM_LIMITS.rsi_oversold.max, settings.params.rsi_overbought - 1),
          }}
          onCommit={(rsi_oversold) => setParams({ rsi_oversold })}
        />
        <RsiToday params={settings.params} summary={summary} />
      </ParamList>
    ),
    macd: (
      <ParamList>
        <ParamField
          label="Média curta"
          unit="pregões"
          value={settings.params.macd_fast}
          limits={{
            min: PARAM_LIMITS.macd_fast.min,
            max: Math.min(PARAM_LIMITS.macd_fast.max, settings.params.macd_slow - 1),
          }}
          onCommit={(macd_fast) => setParams({ macd_fast })}
        />
        <ParamField
          label="Média longa"
          unit="pregões"
          value={settings.params.macd_slow}
          limits={{
            min: Math.max(PARAM_LIMITS.macd_slow.min, settings.params.macd_fast + 1),
            max: PARAM_LIMITS.macd_slow.max,
          }}
          onCommit={(macd_slow) => setParams({ macd_slow })}
        />
        <ParamField
          label="Sinal"
          unit="pregões"
          value={settings.params.macd_signal}
          limits={PARAM_LIMITS.macd_signal}
          onCommit={(macd_signal) => setParams({ macd_signal })}
        />
      </ParamList>
    ),
    stochastic: (
      <ParamList>
        <ParamField
          label="%K"
          unit="pregões"
          value={settings.params.stochastic_k}
          limits={PARAM_LIMITS.stochastic_k}
          onCommit={(stochastic_k) => setParams({ stochastic_k })}
        />
        <ParamField
          label="%D"
          unit="pregões"
          value={settings.params.stochastic_d}
          limits={PARAM_LIMITS.stochastic_d}
          onCommit={(stochastic_d) => setParams({ stochastic_d })}
        />
      </ParamList>
    ),
    atr: (
      <ParamList>
        <ParamField
          label="Período"
          unit="pregões"
          value={settings.params.atr_period}
          limits={PARAM_LIMITS.atr_period}
          onCommit={(atr_period) => setParams({ atr_period })}
        />
      </ParamList>
    ),
  };

  return (
    <Popover open={open} onOpenChange={onOpenChange}>
      <PopoverTrigger render={<Button variant="outline-toggle" size="sm" />}>
        <ChartLine />
        Indicadores
        {shown > 0 && (
          <Badge variant="info" size="sm" numeric>
            {shown}
          </Badge>
        )}
      </PopoverTrigger>
      <PopoverContent align="end" variant="flush" className="max-h-[min(80vh,720px)] w-110">
        {/* Cabeçalho */}
        <div className="flex items-center justify-between border-b px-3.5 py-3">
          <div className="grid">
            <b className="text-sm">Indicadores</b>
            <span className="text-xs text-muted-foreground">
              {shown === 0 ? "Nenhum ligado" : `${shown} ${shown === 1 ? "ligado" : "ligados"}`} · o gráfico muda na
              hora
            </span>
          </div>
          <Button variant="ghost" size="icon-xs" aria-label="Fechar" onClick={() => onOpenChange(false)}>
            <X />
          </Button>
        </div>

        {/* Sobre o preço e painéis embaixo do gráfico */}
        {(["price", "panel"] as const).map((place) => (
          <div key={place} className={cn(place === "panel" && "mt-1 border-t")}>
            <div className="px-3.5 pt-3 pb-0.5 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">
              {place === "price" ? "Sobre o preço" : "Painéis embaixo do gráfico"}
            </div>
            {INDICATORS.filter((info) => info.place === place).map((info) => (
              <IndicatorRow
                key={info.key}
                info={info}
                on={isShown(settings, info.key)}
                params={settings.params}
                summary={summary}
                expanded={expanded === info.key}
                editor={editors[info.key]}
                onToggle={(on) => onChange(toggled(settings, info.key, on))}
                onExpand={() => onExpandedChange(expanded === info.key ? null : info.key)}
              />
            ))}
          </div>
        ))}

        {/* Rodapé */}
        <div className="flex items-center justify-between border-t px-3.5 py-3">
          <Button variant="link" size="sm" onClick={() => onChange({ ...settings, params: DEFAULT_PARAMS })}>
            Restaurar padrão
          </Button>
          <span className="text-xs text-muted-foreground">Vale para todas as ações da partida</span>
        </div>
      </PopoverContent>
    </Popover>
  );
}

interface IndicatorRowProps {
  info: IndicatorInfo;
  on: boolean;
  params: IndicatorParams;
  summary: TechnicalSummary | undefined;
  expanded: boolean;
  editor: ReactNode;
  onToggle: (on: boolean) => void;
  onExpand: () => void;
}

function IndicatorRow({
  info,
  on,
  params,
  summary: technical,
  expanded,
  editor,
  onToggle,
  onExpand,
}: IndicatorRowProps) {
  const summary = info.summary?.(params);
  const bands = scaleBands(info.key, params);
  const today = technical?.readings.find((reading) => reading.key === info.key)?.value ?? null;
  const open = expanded && editor !== undefined;
  return (
    <div
      className={cn("grid grid-cols-[auto_minmax(0,1fr)_auto] items-start gap-3 px-3.5 py-2.5", open && "bg-subtle")}
    >
      <Switch className="mt-0.5" checked={on} onCheckedChange={onToggle} aria-label={info.name} />
      <div className="grid min-w-0 gap-0.5">
        <span className="flex items-center gap-1.5 font-semibold">
          {info.name}
          {on && info.color && info.key !== "averages" && <Swatch token={info.color} />}
          <MetricHint
            metric={info.hint}
            extra={bands && <ScaleRuler value={today} low={bands.low} high={bands.high} />}
          />
        </span>
        <span className="text-xs text-muted-foreground">{info.description}</span>
        {open && <div className="mt-2.5">{editor}</div>}
      </div>
      {editor !== undefined ? (
        <button
          type="button"
          className="flex items-center gap-1 font-mono text-xs text-muted-foreground tabular-nums hover:text-foreground"
          aria-expanded={open}
          aria-label={`Parâmetros de ${info.name}`}
          onClick={onExpand}
        >
          {summary}
          {open ? <ChevronDown className="size-3.5" /> : <ChevronRight className="size-3.5" />}
        </button>
      ) : (
        <span />
      )}
    </div>
  );
}

function AveragesEditor({
  averages,
  onChange,
}: {
  averages: MovingAverage[];
  onChange: (next: MovingAverage[]) => void;
}) {
  const replace = (index: number, average: MovingAverage) =>
    onChange(averages.map((current, i) => (i === index ? average : current)));
  return (
    <div className="grid gap-1.5">
      {averages.map((average, index) => (
        <div key={index} className="flex items-center gap-2 text-[13px]">
          <Swatch token={averageColor(index)} />
          <ToggleGroup
            variant="segmented"
            size="sm"
            aria-label="Tipo de média"
            value={[average.kind]}
            onValueChange={(values) =>
              values[0] &&
              replace(index, {
                ...average,
                kind: values[0] as MovingAverage["kind"],
              })
            }
          >
            <ToggleGroupItem value="sma">Simples</ToggleGroupItem>
            <ToggleGroupItem value="ema">Exponencial</ToggleGroupItem>
          </ToggleGroup>
          <NumberInput
            value={average.period}
            limits={PARAM_LIMITS.average}
            label="Período da média"
            onCommit={(period) => replace(index, { ...average, period })}
          />
          <span className="text-xs text-muted-foreground">pregões</span>
          <Button
            variant="ghost"
            size="icon-xs"
            className="ml-auto"
            aria-label="Remover média"
            disabled={averages.length === 1}
            onClick={() => onChange(averages.filter((_, i) => i !== index))}
          >
            <X />
          </Button>
        </div>
      ))}
      {averages.length < MAX_AVERAGES && (
        <Button
          variant="link"
          size="sm"
          className="justify-self-start"
          onClick={() => onChange([...averages, { kind: "sma", period: 100 }])}
        >
          <Plus />
          Adicionar outra média
        </Button>
      )}
    </div>
  );
}

function ParamList({ children }: { children: ReactNode }) {
  return <div className="grid gap-2">{children}</div>;
}

interface Limits {
  min: number;
  max: number;
}

interface ParamFieldProps {
  label: string;
  unit?: string;
  value: number;
  limits: Limits;
  step?: number;
  onCommit: (value: number) => void;
}

function ParamField({ label, unit, value, limits, step, onCommit }: ParamFieldProps) {
  return (
    <label className="flex items-center gap-2 text-[13px]">
      <span className="min-w-36">{label}</span>
      <NumberInput value={value} limits={limits} step={step} label={label} onCommit={onCommit} />
      {unit && <span className="text-xs text-muted-foreground">{unit}</span>}
    </label>
  );
}

interface NumberInputProps {
  value: number;
  limits: Limits;
  step?: number;
  label: string;
  onCommit: (value: number) => void;
}

/**
 * Campo que grava só o número dentro dos limites; enquanto se digita, o texto fica
 * aqui. O campo nasce de novo quando o valor gravado muda, como no "Restaurar padrão".
 */
function NumberInput(props: NumberInputProps) {
  return <DraftNumberInput key={props.value} {...props} />;
}

function DraftNumberInput({ value, limits, step = 1, label, onCommit }: NumberInputProps) {
  const [draft, setDraft] = useState(String(value).replace(".", ","));
  const parsed = Number(draft.replace(",", "."));
  const valid = draft !== "" && Number.isFinite(parsed) && parsed >= limits.min && parsed <= limits.max;
  const commit = () => {
    if (valid && parsed !== value) onCommit(parsed);
    if (!valid) setDraft(String(value).replace(".", ","));
  };
  return (
    <Input
      fieldSize="xs"
      numeric
      inputMode="decimal"
      aria-label={label}
      aria-invalid={!valid}
      title={`De ${displayNumber(limits.min, step < 1 ? 1 : 0)} a ${displayNumber(limits.max, step < 1 ? 1 : 0)}`}
      className="w-16 text-right"
      value={draft}
      onChange={(event) => setDraft(event.target.value)}
      onBlur={commit}
      onKeyDown={(event) => event.key === "Enter" && commit()}
    />
  );
}

function RsiToday({ params, summary }: { params: IndicatorParams; summary: TechnicalSummary | undefined }) {
  const rsi = summary?.readings.find((reading) => reading.key === "rsi");
  if (!rsi || rsi.value === null) return null;
  return (
    <div className="rounded-lg bg-card px-2.5 py-2 text-xs ring-1 ring-border">
      Com {params.rsi_period} pregões, o IFR de hoje é{" "}
      <b className="font-mono text-(--chart-6) tabular-nums">{displayNumber(rsi.value, 1)}</b>: {rsi.reason}. Período
      menor reage mais rápido e cruza as faixas mais vezes.
    </div>
  );
}

/** A cor de uma série: quadrado nas listas, traço na legenda do gráfico. */
export function Swatch({ token, shape = "square" }: { token: string; shape?: "square" | "line" }) {
  return (
    <span
      className={cn(
        "inline-block shrink-0",
        shape === "square" ? "size-2.5 rounded-[3px]" : "h-[3px] w-3.5 rounded-xs",
      )}
      style={{ background: `var(${token})` }}
    />
  );
}
