import { Controller, useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Check, CircleAlert, CircleDashed } from "lucide-react";
import { FundMark } from "@/shared/components/fund-mark";
import { InfoHint } from "@/shared/components/info-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { InputGroup, InputGroupAddon, InputGroupInput, InputGroupText } from "@/shared/components/ui/input-group";
import { displayRatePercent } from "@/shared/lib/financial-independence";
import { useSaveMyFund } from "../../hooks/mutations/useSaveMyFund";
import { useSetFundPreparation } from "../../hooks/mutations/useSetFundPreparation";
import { useAutosave } from "../../hooks/useAutosave";
import {
  cleanTickerLetters,
  FUND_NAME_MAX_LENGTH,
  fundFormSchema,
  type FundForm,
  fundFromForm,
  fundToForm,
  nameOwners,
  rivalFunds,
  tickerHint,
  tickerOf,
  type TickerHint,
} from "../../lib/fund-preparation";
import { FundConflictsAlert, FundRoomSection } from "./fund-room-section";
import { PreparationFooter } from "./preparation-footer";
import { PreparationSection } from "./preparation-section";
import type { FundModeProps } from "./fund-tab";

const TIMELINE = [
  {
    when: "1º dia",
    title: "Fundada, vazia",
    text: "Fechada, com 0 cotas e patrimônio de R$ 0,00. Nada sai do seu caixa sozinho.",
  },
  {
    when: "Quando quiser",
    title: "Levar da carteira",
    text: "Dinheiro, ações e títulos viram cotas de R$ 100,00, todas suas.",
  },
  {
    when: "Enquanto fechada",
    title: "Só você tem cotas",
    text: "Dá para levar mais da carteira até abrir a primeira oferta pública.",
  },
  {
    when: "Quando abrir",
    title: "Oferta pública",
    text: "A sala tem 5 pregões para comprar cotas; depois elas são negociadas na bolsa.",
  },
];

