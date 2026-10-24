import type { ReactNode } from "react";
import { InfoHint } from "@/shared/components/info-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/shared/components/ui/input-group";
import { cashShare } from "@/shared/lib/strategy-orders";
import { displayMoney } from "@/shared/lib/utils/display";
import type { StrategyInfo, StrategyParam } from "@/types";
import { rangeHint, type ParamDraft, type ParamValues } from "@/shared/lib/strategy-params";
import { TickerPicker } from "@/shared/components/ticker-picker";

/** Quantas ações aparecem como chip antes do "+N". */
const VISIBLE_TICKERS = 5;

type StrategyParamsFormProps = {
  strategy: StrategyInfo;
  draft: ParamDraft;
  /** O que está salvo (ou o padrão, se a estratégia está desligada) */
  saved: ParamValues;
  /** Erro por campo: o que o servidor devolveu e o que a digitação ainda não permite */
  errors: Record<string, string>;
  tickerOptions: string[];
  /** Caixa de hoje, em reais */
  cash: string;
  /** De onde vem o caixa do exemplo: "o caixa de hoje" ou "o saldo inicial" */
  cashLabel?: string;
  /** Ação ao lado do título, como "Restaurar padrão" */
  headerAction?: ReactNode;
  /** Compara cada número com o padrão da estratégia: o que mudou fica em azul, com o aviso "Mudou" */
  compareToDefault?: boolean;
  onChange: (draft: ParamDraft) => void;
};

/** Os parâmetros da estratégia: números com unidade, o ativo, a lista de ações e o exemplo em reais. */
export function StrategyParamsForm({
  strategy,
  draft,
  saved,
  errors,
  tickerOptions,
  cash,
  cashLabel = "o caixa de hoje",
  headerAction,
  compareToDefault = false,
  onChange,
}: StrategyParamsFormProps) {
  const percentParam = strategy.params.find((param) => param.kind === "percent");
  const percentText = percentParam ? draft[percentParam.key] : undefined;
  const percent = typeof percentText === "string" && percentText !== "" ? Number(percentText) : NaN;

  return (
    <div className="grid gap-3.5">
      <div className="flex items-baseline justify-between">
        <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">Parâmetros</span>
        {headerAction}
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {strategy.params.map((param) => {
          if (param.kind === "tickers")
            return (
              <TickersField
                key={param.key}
                param={param}
                tickers={Array.isArray(draft[param.key]) ? (draft[param.key] as string[]) : []}
                error={errors[param.key]}
                options={tickerOptions}
                onChange={(tickers) => onChange({ ...draft, [param.key]: tickers })}
              />
            );
          if (param.kind === "ticker")
            return (
              <AssetField
                key={param.key}
                param={param}
                ticker={String(draft[param.key] ?? "")}
                error={errors[param.key]}
                options={tickerOptions}
                onChange={(ticker) => onChange({ ...draft, [param.key]: ticker })}
              />
            );
          return (
            <NumberField
              key={param.key}
              param={param}
              text={String(draft[param.key] ?? "")}
              saved={saved[param.key]}
              compareToDefault={compareToDefault}
              error={errors[param.key]}
              onChange={(text) => onChange({ ...draft, [param.key]: text })}
            />
          );
        })}
      </div>

      {Number.isFinite(percent) && (
        <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs leading-relaxed text-muted-foreground">
          Com {cashLabel}, cada compra usa até{" "}
          <b className="font-mono text-foreground">{displayMoney(cashShare(cash, percent))}</b> ({percent}% de{" "}
          <span className="font-mono">{displayMoney(cash)}</span>).
        </p>
      )}
    </div>
  );
}

type NumberFieldProps = {
  param: StrategyParam;
  text: string;
  saved: ParamValues[string];
  compareToDefault: boolean;
  error: string | undefined;
  onChange: (text: string) => void;
};

function NumberField({ param, text, saved, compareToDefault, error, onChange }: NumberFieldProps) {
  const unit = param.unit === "%" ? "%" : "";
  const savedNumber = typeof saved === "number" ? saved : null;
  const changed = compareToDefault && text.trim() !== String(param.default);
  const description =
    !compareToDefault && savedNumber !== null && text.trim() !== String(savedNumber)
      ? `Era ${savedNumber}${unit} · de ${param.min}${unit} a ${param.max}${unit}`
      : rangeHint(param);
  const id = `strategy-param-${param.key}`;

  return (
    <Field data-invalid={!!error}>
      <div className="flex items-center gap-1.5">
        <FieldLabel htmlFor={id}>{param.label}</FieldLabel>
        <InfoHint label={`Como ${param.label} muda a estratégia`}>{param.hint}</InfoHint>
      </div>
      <InputGroup size="lg" tone={changed ? "changed" : "default"}>
        <InputGroupInput
          id={id}
          numeric
          inputMode="numeric"
          value={text}
          aria-invalid={!!error}
          onChange={(event) => onChange(event.target.value.replace(/\D/g, ""))}
        />
        {param.unit && <InputGroupAddon align="inline-end">{param.unit}</InputGroupAddon>}
      </InputGroup>
      {error && <FieldError>{error}</FieldError>}
      <FieldDescription>
        {description}
        {changed && (
          <>
            {" · "}
            <b className="font-semibold text-info">Mudou</b>
          </>
        )}
      </FieldDescription>
    </Field>
  );
}

type AssetFieldProps = {
  param: StrategyParam;
  ticker: string;
  error: string | undefined;
  options: string[];
  onChange: (ticker: string) => void;
};

function AssetField({ param, ticker, error, options, onChange }: AssetFieldProps) {
  return (
    <Field data-invalid={!!error}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <FieldLabel>{param.label}</FieldLabel>
          <InfoHint label={`Como ${param.label} muda a estratégia`}>{param.hint}</InfoHint>
        </div>
        <TickerPicker single options={options} selected={[ticker]} onChange={([next]) => onChange(next)} />
      </div>
      <div className="flex flex-wrap gap-1.5">
        <Badge variant="secondary" size="tag" numeric>
          {ticker}
        </Badge>
      </div>
      {error && <FieldError>{error}</FieldError>}
      <FieldDescription>{rangeHint(param)}</FieldDescription>
    </Field>
  );
}

type TickersFieldProps = {
  param: StrategyParam;
  tickers: string[];
  error: string | undefined;
  options: string[];
  onChange: (tickers: string[]) => void;
};

function TickersField({ param, tickers, error, options, onChange }: TickersFieldProps) {
  const rest = tickers.length - VISIBLE_TICKERS;

  return (
    <Field data-invalid={!!error}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <FieldLabel>{param.label}</FieldLabel>
          <InfoHint label={`Como ${param.label} muda a estratégia`}>{param.hint}</InfoHint>
        </div>
        <TickerPicker options={options} selected={tickers} onChange={onChange} />
      </div>
      <div className="flex flex-wrap gap-1.5">
        {tickers.slice(0, VISIBLE_TICKERS).map((ticker) => (
          <Badge key={ticker} variant="secondary" size="tag" numeric>
            {ticker}
          </Badge>
        ))}
        {rest > 0 && (
          <Badge variant="outline" size="tag" numeric>
            +{rest}
          </Badge>
        )}
      </div>
      {error && <FieldError>{error}</FieldError>}
      <FieldDescription>Padrão: as 10 ações mais negociadas</FieldDescription>
    </Field>
  );
}
