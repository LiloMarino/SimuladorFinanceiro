import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricHint } from "@/shared/components/metric-hint";
import { StackedBar } from "@/shared/components/stacked-bar";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { LOCKED_RATE, PAYROLL_MARGIN } from "@/shared/lib/credit-metrics";
import { displayMoney, displayMonthSlashYear, displayPercent } from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { BlockPanel, MechanicBlock } from "./mechanic-block";

type PublicServantBlockProps = {
  mechanic: Extract<ProfessionMechanic, { kind: "public_servant" }>;
};

/** "Sua mecânica: consignado" do Servidor: a margem do salário, os contratos e o juro de hoje. */
export function PublicServantBlock({ mechanic }: PublicServantBlockProps) {
  const margin = Number(mechanic.margin);
  const usedFraction = margin > 0 ? Number(mechanic.margin_used) / margin : 0;

  return (
    <MechanicBlock
      title="Sua mecânica: consignado"
      description="Empréstimo com a parcela descontada do salário: SELIC + 2 ao ano, 1 ponto abaixo do seu comum."
      status={mechanic.status}
      links={[{ label: "Crédito, cartão e linha do consignado", to: "/credit" }]}
    >
      {/* Margem consignável */}
      <BlockPanel title="Margem consignável" aside={<MetricHint metric={PAYROLL_MARGIN} />}>
        <span className="font-mono text-[22px] font-semibold tabular-nums">
          {displayMoney(mechanic.margin)} por mês
        </span>
        <span className="text-[13px] text-muted-foreground">
          35% do salário líquido de {displayMoney(mechanic.net_salary)}: quanto as parcelas podem somar
        </span>
        <StackedBar size="lg" segments={[{ key: "used", fraction: usedFraction, color: "bg-chart-1" }]} />
        <div className="flex flex-wrap justify-between gap-x-4 text-[13px]">
          <span>
            usada <b className="font-mono">{displayMoney(mechanic.margin_used)}</b>
          </span>
          <span>
            livre <b className="font-mono">{displayMoney(mechanic.margin_free)}</b>
          </span>
        </div>
        {mechanic.status === "LOCKED" && (
          <Alert variant="warning">
            <AlertTitle>Margem toda usada.</AlertTitle>
            <AlertDescription>
              As parcelas{" "}
              {mechanic.loans.length === 1
                ? "do seu consignado somam"
                : `dos seus ${mechanic.loans.length} consignados somam`}{" "}
              35% do salário líquido.{" "}
              {mechanic.next_release && mechanic.next_release_amount
                ? `A margem volta conforme eles terminam: o próximo acaba em ${displayMonthSlashYear(mechanic.next_release)} e libera ${displayMoney(mechanic.next_release_amount)} por mês.`
                : "A margem volta conforme eles terminam."}
            </AlertDescription>
          </Alert>
        )}
      </BlockPanel>

      {/* Contratos */}
      {mechanic.loans.length === 0 ? (
        <p className="text-[13px] text-muted-foreground">
          Você ainda não tem consignado. Simule na Crédito, na aba Consignado.
        </p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Contrato</TableHead>
              <TableHead numeric>
                <span className="inline-flex items-center gap-1">
                  Juro travado <MetricHint metric={LOCKED_RATE} />
                </span>
              </TableHead>
              <TableHead numeric>Parcela</TableHead>
              <TableHead numeric>Pagas</TableHead>
              <TableHead numeric>Saldo devedor</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {mechanic.loans.map((loan) => (
              <TableRow key={loan.id}>
                <TableCell>Consignado de {displayMonthSlashYear(loan.contract_date)}</TableCell>
                <TableCell numeric>{displayPercent(loan.annual_rate, 2)} ao ano</TableCell>
                <TableCell numeric>{displayMoney(loan.installment)}</TableCell>
                <TableCell numeric>
                  {loan.paid_installments} de {loan.total_installments}
                </TableCell>
                <TableCell numeric>{displayMoney(loan.balance)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <KeyValueRow
        label="Juro para um novo hoje"
        note={`SELIC de ${displayPercent(mechanic.selic, 2)} + 2, travado no contrato`}
        value={`${displayPercent(mechanic.annual_rate, 2)} ao ano`}
      />
    </MechanicBlock>
  );
}
