import { Check, CircleAlert, CircleDashed } from "lucide-react";
import { useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { useDebounce } from "use-debounce";
import { FundMark } from "@/shared/components/fund-mark";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { InputGroup, InputGroupAddon, InputGroupInput, InputGroupText } from "@/shared/components/ui/input-group";
import { Spinner } from "@/shared/components/ui/spinner";
import { displayRatePercent } from "@/shared/lib/financial-independence";
import {
  cleanTickerLetters,
  FUND_NAME_MAX_LENGTH,
  FUND_NAME_MIN_LENGTH,
  TICKER_LETTERS,
  tickerOf,
} from "@/shared/lib/fund-ticker";
import { displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import type { PortfolioState } from "@/types";
import { useContributeToFund } from "../hooks/mutations/useContributeToFund";
import { useFoundFund } from "../hooks/mutations/useFoundFund";
import { useTickerCheck } from "../hooks/queries/useTickerCheck";
import { cashOf, contributionBody, contributionReady, picksValue, type StockPicks } from "../lib/fund-contribution";
import { EXAMPLE_NET_WORTH, feeToBody, feeToPoints, snapFee } from "../lib/fund-fees";
import { FIRST_QUOTA_PRICE, foundingSummary, tickerFeedback, type TickerFeedback } from "../lib/fund-math";
import { ContributionPicker } from "./contribution-picker";
import { FeeControls } from "./fee-controls";

const TICKER_DEBOUNCE_MS = 300;

type FundFoundFormProps = {
  portfolio: PortfolioState;
  /** Os tetos de taxa da partida, em fração ("0.0200") */
  maxManagement: string;
  maxPerformance: string;
};

function Step({ number, title, children }: { number: number; title: string; children: ReactNode }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2.5">
          <span className="grid size-6 place-items-center rounded-full bg-fund-soft font-mono text-xs font-semibold text-fund">
            {number}
          </span>
          <CardTitle>{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

const FEEDBACK_ICON = { success: Check, error: CircleAlert, neutral: CircleDashed } as const;
const FEEDBACK_TONE = {
  success: "text-success",
  error: "text-destructive",
  neutral: "text-muted-foreground",
} as const;

/** A resposta sobre a sigla enquanto o jogador digita. */
function TickerStatus({ feedback }: { feedback: TickerFeedback }) {
  const Icon = FEEDBACK_ICON[feedback.tone];
  return (
    <span
      role="status"
      className={`inline-flex items-center gap-1.5 text-xs font-medium ${FEEDBACK_TONE[feedback.tone]}`}
    >
      <Icon className="size-3.5 shrink-0" /> {feedback.message}
    </span>
  );
}

/** Fundar a gestora em três passos numa página: nome e sigla, o que sai da carteira e as taxas, com a conta das cotas ao lado. */
export function FundFoundForm({ portfolio, maxManagement, maxPerformance }: FundFoundFormProps) {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [letters, setLetters] = useState("");
  const [cashText, setCashText] = useState("");
  const [picks, setPicks] = useState<StockPicks>({});
  const capManagement = feeToPoints(maxManagement);
  const capPerformance = feeToPoints(maxPerformance);
  const [management, setManagement] = useState(() => snapFee(capManagement / 2, capManagement));
  const [performance, setPerformance] = useState(() => snapFee(capPerformance / 2, capPerformance));

  const foundFund = useFoundFund();
  const contribute = useContributeToFund();

  const [settledLetters] = useDebounce(letters, TICKER_DEBOUNCE_MS);
  const complete = letters.length === TICKER_LETTERS;
  const check = useTickerCheck(tickerOf(settledLetters), { enabled: complete && settledLetters === letters });
  const checking = settledLetters !== letters || check.isFetching;
  const feedback = tickerFeedback(letters, check.data, checking);

  const trimmed = name.trim();
  const summary = foundingSummary(cashOf(cashText), picksValue(picks, portfolio.variable_income));
  const brings = cashOf(cashText) > 0 || Object.keys(picks).length > 0;
  const contributionOk =
    !brings ||
    (contributionReady(cashText, picks, portfolio.variable_income, Number(portfolio.cash)) && summary.quotas >= 1);
  const ready = trimmed.length >= FUND_NAME_MIN_LENGTH && feedback.tone === "success" && contributionOk;
  const pending = foundFund.isPending || contribute.isPending;
  const label = trimmed || "gestora";

  // Funda a gestora e, em seguida, leva a carteira; a página da gestora abre com o que deu certo
  const found = async () => {
    const fund = await foundFund.mutateAsync({
      name: trimmed,
      ticker: tickerOf(letters),
      management_fee: feeToBody(management),
      performance_fee: feeToBody(performance),
    });
    if (brings) {
      await contribute
        .mutateAsync({ fundId: fund.id, request: contributionBody(cashText, picks) })
        .catch(() => undefined);
    }
    void navigate(`/funds/${fund.id}`);
  };

  return (
    <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
      <div className="grid gap-5">
        <Step number={1} title="Nome e sigla">
          <div className="grid gap-4">
            <Field>
              <FieldLabel htmlFor="found-name" className="justify-between">
                Nome da gestora
                <span className="font-mono text-xs font-normal text-muted-foreground">
                  {name.length}/{FUND_NAME_MAX_LENGTH}
                </span>
              </FieldLabel>
              <Input
                id="found-name"
                autoComplete="off"
                placeholder="Ex.: Aurora Gestão"
                value={name}
                onChange={(event) => setName(event.target.value.slice(0, FUND_NAME_MAX_LENGTH))}
              />
              <FieldDescription>
                De {FUND_NAME_MIN_LENGTH} a {FUND_NAME_MAX_LENGTH} letras. Nome e sigla não mudam depois.
              </FieldDescription>
            </Field>
            <Field>
              <FieldLabel htmlFor="found-letters">Sigla da cota</FieldLabel>
              <InputGroup className="w-33">
                <InputGroupInput
                  id="found-letters"
                  numeric
                  autoComplete="off"
                  placeholder="ABCD"
                  value={letters}
                  aria-invalid={feedback.tone === "error"}
                  onChange={(event) => setLetters(cleanTickerLetters(event.target.value))}
                />
                <InputGroupAddon align="inline-end">
                  <InputGroupText>11</InputGroupText>
                </InputGroupAddon>
              </InputGroup>
              <TickerStatus feedback={feedback} />
              <FieldDescription>
                4 letras mais 11, como as cotas de fundo imobiliário na bolsa. Vira o código da cota no livro de
                ofertas.
              </FieldDescription>
            </Field>
          </div>
        </Step>

        <Step number={2} title="O que sai da carteira">
          <ContributionPicker
            portfolio={portfolio}
            cashText={cashText}
            onCashChange={setCashText}
            picks={picks}
            onPicksChange={setPicks}
            idPrefix="found"
          />
        </Step>

        <Step number={3} title="Taxas">
          <FeeControls
            managementPoints={management}
            onManagementChange={setManagement}
            performancePoints={performance}
            onPerformanceChange={setPerformance}
            maxManagement={maxManagement}
            maxPerformance={maxPerformance}
            netWorth={EXAMPLE_NET_WORTH}
          />
        </Step>
      </div>

      {/* Como a gestora nasce */}
      <Card className="xl:sticky xl:top-4">
        <CardHeader>
          <div className="flex items-start gap-2.5">
            <FundMark name={trimmed || "Sua gestora"} />
            <div className="grid min-w-0 gap-0.5">
              <CardTitle className="break-words">Como a {trimmed || "gestora"} nasce</CardTitle>
              <span className="font-mono text-xs text-muted-foreground">{complete ? tickerOf(letters) : "ABCD11"}</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            <div>
              <KeyValueRow label="Sai da sua carteira" value={displayMoney(summary.taken)} />
              <KeyValueRow label="A primeira cota nasce a" value={displayMoney(FIRST_QUOTA_PRICE)} />
              <KeyValueRow label="Você recebe" value={`${displayQuantity(String(summary.quotas))} cotas`} total />
              <KeyValueRow label="Sobra, fica na gestora" value={displayMoney(summary.leftover)} />
              <KeyValueRow
                label="Taxas"
                value={`${displayRatePercent(management / 100)} · ${displayRatePercent(performance / 100)}`}
              />
            </div>
            <p className="rounded-lg bg-subtle px-3 py-2.5 text-xs text-muted-foreground">
              A gestora nasce fechada: só você é cotista, com 100% das cotas. Quando quiser que a sala compre, abra uma
              oferta pública. Sem levar nada agora, você leva depois, na página da gestora.
            </p>
            <Button variant="fund" size="lg" disabled={!ready || pending} onClick={() => void found()}>
              {pending && <Spinner />}
              Fundar a {label}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
