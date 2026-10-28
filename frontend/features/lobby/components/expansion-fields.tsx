import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { DateField } from "@/shared/components/date-field";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { InfoHint } from "@/shared/components/info-hint";
import { Input } from "@/shared/components/ui/input";
import { Switch } from "@/shared/components/ui/switch";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { EXPANSIONS } from "@/shared/lib/expansions";
import { displayIsoDate } from "@/shared/lib/utils/display";
import { cn } from "@/shared/lib/utils";
import {
  campaignOpening,
  COMPUTER_DIFFICULTIES,
  defaultFirstElection,
  difficultyExample,
  GOVERNMENT_MIN_YEARS,
  spansYears,
  wholeYears,
} from "../lib/government-rules";
import type { SimulationFormValues } from "./lobby-match";

const GOVERNMENT = EXPANSIONS.government;

type ExpansionFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  /** Sem edição: convidado ou regras de uma partida salva */
  readOnly: boolean;
};

/** A aba "Expansões" das regras: um cartão por expansão, com as chaves e as regras de cada uma. */
export function ExpansionFields({ form, readOnly }: ExpansionFieldsProps) {
  const [enabled, startDate, endDate, firstElection, difficulty, gameType] = useWatch({
    control: form.control,
    name: ["governmentEnabled", "startDate", "endDate", "firstElection", "computerDifficulty", "gameType"],
  });
  const longEnough = spansYears(startDate, endDate, GOVERNMENT_MIN_YEARS);
  const opening = campaignOpening(startDate, firstElection);

  // Ligar sugere a data da primeira eleição; desligar tira a vitória política, que depende da expansão
  const toggle = (checked: boolean, onChange: (checked: boolean) => void) => {
    onChange(checked);
    if (checked && !form.getValues("firstElection")) {
      form.setValue("firstElection", defaultFirstElection(startDate, endDate), { shouldValidate: true });
    }
    if (!checked && gameType === "POLITICAL") form.setValue("gameType", "CLASSIC", { shouldValidate: true });
    void form.trigger();
  };

  return (
    <div className="grid items-start gap-4">
      <div className={cn("self-start overflow-hidden rounded-xl border bg-card", enabled && "border-2 border-primary")}>
        {/* Faixa do cartão */}
        <div className={cn("relative flex h-28 items-end px-4 py-3.5", GOVERNMENT.bannerClass)}>
          <span className="inline-flex size-14 items-center justify-center rounded-[14px] bg-white/15 text-white ring-1 ring-white/25 ring-inset">
            <GOVERNMENT.icon className="size-[30px]" />
          </span>
          <span className="ml-3 grid text-white">
            <b className="text-xl">{GOVERNMENT.label}</b>
            <span className="text-xs opacity-80">Expansão</span>
          </span>
        </div>

        {/* O que a expansão traz e a chave */}
        <div className="grid gap-2.5 px-4 py-3.5">
          <span className="text-[13px]">{GOVERNMENT.description}</span>
          <ul className="list-disc pl-[18px] text-xs leading-normal text-muted-foreground">
            {GOVERNMENT.highlights.map((highlight) => (
              <li key={highlight} className="mb-1">
                {highlight}
              </li>
            ))}
          </ul>
          <div className="flex items-center justify-between gap-2.5">
            <Badge variant={enabled ? "info" : "secondary"}>{enabled ? "Ligada nesta partida" : "Desligada"}</Badge>
            <Controller
              control={form.control}
              name="governmentEnabled"
              render={({ field }) => (
                <Switch
                  aria-label={`Ligar ${GOVERNMENT.label}`}
                  checked={field.value}
                  disabled={readOnly || (!longEnough && !field.value)}
                  onCheckedChange={(checked) => toggle(checked, field.onChange)}
                />
              )}
            />
          </div>
        </div>

        {/* Partida curta demais */}
        {!longEnough && (
          <div className="px-4 pb-4">
            <Alert variant="destructive">
              <TriangleAlert />
              <AlertTitle>
                A partida tem {wholeYears(startDate, endDate)} anos; o {GOVERNMENT.label} pede {GOVERNMENT_MIN_YEARS}
              </AlertTitle>
              <AlertDescription>
                O tempo de uma campanha e um mandato: a candidatura abre um ano antes da eleição e o mandato dura 4.
              </AlertDescription>
            </Alert>
          </div>
        )}

        {/* Regras da expansão */}
        {enabled && (
          <div className="grid gap-3.5 border-t px-4 py-3.5">
            <div className="grid gap-3 lg:grid-cols-2">
              <Controller
                control={form.control}
                name="firstElection"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="rules-firstElection">Primeira eleição</FieldLabel>
                    <DateField
                      id="rules-firstElection"
                      value={field.value}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                      invalid={fieldState.invalid}
                      disabled={readOnly}
                      period={{ start: startDate, end: endDate }}
                    />
                    <FieldDescription>
                      {opening
                        ? `A candidatura abre um ano antes, em ${displayIsoDate(opening)}.`
                        : "A candidatura abre um ano antes."}
                    </FieldDescription>
                    <FieldError errors={[fieldState.error]} />
                  </Field>
                )}
              />
              <Field>
                <FieldLabel htmlFor="rules-term">Mandato</FieldLabel>
                <Input id="rules-term" value="4 anos" disabled readOnly />
                <FieldDescription>Eleição de novo a cada 4 anos.</FieldDescription>
              </Field>
            </div>

            <Controller
              control={form.control}
              name="computerDifficulty"
              render={({ field }) => (
                <Field>
                  <FieldLabel>
                    Dificuldade do computador
                    <InfoHint label="Como funciona a dificuldade">
                      <div className="space-y-1 text-left">
                        <p>
                          O computador completa a disputa com partidos próprios sempre que há menos de 3 partidos de
                          jogadores. Cada um gasta uma verba por mês, medida sobre a média dos partidos de jogadores.
                        </p>
                        <p>{difficultyExample(field.value)}</p>
                        <p>
                          Mais verba, mais intenção de voto para o computador: a eleição fica mais difícil de ganhar.
                        </p>
                      </div>
                    </InfoHint>
                  </FieldLabel>
                  <ToggleGroup
                    variant="segmented"
                    aria-label="Dificuldade do computador"
                    value={[field.value]}
                    onValueChange={(values) => values[0] && field.onChange(values[0])}
                    disabled={readOnly}
                    className="w-full"
                  >
                    {COMPUTER_DIFFICULTIES.map((option) => (
                      <ToggleGroupItem key={option.value} value={option.value} className="flex-1">
                        {option.label}
                      </ToggleGroupItem>
                    ))}
                  </ToggleGroup>
                  <FieldDescription>{difficultyExample(difficulty)}</FieldDescription>
                </Field>
              )}
            />

            <Controller
              control={form.control}
              name="pollMargin"
              render={({ field }) => (
                <div
                  className={cn(
                    "grid gap-2 rounded-lg border p-3",
                    field.value ? "border-info-border bg-info-soft/40" : "bg-subtle",
                  )}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="inline-flex items-center gap-1 text-sm font-medium">
                      Margem de erro na pesquisa
                      <InfoHint label="O que é a margem de erro">
                        <div className="space-y-1 text-left">
                          <p>
                            A pesquisa ouve uma amostra, não o eleitorado inteiro: cada número sai com um erro sorteado
                            dentro da margem. Grupo menor tem amostra menor e margem maior.
                          </p>
                          <p>Ex.: 30% com margem de 3 pontos quer dizer que o real está entre 27% e 33%.</p>
                          <p>
                            Quando as faixas de dois partidos se cobrem, é empate técnico: a pesquisa não diz quem está
                            na frente.
                          </p>
                        </div>
                      </InfoHint>
                    </span>
                    <Switch
                      aria-label="Margem de erro na pesquisa"
                      checked={field.value}
                      disabled={readOnly}
                      onCheckedChange={field.onChange}
                    />
                  </div>
                  <span className="text-xs leading-normal text-muted-foreground">
                    {field.value
                      ? "A pesquisa mostra cada número com a faixa onde o real está: “30%, com margem de 3 pontos” é algo entre 27% e 33%. Nos grupos menores a margem cresce: ±11 nos investidores. Sorteada pela semente da partida."
                      : "A pesquisa mostra o número exato de cada partido, no total e em cada grupo. Bom para aprender o modelo; tira a incerteza da campanha."}
                  </span>
                  <span className="rounded-md bg-card px-2.5 py-1.5 text-xs text-muted-foreground">
                    {field.value ? (
                      <>
                        Exemplo com a margem: <b className="font-mono text-foreground">PRL 30% ±3</b> e{" "}
                        <b className="font-mono text-foreground">FDS 32% ±3</b> aparecem como empate técnico.
                      </>
                    ) : (
                      <>
                        Exemplo sem a margem: <b className="font-mono text-foreground">PRL 30,4%</b> e{" "}
                        <b className="font-mono text-foreground">FDS 31,8%</b>, os valores do modelo.
                      </>
                    )}
                  </span>
                </div>
              )}
            />
          </div>
        )}
      </div>
    </div>
  );
}
