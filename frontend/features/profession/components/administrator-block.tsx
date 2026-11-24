import { useState } from "react";
import { ChevronDown, Landmark, TriangleAlert } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/shared/components/ui/dropdown-menu";
import { Progress } from "@/shared/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { PROFESSIONS } from "@/shared/lib/professions";
import {
  displayMoney,
  displayMonthYear,
  displayNumber,
  displayPercent,
  displayShortDate,
} from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { SECTOR_EXPERIENCE } from "../lib/profession-metrics";
import { EnrollExamDialog } from "./enroll-exam-dialog";
import { MechanicBlock } from "./mechanic-block";
import { SwitchSectorDialog } from "./switch-sector-dialog";

type AdministratorMechanic = Extract<ProfessionMechanic, { kind: "administrator" }>;
type SectorRow = AdministratorMechanic["sectors"][number];
type AdministratorBlockProps = { mechanic: AdministratorMechanic };

/** "Sua mecânica: setores e concurso" do Administrador: a experiência e a renda por setor, a troca de setor e o concurso para Servidor. */
export function AdministratorBlock({ mechanic }: AdministratorBlockProps) {
  const switchingTo = mechanic.switching_to;

  return (
    <MechanicBlock
      title="Sua mecânica: setores e concurso"
      description={
        switchingTo
          ? `Mudando para o ${PROFESSIONS[switchingTo].name}.`
          : `Você leva a renda do setor onde trabalha. A experiência em cada um sobe em ${mechanic.senior_months} meses e não se perde ao sair.`
      }
      status={mechanic.status}
    >
      {switchingTo ? (
        <SwitchInProgress mechanic={mechanic} switchingTo={switchingTo} />
      ) : (
        <Sectors mechanic={mechanic} />
      )}
      <Exam mechanic={mechanic} />
    </MechanicBlock>
  );
}

/** A troca em andamento: o setor novo, o dia em que ele entra e a renda pela metade até lá. */
function SwitchInProgress({
  mechanic,
  switchingTo,
}: AdministratorBlockProps & { switchingTo: NonNullable<AdministratorMechanic["switching_to"]> }) {
  return (
    <Alert variant="warning">
      <TriangleAlert aria-hidden="true" />
      <AlertDescription>
        <b className="font-semibold">Troca em andamento.</b> Você entra no {PROFESSIONS[switchingTo].name}
        {mechanic.switch_entry_on && ` em ${displayShortDate(mechanic.switch_entry_on)}`}. Até lá a renda é a metade:{" "}
        {displayMoney(mechanic.switch_month_income)}.
      </AlertDescription>
    </Alert>
  );
}

