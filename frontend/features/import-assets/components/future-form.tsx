import { useMemo, useState } from "react";
import { z } from "zod";
import { Controller, useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useDebounce } from "use-debounce";
import { toast } from "sonner";
import {
  CalendarDays,
  CircleX,
  Dices,
  ExternalLink,
  Sparkles,
  TriangleAlert,
} from "lucide-react";
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { DateField } from "@/shared/components/date-field";
import {
  DialogBody,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import {
  Field,
  FieldDescription,
  FieldError,
  FieldLabel,
} from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Progress } from "@/shared/components/ui/progress";
import { Spinner } from "@/shared/components/ui/spinner";
import {
  ToggleGroup,
  ToggleGroupItem,
} from "@/shared/components/ui/toggle-group";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { cn } from "@/shared/lib/utils";
import { dateFieldError } from "@/shared/lib/utils/date-field";
import {
  displayDate,
  displayNumber,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import type {
  FutureParams,
  FuturePreviewRequest,
  FutureRecordingProgressEvent,
  GeneratedFuture,
  SeriesCoverage,
} from "@/types";
import { useCancelFutureRecording } from "../hooks/mutations/useCancelFutureRecording";
import { useDownloadIndicators } from "../hooks/mutations/useDownloadIndicators";
import { useRecordFuture } from "../hooks/mutations/useRecordFuture";
import { useFuturePreview } from "../hooks/queries/useFuturePreview";
import {
  displayShock,
  displayTemperature,
  drawSeed,
  endOfYearAhead,
  FIRST_YEAR_VOLATILITY,
  FUTURE_DOCS_URL,
  INFLATION_SHOCK,
  INFLATION_SHOCK_MARKS,
  inflationShockReading,
  regimeToStartChoice,
  REGIME_NAMES,
  START_CHOICES,
  startChoiceToRegime,
  TEMPERATURE,
  TEMPERATURE_MARKS,
  temperatureReading,
  withMinus,
} from "../lib/future-readings";
import {
  InflationShockHint,
  StartRegimeHint,
  TemperatureHint,
} from "./future-hints";
import { FuturePreviewPanel } from "./future-preview-panel";
import { MarkedSlider } from "./marked-slider";

const SHORTCUT_YEARS = [1, 2, 5, 10];
const PREVIEW_TICKERS = 3;
const SEED_DIGITS = 15;

const formatIso = (iso: string) => displayDate(parseLocalDate(iso));

const futureFormSchema = (lastRealIso: string | null) =>
  z.object({
    // O campo guarda ISO quando a data está completa e real; o texto em digitação é recusado aqui
    until: z
      .string()
      .min(1, "Escolha até quando gerar")
      .superRefine((value, ctx) => {
        const message = dateFieldError(value);
        if (message) {
          ctx.addIssue({ code: "custom", message });
          return;
        }
        if (lastRealIso && value <= lastRealIso) {
          ctx.addIssue({
            code: "custom",
            message: `Escolha uma data depois de ${formatIso(lastRealIso)}, o último dado real do Ibovespa.`,
          });
        }
      }),
    seed: z
      .string()
      .regex(
        new RegExp(`^\\d{1,${SEED_DIGITS}}$`),
        `A semente é um número inteiro de até ${SEED_DIGITS} dígitos`,
      ),
    temperature: z.number().min(TEMPERATURE.min).max(TEMPERATURE.max),
    startRegime: z.enum(["TODAY", "CALM", "NORMAL", "AGITATED"]),
    inflationShock: z
      .number()
      .min(INFLATION_SHOCK.min)
      .max(INFLATION_SHOCK.max),
  });

type FutureFormValues = z.infer<ReturnType<typeof futureFormSchema>>;

function initialValues(
  future: GeneratedFuture | null,
  redrawSeed: boolean,
): FutureFormValues {
  if (!future) {
    return {
      until: endOfYearAhead(5),
      seed: drawSeed(),
      temperature: TEMPERATURE.default,
      startRegime: "TODAY",
      inflationShock: INFLATION_SHOCK.default,
    };
  }
  return {
    until: future.until,
    seed: redrawSeed ? drawSeed() : String(future.seed),
    temperature: future.temperature,
    startRegime: regimeToStartChoice(future.start_regime),
    inflationShock: future.inflation_shock,
  };
}

const toParams = (values: FutureFormValues): FutureParams => ({
  until: values.until,
  seed: Number(values.seed),
  // O slider anda de 0,1 em 0,1: o arredondamento tira o ruído de ponto flutuante
  temperature: Math.round(values.temperature * 10) / 10,
  start_regime: startChoiceToRegime(values.startRegime),
  inflation_shock: values.inflationShock,
});

const countLabel = (count: number, one: string, many: string) =>
  `${count} ${count === 1 ? one : many}`;

type FutureFormProps = {
  /** O futuro gravado, já resolvido; nulo quando a base ainda não tem um */
  future: GeneratedFuture | null;
  coverage: SeriesCoverage[];
  /** Abre com uma semente nova em vez da gravada */
  redrawSeed: boolean;
  onClose: () => void;
  /** Avisa o diálogo de que a gravação começou ou terminou: enquanto grava, ele não fecha */
  onRecordingChange: (recording: boolean) => void;
};

/** Controles à esquerda, prévia à direita e o rodapé que grava. */
export function FutureForm({
  future,
  coverage,
  redrawSeed,
  onClose,
  onRecordingChange,
}: FutureFormProps) {
  const ibovRealEnd = coverage.find((s) => s.key === "IBOV")?.real_end ?? null;
  const stocks = coverage.filter((s) => s.kind === "STOCK");
  const tickers = stocks.slice(0, PREVIEW_TICKERS).map((s) => s.key);

  const schema = useMemo(() => futureFormSchema(ibovRealEnd), [ibovRealEnd]);
  const [defaults] = useState(() => initialValues(future, redrawSeed));
  const form = useForm<FutureFormValues>({
    resolver: zodResolver(schema),
    mode: "onChange",
    defaultValues: defaults,
  });
  const values = useWatch({ control: form.control }) as FutureFormValues;

  // Ativo mostrado ao lado do Ibovespa na prévia
  const [ticker, setTicker] = useState<string | null>(null);
  const [progress, setProgress] = useState<FutureRecordingProgressEvent | null>(
    null,
  );

  const record = useRecordFuture();
  const cancel = useCancelFutureRecording();
  const downloadIndicators = useDownloadIndicators();
  const recording = record.isPending;
  useRealtime("future_recording_progress", setProgress, recording);

  // A prévia espera o slider parar; só controles válidos viram pedido
  const [settled] = useDebounce(values, 250);
  const parsed = schema.safeParse(settled);
  const request: FuturePreviewRequest | null = parsed.success
    ? { ...toParams(parsed.data), ticker }
    : null;
  const previewQuery = useFuturePreview(request, {
    enabled: ibovRealEnd !== null && !recording,
  });
  const preview = previewQuery.data;

  const assets = preview?.assets ?? stocks.length;
  const indicators = preview?.indicators ?? coverage.length - stocks.length;
  const seriesCount = assets + indicators;

  const submit = (valid: FutureFormValues) => {
    const params = toParams(valid);
    setProgress(null);
    onRecordingChange(true);
    record.mutate(params, {
      onSuccess: () => {
        toast.success(`Futuro gravado até ${formatIso(params.until)}`, {
          description: `${countLabel(assets, "ativo", "ativos")} e ${countLabel(indicators, "indicador", "indicadores")}`,
        });
        onClose();
      },
      onError: (err) => {
        // Cancelar a pedido da pessoa não é falha: a base ficou como estava
        if (err.status === 409) {
          toast(err.message);
          record.reset();
        }
      },
      onSettled: () => onRecordingChange(false),
    });
  };

  const regime = preview?.current_regime;
  const otherRegimes = (["AGITATED", "NORMAL", "CALM"] as const).filter(
    (r) => r !== regime,
  );
  const shockReading = inflationShockReading(values.inflationShock);
  const temperature = temperatureReading(values.temperature);
  const recordFailed = record.isError && record.error.status !== 409;

  const footerSummary = () => {
    if (recording) return "Os controles voltam quando a gravação acabar";
    if (future) return `Troca o futuro de ${seriesCount} séries`;
    return (
      <>
        Grava{" "}
        <b className="font-semibold text-foreground">
          {countLabel(assets, "ativo", "ativos")} e{" "}
          {countLabel(indicators, "indicador", "indicadores")}
        </b>
        {parsed.success && preview && (
          <>
            {" "}
            até{" "}
            <span className="font-mono">{formatIso(parsed.data.until)}</span> ·
            cerca de {displayNumber(preview.trading_days, 0)} pregões por série
          </>
        )}
      </>
    );
  };

  const submitLabel = () => {
    if (recording) return "Gravando…";
    if (recordFailed) return "Tentar de novo";
    return future ? "Trocar e gravar" : "Gerar e gravar";
  };

  return (
    <form
      className="flex min-h-0 flex-col gap-4"
      onSubmit={(event) => void form.handleSubmit(submit)(event)}
    >
      {/* Cabeçalho */}
      <DialogHeader variant="divided">
        <div className="flex items-center gap-2">
          <Sparkles className="size-4.5 text-warning" />
          <DialogTitle>Gerar dados futuros</DialogTitle>
        </div>
        <DialogDescription className="max-w-3xl">
          Um futuro plausível montado com trechos reais da bolsa desde 2000.
          Fica gravado como dado gerado, e as partidas o leem como leem o
          histórico.{" "}
          <a
            href={FUTURE_DOCS_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 font-medium"
          >
            Como o futuro é gerado
            <ExternalLink className="size-3" />
          </a>
        </DialogDescription>
      </DialogHeader>

      <DialogBody>
        {/* Avisos */}
        {future && (
          <Alert variant="warning" role="status">
            <TriangleAlert />
            <p>
              <b>Já há um futuro gerado até {formatIso(future.until)}.</b>{" "}
              Gravar troca esse futuro pelo novo em todas as séries.
            </p>
            {future.saved_simulations_on_future > 0 && (
              <p className="text-muted-foreground">
                {future.saved_simulations_on_future === 1
                  ? "1 partida salva já jogou dias desse futuro: ela guarda a própria cópia e continua igual."
                  : `${future.saved_simulations_on_future} partidas salvas já jogaram dias desse futuro: cada uma guarda a própria cópia e continua igual.`}
              </p>
            )}
          </Alert>
        )}
        {recordFailed && (
          <Alert variant="destructive">
            <CircleX />
            <AlertTitle>Não deu pra gravar o futuro.</AlertTitle>
            <AlertDescription>
              Nada mudou na base: o futuro anterior, se havia, continua lá.
              <span className="mt-1 block font-mono text-[11px]">
                {record.error.message}
              </span>
            </AlertDescription>
          </Alert>
        )}

        {ibovRealEnd === null ? (
          /* Sem Ibovespa na base */
          <Empty>
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <CalendarDays />
              </EmptyMedia>
              <EmptyTitle>Falta o Ibovespa na base</EmptyTitle>
              <EmptyDescription>
                Cada trecho do futuro é sorteado pelo clima do Ibovespa naquele
                trimestre. Baixe os indicadores e volte aqui.
              </EmptyDescription>
            </EmptyHeader>
            <EmptyContent className="flex-row justify-center">
              <Button
                type="button"
                disabled={downloadIndicators.isPending}
                onClick={() => downloadIndicators.mutate()}
              >
                {downloadIndicators.isPending && <Spinner />}
                Baixar indicadores
              </Button>
            </EmptyContent>
          </Empty>
        ) : (
          <div className="grid gap-7 lg:grid-cols-[400px_minmax(0,1fr)]">
            {/* Controles */}
            <div
              className={cn(
                "grid content-start gap-4.5 transition-opacity",
                recording && "opacity-55",
              )}
            >
              <Controller
                name="until"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="future-until">Até quando</FieldLabel>
                    <DateField
                      id="future-until"
                      value={field.value}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                      invalid={fieldState.invalid}
                      disabled={recording}
                    />
                    <div className="flex flex-wrap gap-1.5">
                      {SHORTCUT_YEARS.map((years) => (
                        <Button
                          key={years}
                          type="button"
                          size="xs"
                          variant={
                            field.value === endOfYearAhead(years)
                              ? "info"
                              : "outline"
                          }
                          disabled={recording}
                          onClick={() => field.onChange(endOfYearAhead(years))}
                        >
                          +{years} {years === 1 ? "ano" : "anos"}
                        </Button>
                      ))}
                    </div>
                    {fieldState.invalid ? (
                      <FieldError errors={[fieldState.error]} />
                    ) : (
                      preview && (
                        <FieldDescription>
                          Cada série continua do dia útil seguinte ao seu último
                          dado real: Ibovespa em{" "}
                          <span className="font-mono">
                            {formatIso(preview.ibov_start.start)}
                          </span>
                          {preview.laggard_start && (
                            <>
                              , {preview.laggard_start.key} em{" "}
                              <span className="font-mono">
                                {formatIso(preview.laggard_start.start)}
                              </span>
                            </>
                          )}
                          .
                        </FieldDescription>
                      )
                    )}
                  </Field>
                )}
              />

              <Controller
                name="seed"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="future-seed">Semente</FieldLabel>
                    <div className="flex gap-2">
                      <Input
                        id="future-seed"
                        numeric
                        inputMode="numeric"
                        autoComplete="off"
                        value={field.value}
                        aria-invalid={fieldState.invalid}
                        disabled={recording}
                        onChange={(event) =>
                          field.onChange(event.target.value.replace(/\D/g, ""))
                        }
                        onBlur={field.onBlur}
                      />
                      <Button
                        type="button"
                        variant="outline"
                        disabled={recording}
                        onClick={() => field.onChange(drawSeed())}
                      >
                        <Dices />
                        Sortear
                      </Button>
                    </div>
                    {fieldState.invalid ? (
                      <FieldError errors={[fieldState.error]} />
                    ) : (
                      <FieldDescription>
                        Mesma semente e mesmos controles geram o mesmo futuro.
                      </FieldDescription>
                    )}
                  </Field>
                )}
              />

              <Controller
                name="temperature"
                control={form.control}
                render={({ field }) => (
                  <Field>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        <FieldLabel>Temperatura</FieldLabel>
                        <TemperatureHint />
                      </div>
                      <Badge variant="info" numeric>
                        {displayTemperature(field.value)}
                      </Badge>
                    </div>
                    <MarkedSlider
                      aria-label="Temperatura"
                      value={field.value}
                      onValueChange={field.onChange}
                      min={TEMPERATURE.min}
                      max={TEMPERATURE.max}
                      step={TEMPERATURE.step}
                      marks={TEMPERATURE_MARKS}
                      disabled={recording}
                    />
                    <Alert
                      variant={temperature.extreme ? "warning" : "info"}
                      role="status"
                    >
                      <p>
                        <b>{temperature.headline}</b> {temperature.subject}{" "}
                        <b>{temperature.volatility}%</b>, e em{" "}
                        <b>{temperature.crashYears} de 100</b>{" "}
                        {temperature.closing}{" "}
                        <span className="text-muted-foreground">
                          Medido em 100 futuros de 5 anos.
                        </span>
                      </p>
                    </Alert>
                  </Field>
                )}
              />

              <Controller
                name="startRegime"
                control={form.control}
                render={({ field }) => (
                  <Field>
                    <div className="flex items-center gap-1.5">
                      <FieldLabel>Começar em</FieldLabel>
                      <StartRegimeHint />
                    </div>
                    <ToggleGroup
                      variant="segmented"
                      className="w-full"
                      aria-label="Começar em"
                      value={[field.value]}
                      disabled={recording}
                      onValueChange={(next) =>
                        next[0] && field.onChange(next[0])
                      }
                    >
                      <ToggleGroupItem value="TODAY" className="flex-1">
                        Hoje{regime && ` · ${REGIME_NAMES[regime]}`}
                      </ToggleGroupItem>
                      {START_CHOICES.map((choice) => (
                        <ToggleGroupItem
                          key={choice.value}
                          value={choice.value}
                          className="flex-1"
                        >
                          {choice.label}
                        </ToggleGroupItem>
                      ))}
                    </ToggleGroup>
                    <Alert variant="info" role="status">
                      <p>
                        O clima do primeiro trimestre.
                        {regime && (
                          <>
                            {" "}
                            Hoje o mercado está <b>{REGIME_NAMES[regime]}</b>: o
                            1º ano oscila uns{" "}
                            <b>{FIRST_YEAR_VOLATILITY[regime]}%</b> (começando
                            em{" "}
                            {otherRegimes.map((other, index) => (
                              <span key={other}>
                                {index > 0 && "; em "}
                                {REGIME_NAMES[other]},{" "}
                                {FIRST_YEAR_VOLATILITY[other]}%
                              </span>
                            ))}
                            ).
                          </>
                        )}
                      </p>
                    </Alert>
                  </Field>
                )}
              />

              <Controller
                name="inflationShock"
                control={form.control}
                render={({ field }) => (
                  <Field>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        <FieldLabel>Choque de inflação</FieldLabel>
                        <InflationShockHint />
                      </div>
                      <Badge
                        variant={field.value === 0 ? "info" : "warning"}
                        numeric
                      >
                        {displayShock(field.value)}
                      </Badge>
                    </div>
                    <MarkedSlider
                      aria-label="Choque de inflação"
                      value={field.value}
                      onValueChange={field.onChange}
                      min={INFLATION_SHOCK.min}
                      max={INFLATION_SHOCK.max}
                      step={INFLATION_SHOCK.step}
                      marks={INFLATION_SHOCK_MARKS}
                      disabled={recording}
                    />
                    <Alert
                      variant={field.value === 0 ? "info" : "warning"}
                      role="status"
                    >
                      {field.value === 0 ? (
                        <p>
                          <b>Sem choque.</b> A inflação fica no que já aconteceu
                          desde 2000: no pico, uns{" "}
                          <b>{shockReading.inflationPeak}%</b> em 12 meses, com
                          a SELIC a <b>{shockReading.selicPeak}%</b>.
                        </p>
                      ) : (
                        <p>
                          <b>{displayShock(field.value)}.</b> A inflação de 12
                          meses chega a uns <b>{shockReading.inflationPeak}%</b>{" "}
                          e a SELIC a <b>{shockReading.selicPeak}%</b>; a bolsa
                          cai uns{" "}
                          <b>
                            {withMinus(
                              String(Math.abs(shockReading.twoYearDrop)),
                            )}
                            %
                          </b>{" "}
                          em 2 anos.
                        </p>
                      )}
                    </Alert>
                  </Field>
                )}
              />
            </div>

            {/* Prévia */}
            <div
              className={cn(
                "min-w-0 lg:border-l lg:pl-7",
                recording && "opacity-55",
              )}
            >
              <FuturePreviewPanel
                query={previewQuery}
                tickers={tickers}
                ticker={ticker}
                onTickerChange={setTicker}
              />
            </div>
          </div>
        )}

        {/* Progresso da gravação */}
        {recording && (
          <div className="grid gap-1.5">
            <Progress
              size="sm"
              value={progress ? (progress.done / progress.total) * 100 : 0}
            />
            <span className="text-xs text-muted-foreground">
              {progress
                ? `Gravando ${progress.series} · ${progress.done} de ${progress.total} séries`
                : "Gravando…"}
            </span>
          </div>
        )}
      </DialogBody>

      {/* Rodapé */}
      <DialogFooter variant="divided">
        <span className="text-[13px] text-muted-foreground">
          {ibovRealEnd === null
            ? "Sem o Ibovespa não há o que gerar"
            : footerSummary()}
        </span>
        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            disabled={cancel.isPending}
            onClick={() => (recording ? cancel.mutate() : onClose())}
          >
            Cancelar
          </Button>
          <Button
            type="submit"
            disabled={
              recording ||
              ibovRealEnd === null ||
              !form.formState.isValid ||
              previewQuery.isError
            }
          >
            {recording && <Spinner />}
            {submitLabel()}
          </Button>
        </div>
      </DialogFooter>
    </form>
  );
}