/** Fundar a minha gestora: nome e sigla à esquerda; prévia, taxas e as gestoras da sala à direita. */
export function FundFoundTab({
  preparations,
  saved,
  humans,
  assets,
  nickname,
  rules,
  savedSimulation,
  lead,
  locked,
  onClose,
}: FundModeProps) {
  const savedForm = fundToForm(saved);
  const form = useForm<FundForm>({
    resolver: zodResolver(fundFormSchema),
    values: savedForm,
    mode: "onChange",
    resetOptions: { keepDirtyValues: true },
  });
  const draft = useWatch({ control: form.control });
  const name = draft.name ?? "";
  const letters = draft.letters ?? "";
  const saveFund = useSaveMyFund();
  const prepare = useSetFundPreparation();
  const rivals = rivalFunds(preparations, nickname);
  const mine = preparations.funds.some((fund) => fund.nickname === nickname);

  // Grava nome e sigla no perfil e só depois a escolha da sala, que parte do perfil
  const identity = fundFormSchema.safeParse(draft);
  const identityChanged =
    !identity.success || identity.data.name !== savedForm.name || identity.data.letters !== savedForm.letters;
  const blank = name.trim() === "" && letters === "";
  const autosave = useAutosave({
    dirty: !locked && (!mine || identityChanged),
    incomplete: identity.success
      ? null
      : blank
        ? "Falta o nome e a sigla da gestora."
        : (identity.error.issues[0]?.message ?? "Falta completar a gestora."),
    signature: JSON.stringify(draft),
    save: async () => {
      if (!identity.success) return;
      await saveFund.mutateAsync(fundFromForm(identity.data));
      await prepare.mutateAsync({ kind: "FOUND" });
    },
  });

  const hint = tickerHint(letters, assets, rivals);
  const nameClash = nameOwners(name, rivals);
  const clashMessage =
    nameClash.length > 0
      ? `“${name.trim()}”: ${nameClash.join(" e ")} preparou uma gestora com o mesmo nome.`
      : undefined;
  const previewName = name.trim() || "Sua gestora";
  const previewTicker = letters.length === 4 ? tickerOf(letters) : "ABCD11";

  return (
    <form onSubmit={(event) => event.preventDefault()} className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
      <div className="grid min-h-0 content-start gap-4.5 overflow-y-auto px-6 py-5">
        {lead}
        <fieldset
          disabled={locked}
          className="grid min-w-0 grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)] items-start gap-6 disabled:opacity-55"
        >
          {/* Identidade e linha do tempo */}
          <div className="grid min-w-0 gap-4.5">
            <PreparationSection title="Identidade" hint="salva no perfil">
              <Controller
                control={form.control}
                name="name"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid || !!clashMessage}>
                    <FieldLabel htmlFor="prep-fund-name" className="justify-between">
                      Nome da gestora
                      <span className="font-mono text-xs font-normal text-sidebar-muted">
                        {name.length}/{FUND_NAME_MAX_LENGTH}
                      </span>
                    </FieldLabel>
                    <Input
                      {...field}
                      id="prep-fund-name"
                      autoComplete="off"
                      placeholder="Ex.: Aurora Gestão"
                      aria-invalid={fieldState.invalid || !!clashMessage}
                      onChange={(event) => field.onChange(event.target.value.slice(0, FUND_NAME_MAX_LENGTH))}
                    />
                    {clashMessage || fieldState.error ? (
                      <FieldError
                        errors={[fieldState.error ?? (clashMessage ? { message: clashMessage } : undefined)]}
                      />
                    ) : (
                      <FieldDescription>
                        Aparece no menu, no caixa da topbar, no ranking e para quem comprar suas cotas.
                      </FieldDescription>
                    )}
                  </Field>
                )}
              />
              <Controller
                control={form.control}
                name="letters"
                render={({ field }) => (
                  <Field data-invalid={hint.status === "asset" || hint.status === "taken"}>
                    <FieldLabel htmlFor="prep-fund-letters">Sigla da cota</FieldLabel>
                    <InputGroup className="w-33">
                      <InputGroupInput
                        {...field}
                        id="prep-fund-letters"
                        numeric
                        autoComplete="off"
                        placeholder="ABCD"
                        aria-invalid={hint.status === "asset" || hint.status === "taken"}
                        onChange={(event) => field.onChange(cleanTickerLetters(event.target.value))}
                      />
                      <InputGroupAddon align="inline-end">
                        <InputGroupText>11</InputGroupText>
                      </InputGroupAddon>
                    </InputGroup>
                    <TickerStatus hint={hint} letters={letters} />
                    <FieldDescription>
                      4 letras mais 11, como as cotas de fundo imobiliário na bolsa. Vira o código da cota no livro de
                      ofertas.
                    </FieldDescription>
                  </Field>
                )}
              />
            </PreparationSection>

            {/* Linha do tempo */}
            <PreparationSection title="Como ela nasce" hint="na partida">
              <ol className="grid">
                {TIMELINE.map((step) => (
                  <li key={step.title} className="grid grid-cols-[6.5rem_1fr] gap-3 border-t border-muted py-2.5">
                    <span className="font-mono text-xs text-muted-foreground">{step.when}</span>
                    <div className="grid gap-0.5">
                      <b className="text-[13px] font-semibold">{step.title}</b>
                      <span className="text-xs text-muted-foreground">{step.text}</span>
                    </div>
                  </li>
                ))}
              </ol>
            </PreparationSection>
          </div>

          {/* Prévia, taxas e gestoras da sala */}
          <div className="grid min-w-0 gap-4.5">
            <PreparationSection title="Como a sala vai ver" hint="prévia">
              <div className="grid gap-2 rounded-[10px] bg-subtle px-3.5 py-3 ring-1 ring-border ring-inset">
                <span className="text-xs text-muted-foreground">No menu, em Expansões</span>
                <div className="rounded-lg bg-sidebar p-1.5">
                  <div className="flex items-center gap-2.5 rounded-md bg-sidebar-accent px-2.5 py-2 text-sm text-sidebar-foreground">
                    <FundMark name={previewName} />
                    <span className="truncate" title={previewName}>
                      {previewName}
                    </span>
                  </div>
                </div>
                <span className="text-xs text-muted-foreground">No caixa da topbar</span>
                <span className="inline-flex max-w-full items-center gap-1.5 justify-self-start rounded-lg bg-card px-2.5 py-1.5 text-[13px] ring-1 ring-input ring-inset">
                  <span className="text-muted-foreground">Caixa ·</span>
                  <b className="truncate font-semibold" title={previewName}>
                    {previewName}
                  </b>
                </span>
                <span className="text-xs text-muted-foreground">No livro de ofertas</span>
                <span className="inline-flex items-center gap-2 justify-self-start rounded-lg bg-card px-2.5 py-1.25 text-[13px] ring-1 ring-border ring-inset">
                  <Badge variant="fund" numeric>
                    {previewTicker}
                  </Badge>
                  <span className="text-muted-foreground">depois da 1ª oferta pública</span>
                </span>
              </div>
            </PreparationSection>

            <PreparationSection title="Taxas" hint="na partida">
              <div className="grid gap-2 rounded-[10px] p-3 ring-1 ring-border ring-inset">
                <span className="text-[13px]">Você escolhe na página da gestora, até o teto desta sala:</span>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary" size="tag">
                    Administração até
                    <b className="font-mono font-semibold">
                      {displayRatePercent(rules.fund_max_management_fee)} ao ano
                    </b>
                    <InfoHint label="Como funciona a taxa de administração">
                      <b className="block">Taxa de administração</b>
                      Uma parte do patrimônio da gestora que vai para você todo mês, ganhe ou perca. Com R$ 100.000,00
                      de patrimônio e 1,5% ao ano, saem R$ 125,00 por mês (100.000 × 1,5% ÷ 12). Taxa baixa atrai
                      cotista; o teto desta sala é {displayRatePercent(rules.fund_max_management_fee)} ao ano, escolhido
                      pelo host nas regras.
                    </InfoHint>
                  </Badge>
                  <Badge variant="secondary" size="tag">
                    Performance até
                    <b className="font-mono font-semibold">{displayRatePercent(rules.fund_max_performance_fee)}</b>
                    <InfoHint label="Como funciona a taxa de performance">
                      <b className="block">Taxa de performance</b>
                      Uma parte do que a cota render acima do CDI, a taxa que os bancos pagam entre si, cobrada sobre o
                      excesso. Uma cota de R$ 100,00 que vai a R$ 110,00 num período em que o CDI rendeu 4% (R$ 104,00)
                      rendeu R$ 6,00 a mais: com taxa de 20%, ficam R$ 1,20 para você. O teto desta sala é{" "}
                      {displayRatePercent(rules.fund_max_performance_fee)}.
                    </InfoHint>
                  </Badge>
                </div>
                <span className="text-xs text-muted-foreground">
                  Administração sai do patrimônio todo mês; performance é uma parte do que a cota render acima do CDI.
                </span>
              </div>
            </PreparationSection>

            <FundRoomSection rivals={rivals} humans={humans} draft={{ name, ticker: tickerOf(letters) }} />
          </div>
        </fieldset>

        <FundConflictsAlert conflicts={preparations.fund_conflicts} />
      </div>

      <PreparationFooter
        note={
          savedSimulation
            ? "Travado com partida salva selecionada."
            : "Fica no seu perfil: nome e sigla. Só nesta sala: fundar no 1º dia."
        }
        saving={autosave.saving}
        error={autosave.error}
        incomplete={autosave.incomplete}
        onRetry={autosave.retry}
        onClose={onClose}
      />
    </form>
  );
}

/** A resposta local sobre a sigla enquanto o jogador digita. */
function TickerStatus({ hint, letters }: { hint: TickerHint; letters: string }) {
  if (hint.status === "free") {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-success">
        <Check className="size-3.5" /> {tickerOf(letters)} está livre nesta sala
      </span>
    );
  }
  if (hint.status === "asset") {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-destructive">
        <CircleAlert className="size-3.5 shrink-0" /> {letters} já é um ativo da partida ({hint.assets.join(", ")})
      </span>
    );
  }
  if (hint.status === "taken") {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-destructive">
        <CircleAlert className="size-3.5 shrink-0" /> {tickerOf(letters)} é a gestora que {hint.owners.join(" e ")}{" "}
        preparou nesta sala
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
      <CircleDashed className="size-3.5" /> 4 letras; o 11 vem junto
    </span>
  );
}
