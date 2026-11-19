import { Bot, TriangleAlert, UserPlus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useCredit } from "@/shared/hooks/queries/useCredit";
import { ActionGroup } from "@/shared/components/action-card";
import { ActionRow } from "@/shared/components/action-row";
import { FundSection } from "@/shared/components/fund-section";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { displaySelicSpread } from "@/shared/lib/credit";
import { CREDIT_RATING } from "@/shared/lib/fund-metrics";
import { netWorthOf } from "@/shared/lib/fund-view";
import { displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { MAX_COMANAGERS } from "../../lib/fund-comanagers";
import { HOLDING_CLASSES } from "../../lib/fund-classes";
import type { FundTabActions } from "../../lib/fund-tabs";
import { FundLoanDebt } from "../fund-loan-debt";
import { FundPayableFee } from "../fund-payable-fee";

const cashOf = (fund: FundDetails) => Number(fund.composition.find((item) => item.asset_class === "cash")?.value ?? 0);

/** O aviso de caixa zerado com taxa ou parcela por pagar. */
function CashNotice({ fund, installment }: { fund: FundDetails; installment: number }) {
  const payable = Number(fund.fees.payable);
  if (cashOf(fund) > 0 || (payable <= 0 && installment <= 0)) return null;

  const owed = [
    payable > 0 ? `${displayMoney(payable)} de taxa a pagar` : null,
    installment > 0 ? `${displayMoney(installment)} de parcela do empréstimo` : null,
  ].filter((item) => item !== null);

  return (
    <Alert variant="warning">
      <TriangleAlert />
      <AlertDescription>
        O caixa da gestora está zerado e ela deve {owed.join(" e ")}. O próximo dinheiro que entrar quita essas dívidas
        antes de qualquer outra coisa.
      </AlertDescription>
    </Alert>
  );
}

type OperateProps = { fund: FundDetails; label?: string };

/** O botão que põe a conta da gestora em uso; congelada ou no automático, a carteira não recebe ordens à mão e o botão não aparece. */
function OperateButton({ fund, label = "Operar a carteira" }: OperateProps) {
  const { fund: activeFund, switchAccount } = useActiveAccount();
  if (fund.frozen_until !== null || fund.automatic) return null;
  const operating = activeFund?.fund_id === fund.id;

  return operating ? (
    <Button size="xs" variant="outline" onClick={() => switchAccount(null)}>
      Voltar à minha carteira
    </Button>
  ) : (
    <Button size="xs" variant="fund" onClick={() => switchAccount(fund.id)}>
      {label}
    </Button>
  );
}

/** O card "Patrimônio da gestora": o que ela tem, o que deve e o que sobra por cota. */
function NetWorthCard({ fund }: { fund: FundDetails }) {
  const total = Number(fund.quotas);
  const netWorth = netWorthOf(fund);

  return (
    <FundSection title="Patrimônio da gestora" action={<OperateButton fund={fund} />}>
      <div>
        {fund.composition.map((item) => (
          <KeyValueRow
            key={item.asset_class}
            label={HOLDING_CLASSES[item.asset_class].label}
            value={displayMoney(item.value)}
          />
        ))}
        <FundLoanDebt debt={fund.fees.loan_debt} />
        <FundPayableFee payable={fund.fees.payable} />
        <KeyValueRow
          label="Patrimônio total"
          value={displayMoney(netWorth)}
          note={
            total > 0 && fund.nav !== null
              ? `÷ ${displayQuantity(fund.quotas)} cotas = ${displayMoney(fund.nav)} por cota`
              : undefined
          }
          total
        />
      </div>
    </FundSection>
  );
}

/** O card "Empréstimo da gestora": completo com a conta dela em uso; com outra conta, só o que ela deve. */
function LoanCard({ fund }: { fund: FundDetails }) {
  const navigate = useNavigate();
  const { fund: activeFund, switchAccount } = useActiveAccount();
  const operating = activeFund?.fund_id === fund.id;
  const { data: credit } = useCredit({ enabled: operating });
  const debt = fund.fees.loan_debt;

  if (!operating || !credit) {
    return (
      <FundSection title="Empréstimo da gestora" action={<OperateButton fund={fund} />}>
        <KeyValueRow label={<MetricLabel metric={CREDIT_RATING} />} value="Opere a carteira para ver" />
        <KeyValueRow label="Deve" value={displayMoney(debt)} />
      </FundSection>
    );
  }

  const remaining = credit.loans.reduce((sum, loan) => sum + loan.total_installments - loan.paid_installments, 0);
  const installments = credit.loans.reduce((sum, loan) => sum + loan.total_installments, 0);
  const goCredit = () => {
    switchAccount(fund.id);
    void navigate("/credit");
  };

  return (
    <FundSection
      title="Empréstimo da gestora"
      action={
        <Button size="xs" variant="outline" onClick={goCredit}>
          Pedir empréstimo
        </Button>
      }
    >
      <div>
        <KeyValueRow
          label={<MetricLabel metric={CREDIT_RATING} />}
          value={
            <Badge variant="fund" size="tag">
              Nota {credit.rating.grade}
            </Badge>
          }
        />
        <KeyValueRow
          label="Deve"
          value={displayMoney(debt)}
          note={credit.open_loans > 0 ? `${remaining} de ${installments} parcelas a pagar` : "Sem empréstimo aberto"}
        />
        <KeyValueRow
          label="Juros"
          value={credit.offer.annual_rate === null ? "—" : `${displayPercent(credit.offer.annual_rate, 2)} ao ano`}
          note={
            credit.offer.spread === null
              ? undefined
              : `SELIC de ${displayPercent(credit.offer.selic, 2)} + ${displaySelicSpread(credit.offer.spread).replace("SELIC + ", "")} pontos, pela nota ${credit.rating.grade}`
          }
        />
        <KeyValueRow label="Próxima parcela" value={displayMoney(credit.next_installments_total)} />
        <KeyValueRow label="Limite" value={displayMoney(credit.offer.max_amount)} />
      </div>
    </FundSection>
  );
}

/** O card "Posições": cada ativo da carteira com quantidade, preço, valor e fatia do patrimônio. */
function PositionsCard({ positions }: { positions: NonNullable<FundDetails["positions"]> }) {
  return (
    <FundSection title="Posições">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead wrap>Ativo</TableHead>
            <TableHead>Classe</TableHead>
            <TableHead numeric>Quantidade</TableHead>
            <TableHead numeric>Preço</TableHead>
            <TableHead numeric>Valor</TableHead>
            <TableHead numeric>Fatia do patrimônio</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {positions.map((position) => {
            const quantity = position.quantity === null ? null : Number(position.quantity);
            return (
              <TableRow key={`${position.asset_class}-${position.ticker ?? position.name}`}>
                <TableCell wrap>
                  <span className="grid">
                    <b className="font-semibold">{position.ticker ?? position.name}</b>
                    {position.ticker && <span className="text-xs text-muted-foreground">{position.name}</span>}
                  </span>
                </TableCell>
                <TableCell>{HOLDING_CLASSES[position.asset_class].label}</TableCell>
                <TableCell numeric>{position.quantity === null ? "—" : displayQuantity(position.quantity)}</TableCell>
                <TableCell numeric>
                  {quantity === null || quantity === 0 ? "—" : displayMoney(Number(position.value) / quantity)}
                </TableCell>
                <TableCell numeric>{displayMoney(position.value)}</TableCell>
                <TableCell numeric>{displayPercent(position.fraction, 1)}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </FundSection>
  );
}

/** As duas saídas da carteira congelada na presidência: ligar o automático ou chamar um co-gestor. */
function FrozenOptions({ fund, actions }: { fund: FundDetails; actions: FundTabActions }) {
  return (
    <ActionGroup
      title="Para a carteira seguir enquanto você governa"
      subtitle="A carteira só recebe ordens de novo no fim do mandato, se nada mudar"
    >
      <ActionRow
        tone="fund"
        icon={Bot}
        title="Ligar o automático"
        description="Uma estratégia opera a carteira da gestora até o fim do mandato; as decisões e as taxas seguem congeladas."
        alsoIn="Configurações"
        actionLabel="Escolher estratégia"
        onAction={() => actions.goTo("settings")}
        primary
      />
      <ActionRow
        tone="fund"
        icon={UserPlus}
        title="Convidar co-gestor"
        description="Quando ele aceita, assume a carteira na hora e ela volta a operar."
        alsoIn="Cotas"
        actionLabel="Convidar"
        onAction={() => actions.open("invite")}
        blockedReason={
          fund.comanagers.length >= MAX_COMANAGERS ? `A gestora já tem ${MAX_COMANAGERS} co-gestores` : undefined
        }
      />
    </ActionGroup>
  );
}

/** A carteira da gestora, só do gestor: patrimônio, empréstimo e posições. */
export function PortfolioTab({ fund, actions }: { fund: FundDetails; actions: FundTabActions }) {
  const { fund: activeFund } = useActiveAccount();
  const { data: credit } = useCredit({ enabled: activeFund?.fund_id === fund.id });
  const installment = credit && !credit.cash_covers_next ? Number(credit.next_installments_total) : 0;

  return (
    <div className="grid gap-5 pt-3">
      <CashNotice fund={fund} installment={installment} />
      {fund.frozen_until !== null && !fund.automatic && <FrozenOptions fund={fund} actions={actions} />}
      <div className="grid items-start gap-5 xl:grid-cols-2">
        <NetWorthCard fund={fund} />
        <LoanCard fund={fund} />
      </div>
      {fund.positions && <PositionsCard positions={fund.positions} />}
    </div>
  );
}
