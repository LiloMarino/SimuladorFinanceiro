import { useState } from "react";
import { Info } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import { moneyToBody, shareToField } from "@/shared/lib/utils/money-field";
import { useConvertPension } from "../hooks/mutations/useConvertPension";
import {
  convertedIncome,
  monthsText,
  nextBracketGain,
  planTime,
  redeemSplit,
  type RetireeMechanic,
} from "../lib/pension";
import { CONVERTED_INCOME, PENSION_BALANCE, REAL_RATE, REDEEM_TAX } from "../lib/profession-metrics";
import { FigureCard } from "./figure-card";
import { BlockPanel, MechanicBlock } from "./mechanic-block";
import { PROFESSION_HISTORY_ID } from "./profession-history";
import { RedeemPensionDialog } from "./redeem-pension-dialog";

type RetireeBlockProps = { mechanic: RetireeMechanic };

/** "Sua mecânica: previdência" do Aposentado: o saldo travado, a renda já convertida, o IR do resgate e o valor que vira renda para sempre ou volta ao caixa. */
export function RetireeBlock({ mechanic }: RetireeBlockProps) {
  const converted = Number(mechanic.converted_amount) > 0;

  return (
    <MechanicBlock
      title="Sua mecânica: previdência"
      description="Saldo travado que rende o CDI menos 1%. Pode virar renda para sempre ou ser resgatado com IR regressivo."
      status={mechanic.status}
      links={[
        { label: "Carteira, linha Previdência", to: "/portfolio" },
        { label: "Histórico da profissão", anchor: PROFESSION_HISTORY_ID },
      ]}
    >
      {/* Os números da previdência */}
      <div className="grid gap-3 md:grid-cols-3">
        <FigureCard
          label={
            <span className="inline-flex items-center gap-1">
              Saldo da previdência <MetricHint metric={PENSION_BALANCE} />
            </span>
          }
          value={displayMoney(mechanic.balance)}
          note={`rende ${displayPercent(mechanic.annual_rate)} ao ano (CDI − 1%)`}
        />
        <FigureCard
          label={
            <span className="inline-flex items-center gap-1">
              Renda já convertida <MetricHint metric={CONVERTED_INCOME} />
            </span>
          }
          value={displayMoney(mechanic.converted_income)}
          note={
            converted && mechanic.converted_real_rate !== null
              ? `por mês, de ${displayMoney(mechanic.converted_amount)} a juro real de ${displayPercent(mechanic.converted_real_rate, 1)}`
              : "nenhuma ainda"
          }
        />
        <FigureCard
          label={
            <span className="inline-flex items-center gap-1">
              IR no resgate hoje{" "}
              <MetricHint metric={REDEEM_TAX} extra={<BracketTable brackets={mechanic.brackets} />} />
            </span>
          }
          value={displayPercent(mechanic.redeem_rate, 0)}
          note={`${planTime(mechanic.months_in_plan)} no plano`}
        />
      </div>
      <PensionActions mechanic={mechanic} />
    </MechanicBlock>
  );
}

/** A tabela do IR pelo tempo no plano, como o servidor a entrega, com a faixa de hoje em destaque. */
function BracketTable({ brackets }: { brackets: RetireeMechanic["brackets"] }) {
  return (
    <ul className="grid gap-0.5 pt-1">
      {brackets.map((bracket) => (
        <li key={bracket.label} className={`flex justify-between gap-4 ${bracket.current ? "font-semibold" : ""}`}>
          <span>{bracket.label}</span>
          <span className="font-mono">{displayPercent(bracket.rate, 0)}</span>
        </li>
      ))}
    </ul>
  );
}

