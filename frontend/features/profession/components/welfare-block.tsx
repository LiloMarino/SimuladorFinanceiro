import { useState } from "react";
import { ArrowRight, Lock } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Button } from "@/shared/components/ui/button";
import { Progress } from "@/shared/components/ui/progress";
import { displayMoney, displayMonthYear, displayNumber, displayPercent } from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { SOCIAL_TARIFF, TECHNICAL_COURSE, WELFARE_DEPOSIT, WELFARE_SAVINGS } from "../lib/profession-metrics";
import { EnrollCourseDialog } from "./enroll-course-dialog";
import { FigureCard } from "./figure-card";
import { BlockBand, BlockNote, MechanicBlock } from "./mechanic-block";
import { PROFESSION_HISTORY_ID } from "./profession-history";

type WelfareMechanic = Extract<ProfessionMechanic, { kind: "welfare" }>;
type WelfareBlockProps = { mechanic: WelfareMechanic };

/** "Sua mecânica: Pé-de-Meia, tarifa social e curso técnico" do Auxílio: a poupança do governo, o desconto na despesa e a saída para o CLT. */
export function WelfareBlock({ mechanic }: WelfareBlockProps) {
  return (
    <MechanicBlock
      title="Sua mecânica: Pé-de-Meia, tarifa social e curso técnico"
      description={
        mechanic.in_course
          ? "Curso técnico em andamento."
          : "Benefícios de quem vive de bico, e a saída para um emprego com carteira."
      }
      status={mechanic.status}
      links={[
        { label: "Carteira, linha Pé-de-Meia", to: "/portfolio" },
        { label: "Histórico da profissão", anchor: PROFESSION_HISTORY_ID },
      ]}
    >
      {mechanic.in_course ? <CourseInProgress mechanic={mechanic} /> : <Saving mechanic={mechanic} />}
    </MechanicBlock>
  );
}

/** O Auxílio poupando: o saldo e a data de liberação, o depósito do mês, a tarifa social e a matrícula no curso. */
function Saving({ mechanic }: WelfareBlockProps) {
  const [enrolling, setEnrolling] = useState(false);
  const hasSurplus = Number(mechanic.surplus) > 0;

  return (
    <>
      {/* Os números do Pé-de-Meia e da tarifa */}
      <div className="grid gap-3 md:grid-cols-3">
        <FigureCard
          label={
            <span className="inline-flex items-center gap-1">
              Pé-de-Meia <MetricHint metric={WELFARE_SAVINGS} />
            </span>
          }
          value={displayMoney(mechanic.balance)}
          note={`travado · libera em ${displayMonthYear(mechanic.next_release_on)}`}
          flag={
            mechanic.cash_was_negative
              ? { text: "caixa negativo no período: a liberação pula para a data seguinte", tone: "warning" }
              : { text: "caixa nunca negativo no período", tone: "success" }
          }
        />
        <FigureCard
          label={
            <span className="inline-flex items-center gap-1">
              Depósito deste mês <MetricHint metric={WELFARE_DEPOSIT} />
            </span>
          }
          value={displayMoney(mechanic.deposit)}
          note={
            hasSurplus
              ? `${displayPercent(mechanic.deposit_rate, 0)} da sobra de ${displayMoney(mechanic.surplus)} · teto de ${displayMoney(mechanic.deposit_cap)}`
              : `sem sobra no mês até agora · teto de ${displayMoney(mechanic.deposit_cap)}`
          }
        />
        <FigureCard
          label={
            <span className="inline-flex items-center gap-1">
              Tarifa social <MetricHint metric={SOCIAL_TARIFF} />
            </span>
          }
          value={`−${displayMoney(mechanic.discount)} por mês`}
          note={`despesa de ${displayMoney(mechanic.paid_expense)} no lugar de ${displayMoney(mechanic.full_expense)}`}
        />
      </div>

      {/* A regra do depósito e da liberação */}
      <div className="grid gap-1.5">
        <BlockNote>
          Todo mês em que o caixa e a renda fixa terminam maiores do que começaram, o governo deposita{" "}
          {displayPercent(mechanic.deposit_rate, 0)} dessa sobra, até {displayMoney(mechanic.deposit_cap)}. O depósito
          acompanha o gasto do governo com auxílio: hoje {displayNumber(mechanic.deposit_factor, 1)}×.
        </BlockNote>
        <BlockNote icon={Lock}>O saldo libera a cada 2 anos, se o caixa não ficou negativo no período.</BlockNote>
      </div>

      {/* Curso técnico */}
      <BlockBand>
        <div className="grid items-end gap-x-4 gap-y-1 md:grid-cols-[1fr_auto]">
          <div className="grid gap-1">
            <span className="flex items-center gap-1.5 text-[13px] font-semibold">
              Curso técnico <MetricHint metric={TECHNICAL_COURSE} />
            </span>
            <p className="text-[13px]">
              {mechanic.course_months} meses com a renda do bico pela metade (
              {displayMoney(mechanic.gig_income_in_course)} em vez de {displayMoney(mechanic.gig_income)}). Ao concluir,
              você vira <b className="font-bold">CLT</b> com salário de {displayMoney(mechanic.clt_salary)}.
            </p>
            <p className="text-xs text-muted-foreground">
              Vira CLT: perde a tarifa social e o Pé-de-Meia para de receber depósitos. O saldo de{" "}
              {displayMoney(mechanic.balance)} cai no seu caixa.
            </p>
          </div>
          <Button variant="outline" onClick={() => setEnrolling(true)}>
            Matricular
          </Button>
        </div>
      </BlockBand>

      <EnrollCourseDialog open={enrolling} onOpenChange={setEnrolling} mechanic={mechanic} />
    </>
  );
}

/** O curso em andamento: os meses feitos, quando conclui e o que acontece na conclusão. */
function CourseInProgress({ mechanic }: WelfareBlockProps) {
  const done = mechanic.course_months_done ?? 0;
  const ends = mechanic.course_ends_on;

  return (
    <>
      {/* Andamento do curso */}
      <div className="grid gap-1.5">
        <div className="flex justify-between text-[13px]">
          <b className="font-bold">Curso técnico</b>
          <span className="font-mono">
            {done} de {mechanic.course_months} meses
          </span>
        </div>
        <Progress value={(done / mechanic.course_months) * 100} size="md" />
        <span className="text-xs text-muted-foreground">
          {ends && `Conclui em ${displayMonthYear(ends)} · `}renda do bico pela metade até lá:{" "}
          {displayMoney(mechanic.gig_income_in_course)}
        </span>
      </div>

      {/* O que a conclusão muda */}
      <div className="grid gap-1.5">
        <BlockNote icon={ArrowRight}>
          {ends ? `Em ${displayMonthYear(ends)} você` : "Ao concluir você"} vira <b className="font-bold">CLT</b>:
          salário de {displayMoney(mechanic.clt_salary)}, FGTS e hora extra. O Pé-de-Meia para de receber depósitos e o
          saldo de {displayMoney(mechanic.balance)} cai no seu caixa.
        </BlockNote>
        <BlockNote>Pé-de-Meia {displayMoney(mechanic.balance)} e tarifa social seguem até a conclusão.</BlockNote>
      </div>
    </>
  );
}
