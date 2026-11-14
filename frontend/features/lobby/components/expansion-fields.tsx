import { Fragment } from "react";
import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { Lock, TriangleAlert } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { DateField } from "@/shared/components/date-field";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { InfoHint } from "@/shared/components/info-hint";
import { Input } from "@/shared/components/ui/input";
import { Switch } from "@/shared/components/ui/switch";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { EXPANSIONS } from "@/shared/lib/expansions";
import { isIsoDate } from "@/shared/lib/utils/date-field";
import { displayIsoDate } from "@/shared/lib/utils/display";
import { cn } from "@/shared/lib/utils";
import {
  campaignOpening,
  COMPUTER_DIFFICULTIES,
  defaultFirstElection,
  difficultyExample,
  GOVERNMENT_MIN_YEARS,
  INITIAL_ACCOUNTS,
  initialAccountDescription,
  initialAccountExample,
  SELIC_CONTROLS,
  spansYears,
  wholeYears,
} from "../lib/government-rules";
import { useInitialAccount } from "../hooks/queries/useInitialAccount";
import type { SimulationFormValues } from "../lib/simulation-form";
import { ExpansionIntro } from "./expansion-intro";
import { FundsCard } from "./funds-card";

const GOVERNMENT = EXPANSIONS.government;

type ExpansionFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  /** Sem edição: convidado ou regras de uma partida salva */
  readOnly: boolean;
  /** Regras de uma partida que já começou: as expansões ficam como foram gravadas */
  locked: boolean;
};

