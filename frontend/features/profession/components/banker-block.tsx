import { MetricHint } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Link } from "react-router-dom";
import { displayDate, displayMoney, displayPercent, parseLocalDate } from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { TREASURY_FIXED } from "../lib/profession-metrics";
import { BlockPanel, MechanicBlock } from "./mechanic-block";

type BankerBlockProps = {
  mechanic: Extract<ProfessionMechanic, { kind: "banker" }>;
};

const termName = (years: number) => `${years} ${years === 1 ? "ano" : "anos"}`;

/** "Sua mecânica: CDB da casa" do Bancário: três prazos a 1 ponto acima do Tesouro prefixado, com teto de 1 salário. */
export function BankerBlock({ mechanic }: BankerBlockProps) {
  const applied = mechanic.cdbs.filter((cdb) => Number(cdb.applied) > 0);
  // O CDB de menor prazo com dinheiro aplicado é o primeiro a vencer e abrir espaço sob o teto
  const nextToMature = applied[0];
  const cap = mechanic.cdbs[0]?.cap ?? "0";

  return (
    <MechanicBlock
      title="Sua mecânica: CDB da casa"
      description="O banco onde você trabalha paga 1 ponto acima do Tesouro prefixado do mesmo prazo."
      status={mechanic.status}
      links={[
        { label: "Renda fixa, linha com o selo", to: "/fixed-income" },
        { label: "Carteira", to: "/portfolio" },
      ]}
    >
      {mechanic.status === "LOCKED" && (
        <Alert variant="warning">
          <AlertTitle>Tetos cheios.</AlertTitle>
          <AlertDescription>
            Cada CDB aceita até 1 salário líquido.
            {nextToMature &&
              ` O de ${termName(nextToMature.years)} vence em ${displayDate(parseLocalDate(nextToMature.maturity_date))} e libera ${displayMoney(nextToMature.applied)}; um reajuste de salário também sobe o teto.`}
          </AlertDescription>
        </Alert>
      )}

      {/* CDBs da casa */}
      <div className="grid gap-4 md:grid-cols-3">
        {mechanic.cdbs.map((cdb) => {
          const free = Math.max(Number(cdb.cap) - Number(cdb.applied), 0);
          return (
            <BlockPanel
              key={cdb.years}
              title={termName(cdb.years)}
              aside={free === 0 ? <Badge variant="warning">Teto cheio</Badge> : undefined}
            >
              <span className="font-mono text-[22px] font-semibold tabular-nums">
                {displayPercent(cdb.annual_rate, 2)} ao ano
              </span>
              <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                prefixado {displayPercent(cdb.treasury_rate, 2)} + 1 <MetricHint metric={TREASURY_FIXED} />
              </span>
              <span className="text-[13px]">
                aplicado <b className="font-mono">{displayMoney(cdb.applied)}</b>
                {" · "}
                {free === 0 ? (
                  "nada livre"
                ) : (
                  <>
                    livre <b className="font-mono">{displayMoney(free)}</b>
                  </>
                )}
              </span>
            </BlockPanel>
          );
        })}
      </div>

      <p className="text-[13px] text-muted-foreground">
        Teto de <b className="font-mono">{displayMoney(cap)}</b> por CDB: 1 salário líquido. As taxas valem o mês todo.
      </p>

      {/* Aplicações */}
      {applied.length > 0 && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Aplicação</TableHead>
              <TableHead numeric>Taxa travada</TableHead>
              <TableHead numeric>Aplicado</TableHead>
              <TableHead numeric>Hoje</TableHead>
              <TableHead numeric>Vence</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {applied.map((cdb) => (
              <TableRow key={cdb.years}>
                <TableCell>CDB da casa {termName(cdb.years)}</TableCell>
                <TableCell numeric>{displayPercent(cdb.annual_rate, 2)} ao ano</TableCell>
                <TableCell numeric>{displayMoney(cdb.applied)}</TableCell>
                <TableCell numeric>{displayMoney(cdb.current_value)}</TableCell>
                <TableCell numeric>{displayDate(parseLocalDate(cdb.maturity_date))}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <p className="text-[13px] text-muted-foreground">
        Sem resgate antes do vencimento: o dinheiro fica até o fim do prazo.
      </p>

      <div>
        <Button variant="outline" size="sm" nativeButton={false} render={<Link to="/fixed-income" />}>
          Aplicar na Renda fixa
        </Button>
      </div>
    </MechanicBlock>
  );
}
