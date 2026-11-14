import { FileText } from "lucide-react";
import { useState } from "react";
import { StackedBar } from "@/shared/components/stacked-bar";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import { displayIsoDate, displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { HOLDING_CLASSES } from "../lib/fund-classes";
import { FundPositionsTable } from "./fund-positions-table";
import { FundReportDialog } from "./fund-report-dialog";
import { FundSection } from "./fund-section";

/** A barra e a legenda do patrimônio por classe, ao vivo. */
function ClassBreakdown({ composition }: { composition: FundDetails["composition"] }) {
  return (
    <div className="grid gap-3">
      <StackedBar
        size="lg"
        segments={composition.map((item) => ({
          key: item.asset_class,
          fraction: Number(item.fraction),
          color: HOLDING_CLASSES[item.asset_class].color,
        }))}
      />
      <ul className="grid gap-1.5">
        {composition.map((item) => (
          <li key={item.asset_class} className="flex items-center gap-2 text-[13px]">
            <span className={cn("size-2.5 rounded-full", HOLDING_CLASSES[item.asset_class].color)} />
            <span className="flex-1">{HOLDING_CLASSES[item.asset_class].label}</span>
            <span className="font-mono text-muted-foreground">{displayMoney(item.value)}</span>
            <span className="w-14 text-right font-mono font-semibold">{displayPercent(item.fraction, 1)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** A carteira por classe ao vivo e, para o gestor, a tabela de posições; a sala vê o último relatório mensal. */
export function FundComposition({ fund }: { fund: FundDetails }) {
  const [reportOpen, setReportOpen] = useState(false);
  const { positions, last_report: report } = fund;

  return (
    <FundSection title={positions ? "Carteira da gestora" : "No que investe"}>
      <div className="grid gap-4">
        <ClassBreakdown composition={fund.composition} />
        {positions && <FundPositionsTable positions={positions} />}
        {report ? (
          <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-subtle px-3 py-2.5">
            <span className="text-xs text-muted-foreground">
              {positions
                ? `A sala vê a carteira posição a posição só no relatório mensal, o último de ${displayIsoDate(report.day)}.`
                : `As posições saem uma vez por mês, no relatório. O último é de ${displayIsoDate(report.day)}.`}
            </span>
            <Button variant="link" size="xs" onClick={() => setReportOpen(true)}>
              <FileText />
              Ver o último relatório
            </Button>
            <FundReportDialog open={reportOpen} onOpenChange={setReportOpen} fundName={fund.name} report={report} />
          </div>
        ) : (
          <p className="text-xs text-muted-foreground">
            O primeiro relatório mensal com as posições sai no fim do mês.
          </p>
        )}
      </div>
    </FundSection>
  );
}