/** A tabela de setores e a linha "Trocar de setor". */
function Sectors({ mechanic }: AdministratorBlockProps) {
  const [target, setTarget] = useState<SectorRow | null>(null);
  const others = mechanic.sectors.filter((row) => !row.current);

  return (
    <>
      {/* Setores */}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Setor</TableHead>
            <TableHead>
              <span className="inline-flex items-center gap-1">
                Experiência <MetricHint metric={SECTOR_EXPERIENCE} />
              </span>
            </TableHead>
            <TableHead numeric>Nível</TableHead>
            <TableHead numeric>Renda hoje</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {mechanic.sectors.map((row) => (
            <SectorLine key={row.sector} row={row} seniorMonths={mechanic.senior_months} />
          ))}
        </TableBody>
      </Table>

      {/* Trocar de setor */}
      <div className="grid items-end gap-x-4 gap-y-1 md:grid-cols-[1fr_auto]">
        <div className="grid gap-0.5">
          <span className="text-[13px] font-semibold">Trocar de setor</span>
          <span className="text-xs text-muted-foreground">
            A troca leva 1 mês com a renda pela metade. Leva só a renda do setor: sem a mecânica dele.
          </span>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger disabled={mechanic.exam_status === "studying"} render={<Button variant="outline" />}>
            Trocar para…
            <ChevronDown aria-hidden="true" />
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            {others.map((row) => (
              <DropdownMenuItem key={row.sector} onClick={() => setTarget(row)}>
                {PROFESSIONS[row.sector].name}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {target && (
        <SwitchSectorDialog
          open
          onOpenChange={(open) => !open && setTarget(null)}
          mechanic={mechanic}
          target={target}
        />
      )}
    </>
  );
}

/** Uma linha da tabela: o setor, a barra de meses, o nível e a renda de hoje. */
function SectorLine({ row, seniorMonths }: { row: SectorRow; seniorMonths: number }) {
  return (
    <TableRow variant={row.current ? "current" : "default"}>
      <TableCell>
        {PROFESSIONS[row.sector].name}
        {row.current && (
          <Badge variant="info" size="tag" className="ml-1.5">
            atual
          </Badge>
        )}
      </TableCell>
      <TableCell>
        <div className="grid w-44 gap-1">
          <Progress value={(Math.min(row.months, seniorMonths) / seniorMonths) * 100} size="sm" />
          <span className="text-xs font-normal text-muted-foreground">
            {row.months} {row.months === 1 ? "mês" : "meses"} · {row.senior ? "sênior" : "júnior"}
          </span>
        </div>
      </TableCell>
      <TableCell numeric>{displayNumber(row.level, 2)}×</TableCell>
      <TableCell numeric>{displayMoney(row.income)}</TableCell>
    </TableRow>
  );
}

/** A linha "Concurso para Servidor": o edital, o estudo em andamento e a inscrição. */
function Exam({ mechanic }: AdministratorBlockProps) {
  const [enrolling, setEnrolling] = useState(false);
  const { exam_status: status } = mechanic;
  const chance = displayPercent(mechanic.exam_pass_chance, 0);
  const cut = displayPercent(mechanic.exam_income_cut, 0);

  return (
    <div className="grid items-end gap-x-4 gap-y-1 md:grid-cols-[1fr_auto]">
      <div className="grid gap-1">
        <span className="flex items-center gap-1.5 text-[13px] font-semibold">
          <Landmark className="size-3.5 text-muted-foreground" aria-hidden="true" />
          Concurso para Servidor
          {status === "open" && (
            <Badge variant="success" size="tag">
              Edital aberto
            </Badge>
          )}
          {status === "closed" && (
            <Badge variant="secondary" size="tag">
              Sem edital
            </Badge>
          )}
          {status === "studying" && (
            <Badge variant="info" size="tag">
              Estudando
            </Badge>
          )}
        </span>
        {status === "open" && mechanic.exam_open_until && (
          <>
            <p className="text-[13px]">
              Inscrições até {displayShortDate(mechanic.exam_open_until)}. {mechanic.exam_study_months} meses de estudo
              com a renda {cut} menor; chance de aprovação de {chance}.
            </p>
            <p className="text-xs text-muted-foreground">
              Aprovado, você vira Servidor com estabilidade, e a perde se sair.
            </p>
          </>
        )}
        {status === "closed" && mechanic.exam_next_on && (
          <>
            <p className="text-[13px]">O próximo abre em {displayMonthYear(mechanic.exam_next_on)}.</p>
            {mechanic.exam_extra_possible && (
              <p className="text-xs text-muted-foreground">
                Com o gasto do governo acima do normal, sai um edital a mais em julho.
              </p>
            )}
          </>
        )}
        {status === "studying" && mechanic.exam_result_on && (
          <p className="text-[13px]">
            Resultado em {displayMonthYear(mechanic.exam_result_on)}. Até lá a renda é {cut} menor:{" "}
            {displayMoney(mechanic.exam_income)}. Chance de aprovação de {chance}.
          </p>
        )}
      </div>
      {status === "open" && (
        <Button variant="outline" disabled={mechanic.switching_to !== null} onClick={() => setEnrolling(true)}>
          Inscrever
        </Button>
      )}
      <EnrollExamDialog open={enrolling} onOpenChange={setEnrolling} mechanic={mechanic} />
    </div>
  );
}