/** A aba "Expansões" das regras: um cartão por expansão, com as chaves e as regras de cada uma. */
export function ExpansionFields({ form, readOnly, locked }: ExpansionFieldsProps) {
  const [enabled, startDate, endDate, firstElection, difficulty, gameType, fundsEnabled] = useWatch({
    control: form.control,
    name: [
      "governmentEnabled",
      "startDate",
      "endDate",
      "firstElection",
      "computerDifficulty",
      "gameType",
      "fundsEnabled",
    ],
  });
  const longEnough = spansYears(startDate, endDate, GOVERNMENT_MIN_YEARS);
  const initialAccount = useInitialAccount(startDate, { enabled: enabled && isIsoDate(startDate) });
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
      {/* Expansões da partida já começada */}
      {locked && (
        <div className="grid gap-3 rounded-xl border bg-card p-4">
          <span className="flex items-center gap-1.5 text-xs font-semibold tracking-wide text-sidebar-muted uppercase">
            <Lock className="size-3" />
            Expansões
          </span>
          <span className="flex flex-wrap gap-1.5">
            {enabled && (
              <Badge variant="outline">
                <ExpansionEmblem expansion="government" size="xs" />
                {GOVERNMENT.label}
              </Badge>
            )}
            {fundsEnabled && (
              <Badge variant="outline">
                <ExpansionEmblem expansion="funds" size="xs" />
                {EXPANSIONS.funds.label}
              </Badge>
            )}
            {!enabled && !fundsEnabled && (
              <span className="text-sm text-muted-foreground">Nenhuma expansão ligada</span>
            )}
          </span>
          <span className="text-xs text-muted-foreground">
            A partida já começou: as expansões ficam como estão até o fim, porque a gestora e o governo guardam
            histórico desde o primeiro dia.
          </span>
        </div>
      )}

      <div className={cn("self-start overflow-hidden rounded-xl border bg-card", enabled && "border-2 border-primary")}>
        <ExpansionIntro expansion="government" enabled={enabled}>
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
        </ExpansionIntro>

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
                          Os 3 partidos do computador (UPR, MNV e ACI) sempre estão na disputa, ao lado dos de
                          jogadores. Cada um recebe o fundo público do mês e gasta uma verba medida sobre ele.
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

            {/* Conta inicial do governo */}
            <Controller
              control={form.control}
              name="initialAccount"
              render={({ field }) => (
                <div className="grid gap-2 rounded-lg border border-info-border bg-info-soft/40 p-3">
                  <span className="inline-flex items-center gap-1 text-sm font-medium">
                    Conta inicial do governo
                    <InfoHint label="O que é a conta inicial">
                      <div className="space-y-1 text-left">
                        <p>
                          A conta do país tem a dívida (o que o governo já deve) e o resultado primário (receita menos
                          despesa, sem contar os juros da dívida). Aqui você escolhe com que resultado primário a
                          partida começa.
                        </p>
                        <p>
                          Ex.: um déficit primário de 1,7% do PIB quer dizer que o governo gasta 1,7% do PIB a mais do
                          que arrecada, por ano, fora os juros.
                        </p>
                        <p>
                          Jogável começa com receita igual ao gasto, e o déficit só aparece se o presidente mexer nos
                          impostos. Realista começa com o déficit que o Brasil tinha no ano de início.
                        </p>
                      </div>
                    </InfoHint>
                  </span>
                  <ToggleGroup
                    variant="segmented"
                    aria-label="Conta inicial do governo"
                    value={[field.value]}
                    onValueChange={(values) => values[0] && field.onChange(values[0])}
                    disabled={readOnly}
                    className="w-full"
                  >
                    {INITIAL_ACCOUNTS.map((option) => (
                      <ToggleGroupItem key={option.value} value={option.value} className="flex-1">
                        {option.label}
                      </ToggleGroupItem>
                    ))}
                  </ToggleGroup>
                  <span className="text-xs leading-normal text-muted-foreground">
                    {initialAccountDescription(field.value, initialAccount.data)}
                  </span>
                  {initialAccount.data && (
                    <span className="rounded-md bg-card px-2.5 py-1.5 text-xs text-muted-foreground">
                      Começa em {initialAccount.data.year} com:{" "}
                      {initialAccountExample(field.value, initialAccount.data).figures.map((figure, index) => (
                        <Fragment key={figure}>
                          {index > 0 && " · "}
                          <b className="font-mono text-foreground">{figure}</b>
                        </Fragment>
                      ))}
                      . {initialAccountExample(field.value, initialAccount.data).premium}
                    </span>
                  )}
                  <span className="text-xs text-faint-foreground">
                    Dívida e déficit saem dos dados anuais do Banco Central; no futuro gerado, vale o último ano com
                    dado.
                  </span>
                </div>
              )}
            />

            {/* Quem decide a SELIC */}
            <Controller
              control={form.control}
              name="selicControl"
              render={({ field }) => {
                const option = SELIC_CONTROLS[field.value];
                return (
                  <div className="grid gap-2 rounded-lg border border-info-border bg-info-soft/40 p-3">
                    <span className="inline-flex items-center gap-1 text-sm font-medium">
                      Quem decide a SELIC
                      <InfoHint label="O que é decidir a SELIC">
                        <div className="space-y-1 text-left">
                          <p>
                            A SELIC é o juro básico do país. Juro real é a SELIC menos a inflação dos últimos 12 meses:
                            o quanto o dinheiro rende de verdade.
                          </p>
                          <p>Ex.: SELIC de 10% com inflação de 4% dá juro real de 6%.</p>
                          <p>
                            Juro real alto segura a inflação e esfria o crédito; baixo aquece a economia e puxa a
                            inflação meses depois. Os grupos de eleitores ficam satisfeitos com o juro real entre 2% e
                            7%.
                          </p>
                        </div>
                      </InfoHint>
                    </span>
                    <ToggleGroup
                      variant="segmented"
                      aria-label="Quem decide a SELIC"
                      value={[field.value]}
                      onValueChange={(values) => values[0] && field.onChange(values[0])}
                      disabled={readOnly}
                      className="w-full"
                    >
                      {(["AUTONOMOUS", "GOVERNMENT"] as const).map((value) => (
                        <ToggleGroupItem key={value} value={value} className="flex-1">
                          {SELIC_CONTROLS[value].label}
                        </ToggleGroupItem>
                      ))}
                    </ToggleGroup>
                    <span className="text-xs leading-normal text-muted-foreground">{option.description}</span>
                    <span className="rounded-md bg-card px-2.5 py-1.5 text-xs text-muted-foreground">
                      {option.example}
                    </span>
                  </div>
                );
              }}
            />
          </div>
        )}
      </div>

      <FundsCard form={form} readOnly={readOnly} />
    </div>
  );
}
