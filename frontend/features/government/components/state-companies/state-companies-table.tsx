import { Link } from "react-router-dom";
import { Landmark, Plus } from "lucide-react";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { cn } from "@/shared/lib/utils";
import { STATE_LEVER_LABEL } from "@/shared/lib/state-lever";
import { POLICY_LABEL, sizeLabel } from "@/shared/lib/state-company";
import { displayMoneyLarge, displayMonthSlashYear, displayPercent } from "@/shared/lib/utils/display";
import type { GovernmentMeasure, StateCompaniesPanel, StateCompany } from "@/types";
import { DIVIDEND_POLICY, PRICE_CONTROL, SINCE_FOUNDING, STATE_STAKE } from "../../lib/government-metrics";
import {
  companyValue,
  controlLabel,
  heldCompanies,
  rowControlEffect,
  signedSince,
  sinceFounding,
  votesOnLabel,
} from "../../lib/state-companies";

type StateCompaniesTableProps = {
  panel: StateCompaniesPanel;
  /** A fila do Congresso: dela vem o dia da votação de cada privatização */
  queue: GovernmentMeasure[];
  onFound: () => void;
  onCommand: (ticker: string) => void;
  onPrivatize: (ticker: string) => void;
  onSeeVote: () => void;
};

/** As estatais do governo, uma linha por empresa; o presidente comanda, privatiza e funda daqui, e a sala lê. */
export function StateCompaniesTable({
  panel,
  queue,
  onFound,
  onCommand,
  onPrivatize,
  onSeeVote,
}: StateCompaniesTableProps) {
  const companies = heldCompanies(panel.companies);

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          {/* Header */}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <h2 className="text-[15px] font-semibold">Estatais do governo</h2>
              {!panel.is_president && <Badge variant="secondary">só leitura</Badge>}
            </div>
            {panel.is_president && companies.length > 0 && (
              <Button size="sm" onClick={onFound}>
                <Plus data-icon="inline-start" />
                Fundar estatal
              </Button>
            )}
          </div>

          {/* Listagem das estatais */}
          {companies.length === 0 ? (
            <Empty>
              <EmptyMedia variant="icon">
                <Landmark />
              </EmptyMedia>
              <EmptyHeader>
                <EmptyTitle>O governo não tem estatais</EmptyTitle>
                <EmptyDescription>
                  {panel.is_president
                    ? `Fundar uma estatal vai a votação no Congresso e é paga com dívida: o governo fica com ${displayPercent(panel.rules.founding_share, 0)} e a bolsa com ${displayPercent(1 - Number(panel.rules.founding_share), 0)}.`
                    : "Quando o presidente fundar uma estatal, ou o jogo marcar uma como do governo, ela aparece aqui para a sala toda."}
                </EmptyDescription>
              </EmptyHeader>
              {panel.is_president && (
                <Button size="sm" onClick={onFound}>
                  <Plus data-icon="inline-start" />
                  Fundar estatal
                </Button>
              )}
            </Empty>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead wrap>Empresa</TableHead>
                  <TableHead wrap>Alavanca</TableHead>
                  <TableHead wrap numeric>
                    <MetricLabel metric={STATE_STAKE} />
                  </TableHead>
                  <TableHead wrap numeric>
                    <MetricLabel metric={SINCE_FOUNDING} />
                  </TableHead>
                  <TableHead wrap>
                    <MetricLabel metric={PRICE_CONTROL} />
                  </TableHead>
                  <TableHead wrap>
                    <MetricLabel metric={DIVIDEND_POLICY} />
                  </TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {companies.map((company) => (
                  <CompanyRow
                    key={company.ticker}
                    company={company}
                    isPresident={panel.is_president}
                    voteLabel={votesOnLabel(company, queue)}
                    onCommand={() => onCommand(company.ticker)}
                    onPrivatize={() => onPrivatize(company.ticker)}
                    onSeeVote={onSeeVote}
                  />
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

type CompanyRowProps = {
  company: StateCompany;
  isPresident: boolean;
  voteLabel: string | null;
  onCommand: () => void;
  onPrivatize: () => void;
  onSeeVote: () => void;
};

function CompanyRow({ company, isPresident, voteLabel, onCommand, onPrivatize, onSeeVote }: CompanyRowProps) {
  const since = sinceFounding(company);
  const effect = rowControlEffect(company);
  const locked = company.privatization_measure_id !== null || company.status === "PRIVATIZING";
  const nextControl = company.order.control !== company.in_force.control ? company.order.control : null;
  const nextPolicy =
    company.order.dividend_policy !== company.in_force.dividend_policy ? company.order.dividend_policy : null;

  return (
    <TableRow variant={voteLabel ? "warning" : "default"}>
      {/* Empresa */}
      <TableCell wrap>
        <span className="grid gap-0.5">
          <span className="flex flex-wrap items-center gap-1.5">
            <b className="font-medium">{company.name}</b>
            <span className="font-mono text-xs text-muted-foreground">{company.ticker}</span>
          </span>
          <span className="text-xs text-muted-foreground">
            {company.origin === "IMPORTED" || company.founded_on === null || company.size === null
              ? "Importada · já existia na bolsa"
              : `Fundada em ${displayMonthSlashYear(company.founded_on)} · porte ${sizeLabel(company.size)}`}
          </span>
          {voteLabel ? (
            <Badge variant="warning" size="sm" className="justify-self-start">
              Privatização em votação · {voteLabel}
            </Badge>
          ) : (
            company.privatization_measure_id !== null &&
            company.status === "ACTIVE" && (
              <Badge variant="info" size="sm" className="justify-self-start">
                Privatização aprovada · a oferta abre em breve
              </Badge>
            )
          )}
          {company.status === "PRIVATIZING" && (
            <Badge variant="info" size="sm" className="justify-self-start">
              Oferta aberta à sala
            </Badge>
          )}
        </span>
      </TableCell>

      {/* Alavanca */}
      <TableCell wrap>{company.lever ? STATE_LEVER_LABEL[company.lever] : "—"}</TableCell>

      {/* Fatia do governo */}
      <TableCell numeric wrap>
        <span className="grid gap-0.5">
          <b className="font-mono font-semibold">{displayMoneyLarge(company.government_value)}</b>
          <span className="text-xs font-normal text-muted-foreground">
            {displayPercent(company.government_share, 1, { trim: true })} de {displayMoneyLarge(companyValue(company))}
          </span>
        </span>
      </TableCell>

      {/* Desde a fundação */}
      <TableCell numeric wrap>
        {since === null ? (
          <span className="text-muted-foreground">—</span>
        ) : (
          <b className={cn("font-mono font-semibold", since < 0 ? "text-destructive" : "text-success")}>
            {signedSince(since)}
          </b>
        )}
      </TableCell>

      {/* Controle de preço */}
      <TableCell wrap>
        {company.lever === null ? (
          <span className="text-xs text-muted-foreground">Sem alavanca de preço</span>
        ) : (
          <span className={cn("grid gap-0.5", locked && "text-muted-foreground")}>
            <b className="font-medium">{controlLabel(company.in_force.control)}</b>
            {effect && <span className="text-xs text-muted-foreground">{effect}</span>}
            {nextControl && (
              <span className="text-xs text-muted-foreground">
                Ordem para o mês seguinte: {controlLabel(nextControl).toLowerCase()}
              </span>
            )}
          </span>
        )}
      </TableCell>

      {/* Dividendos */}
      <TableCell wrap>
        <span className={cn("grid gap-0.5", locked && "text-muted-foreground")}>
          <b className="font-medium">{POLICY_LABEL[company.in_force.dividend_policy]}</b>
          <span className="text-xs text-muted-foreground">
            {displayMoneyLarge(company.treasury_dividend_12m)} ao Tesouro em 12 meses
          </span>
          {nextPolicy && (
            <span className="text-xs text-muted-foreground">Mês seguinte: {POLICY_LABEL[nextPolicy]}</span>
          )}
          <Button
            variant="link"
            size="xs"
            nativeButton={false}
            render={<Link to={`/variable-income/${company.ticker}`} />}
            className="justify-self-start"
          >
            Ver lucro e dividendos
          </Button>
        </span>
      </TableCell>

      {/* Ações */}
      <TableCell numeric wrap>
        <span className="flex flex-wrap justify-end gap-1.5">
          {voteLabel && (
            <Button size="xs" variant="outline" onClick={onSeeVote}>
              Ver votação
            </Button>
          )}
          {isPresident && company.can_command && (
            <>
              <Button size="xs" variant="outline" onClick={onCommand}>
                Comandar
              </Button>
              <Button size="xs" variant="outline" onClick={onPrivatize}>
                Privatizar
              </Button>
            </>
          )}
        </span>
      </TableCell>
    </TableRow>
  );
}