/** O campo de valor e as duas saídas dele: converter em renda ou resgatar para o caixa. */
function PensionActions({ mechanic }: RetireeBlockProps) {
  const convert = useConvertPension();
  const [reviewing, setReviewing] = useState(false);
  // Nulo mostra a metade do saldo; o jogador só guarda o que digitou
  const [typed, setTyped] = useState<string | null>(null);
  const balance = Number(mechanic.balance);
  const text = typed ?? shareToField(mechanic.balance, 0.5);
  const amount = Number(moneyToBody(text)) || 0;
  const valid = amount >= 0.01 && amount <= balance;
  const overBalance = amount > balance;

  const income = convertedIncome(amount, mechanic.income_rate);
  const canConvert = valid && Number(mechanic.real_rate) > 0 && !convert.isPending;
  const redeem = redeemSplit(amount, mechanic.redeem_rate);
  const wait = nextBracketGain(mechanic, amount);
  const expected = mechanic.expected_ipca_from_focus
    ? `o IPCA esperado do Focus, ${displayPercent(mechanic.expected_ipca, 1)}`
    : `o IPCA dos últimos 12 meses, ${displayPercent(mechanic.expected_ipca, 1)}`;

  return (
    <>
      {/* Valor */}
      <div className="border-y bg-subtle px-5 py-3">
        <Field data-invalid={overBalance}>
          <FieldLabel htmlFor="pension-amount">Valor</FieldLabel>
          <Input
            id="pension-amount"
            numeric
            inputMode="decimal"
            value={text}
            aria-invalid={overBalance}
            onChange={(event) => setTyped(formatMoney(event.target.value))}
          />
          {overBalance ? (
            <FieldError>O valor passa do saldo de {displayMoney(balance)}.</FieldError>
          ) : (
            <FieldDescription>De R$ 0,01 até o saldo, {displayMoney(balance)}.</FieldDescription>
          )}
        </Field>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {/* Converter em renda */}
        <BlockPanel title="Converter em renda">
          <b className="font-mono text-[17px] font-semibold">{displayMoney(income)} por mês</b>
          <span className="text-xs text-muted-foreground">
            {Number(mechanic.real_rate) > 0 ? (
              <>
                para sempre{mechanic.inflation_indexed ? ", corrigida pelo IPCA" : ""} · juro real de hoje{" "}
                {displayPercent(mechanic.real_rate, 1)} ao ano{" "}
                <MetricHint
                  metric={REAL_RATE}
                  extra={
                    <p>
                      Hoje: SELIC {displayPercent(mechanic.selic)} e {expected}.
                    </p>
                  }
                />
              </>
            ) : (
              <>
                O juro real de hoje está zerado ou negativo: espere ele subir para converter{" "}
                <MetricHint metric={REAL_RATE} />
              </>
            )}
          </span>
          <Button
            variant="outline"
            className="justify-self-start"
            disabled={!canConvert}
            onClick={() => convert.mutate({ amount: moneyToBody(text) }, { onSuccess: () => setTyped(null) })}
          >
            Converter {displayMoney(amount)}
          </Button>
        </BlockPanel>

        {/* Resgatar agora */}
        <BlockPanel title="Resgatar agora">
          <b className="font-mono text-[17px] font-semibold">{displayMoney(redeem.net)} líquido</b>
          <span className="text-xs text-muted-foreground">
            IR de {displayPercent(mechanic.redeem_rate, 0)}: {displayMoney(redeem.tax)} ficam com a Receita
          </span>
          <Button variant="outline" className="justify-self-start" disabled={!valid} onClick={() => setReviewing(true)}>
            Resgatar {displayMoney(amount)}
          </Button>
        </BlockPanel>
      </div>

      {/* A próxima faixa e o aviso da conversão */}
      {wait && (
        <p className="flex items-start gap-2 text-[13px] text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
          <span>
            <b className="font-bold text-foreground">
              Em {monthsText(wait.months)} o IR cai para {displayPercent(wait.rate, 0)}
            </b>
            : o mesmo resgate daria {displayMoney(wait.laterNet)} líquidos.
          </span>
        </p>
      )}
      <p className="flex items-start gap-2 text-[13px] text-muted-foreground">
        <Info className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
        <span>
          Converter é para sempre: o valor convertido sai do saldo e não volta. A renda fica no juro real do dia da
          conversão{mechanic.inflation_indexed ? " e sobe todo mês pelo IPCA" : ""}, sem IR e sem o reajuste dos
          aposentados.
        </span>
      </p>

      <RedeemPensionDialog
        key={amount}
        open={reviewing}
        onOpenChange={setReviewing}
        mechanic={mechanic}
        amount={amount}
        onRedeemed={() => setTyped(null)}
      />
    </>
  );
}
