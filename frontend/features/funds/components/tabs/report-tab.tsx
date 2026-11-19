import { Pie, PieChart, ResponsiveContainer } from "recharts";
import { useState } from "react";
import { CardState } from "@/shared/components/card-state";
import { FundSection } from "@/shared/components/fund-section";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { cn } from "@/shared/lib/utils";
import {
  displayIsoDate,
  displayMoney,
  displayMonthName,
  displayMonthSlashYear,
  displayPercent,
  displayShortDate,
  displaySignedPercent,
} from "@/shared/lib/utils/display";
import type { FundDetails, FundMonthlyReport } from "@/types";
import { useFundReport } from "../../hooks/queries/useFundReport";
import { HOLDING_CLASSES } from "../../lib/fund-classes";
import { movementText } from "../../lib/fund-movements";
import { FundPayableFee } from "../fund-payable-fee";
import { FundPositionsTable } from "../fund-positions-table";

type AssetClass = FundDetails["composition"][number]["asset_class"];

/** O mês no formato do endereço da API ("2026-10"). */
const monthKey = (isoDate: string) => isoDate.slice(0, 7);

/** A fatia de cada classe de ativo no relatório, somando as posições dela. */
function allocationOf(positions: FundMonthlyReport["report"]["positions"]) {
  const byClass = new Map<AssetClass, number>();
  for (const position of positions) {
    byClass.set(position.asset_class, (byClass.get(position.asset_class) ?? 0) + Number(position.fraction));
  }
  return [...byClass.entries()].map(([assetClass, fraction]) => ({ assetClass, fraction }));
}

/** O card da alocação: o donut por classe e as posições do último pregão do mês. */
function AllocationCard({ report }: { report: FundMonthlyReport }) {
  const slices = allocationOf(report.report.positions);

  return (
    <FundSection title={`Alocação da carteira em ${displayShortDate(report.report.day)}`}>
      <div className="grid gap-4">
        <div className="grid items-center gap-4 sm:grid-cols-[180px_1fr]">
          <div className="h-44">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={slices.map((slice) => ({ ...slice, fill: HOLDING_CLASSES[slice.assetClass].fill }))}
                  dataKey="fraction"
                  nameKey="assetClass"
                  innerRadius="62%"
                  outerRadius="100%"
                  stroke="none"
                  isAnimationActive={false}
                ></Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <ul className="grid gap-1.5">
            {slices.map((slice) => (
              <li key={slice.assetClass} className="flex items-center gap-2 text-[13px]">
                <span className={cn("size-2.5 rounded-full", HOLDING_CLASSES[slice.assetClass].color)} />
                <span className="flex-1">{HOLDING_CLASSES[slice.assetClass].label}</span>
                <span className="w-14 text-right font-mono font-semibold">{displayPercent(slice.fraction, 1)}</span>
              </li>
            ))}
          </ul>
        </div>
        <FundPositionsTable positions={report.report.positions} />
        <FundPayableFee payable={report.report.fee_payable} />
      </div>
    </FundSection>
  );
}

/** O card "O mês em números": o patrimônio por cota contra o CDI, o rendimento e as taxas pagas. */
function MonthNumbersCard({ report }: { report: FundMonthlyReport }) {
  const start = Number(report.nav_start);
  const navReturn = start > 0 ? Number(report.nav_end) / start - 1 : 0;
  const cdi = Number(report.cdi_return);

  return (
    <FundSection title="O mês em números">
      <div>
        <KeyValueRow
          label="Patrimônio por cota"
          value={`${displayMoney(report.nav_start)} → ${displayMoney(report.nav_end)}`}
        />
        <KeyValueRow
          label="Contra o CDI"
          value={displaySignedPercent(navReturn - cdi, 2)}
          note={`A cota rendeu ${displaySignedPercent(navReturn, 2)} e o CDI ${displayPercent(cdi, 2)} no mês`}
        />
        <KeyValueRow
          label="Rendimento por cota"
          value={report.distribution?.paid_per_quota ? displayMoney(report.distribution.paid_per_quota) : "—"}
          note={report.distribution?.paid_on ? `Pago em ${displayIsoDate(report.distribution.paid_on)}` : undefined}
        />
        <KeyValueRow label="Taxa de administração paga" value={displayMoney(report.management_fee_paid)} />
        <KeyValueRow label="Taxa de performance paga" value={displayMoney(report.performance_fee_paid)} />
        <KeyValueRow label="Empréstimo a pagar" value={displayMoney(report.loan_debt)} total />
      </div>
    </FundSection>
  );
}

/** O card "Operações do mês": o que a gestora comprou e vendeu. */
function OperationsCard({ report }: { report: FundMonthlyReport }) {
  return (
    <FundSection title={`Operações de ${displayMonthName(report.month)}`}>
      {report.operations.length === 0 ? (
        <p className="text-[13px] text-muted-foreground">A gestora não operou neste mês.</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Data</TableHead>
              <TableHead wrap>Operação</TableHead>
              <TableHead numeric>Valor</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {report.operations.map((operation, index) => (
              <TableRow key={`${operation.day}-${operation.type}-${index}`}>
                <TableCell variant="note">{displayShortDate(operation.day)}</TableCell>
                <TableCell wrap>{movementText(operation)}</TableCell>
                <TableCell numeric>{operation.amount === null ? "—" : displayMoney(operation.amount)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </FundSection>
  );
}

/** O relatório mensal, aberto a qualquer cotista: o mês escolhido, a alocação, os números e as operações. */
export function ReportTab({ fund }: { fund: FundDetails }) {
  const latest = fund.last_report ? monthKey(fund.last_report.day) : null;
  const [picked, setPicked] = useState<string | null>(null);
  const month = picked ?? latest;
  const { data: report, error, refetch } = useFundReport(fund.id, month);

  if (month === null) {
    return (
      <div className="pt-3">
        <FundSection title="Relatório">
          <p className="text-[13px] text-muted-foreground">
            O primeiro relatório sai na virada do mês seguinte à oferta pública.
          </p>
        </FundSection>
      </div>
    );
  }

  return (
    <div className="grid gap-5 pt-3">
      {/* Cabeçalho */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">
          Relatório de {displayMonthName(`${month}-01`)} de {month.slice(0, 4)}
        </h2>
        {report && (
          <ToggleGroup
            variant="segmented"
            aria-label="Mês do relatório"
            value={[month]}
            onValueChange={(values) => {
              if (values[0]) setPicked(values[0]);
            }}
          >
            {report.months.map((item) => (
              <ToggleGroupItem key={item} value={monthKey(item)}>
                {displayMonthSlashYear(item)}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        )}
      </div>
      {!report && (
        <CardState
          label="Carregando o relatório"
          error={error}
          onRetry={() => void refetch()}
          errorTitle="Não deu para carregar o relatório"
        >
          <Skeleton className="h-64" />
        </CardState>
      )}
      {report && (
        <>
          <AllocationCard report={report} />
          <div className="grid items-start gap-5 xl:grid-cols-2">
            <MonthNumbersCard report={report} />
            <OperationsCard report={report} />
          </div>
        </>
      )}
    </div>
  );
}
