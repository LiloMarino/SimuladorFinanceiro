import { useState, type ReactNode } from "react";
import { Check, TriangleAlert } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Progress } from "@/shared/components/ui/progress";
import { cn } from "@/shared/lib/utils";
import { displayMoney, displayMonthYear, displayPercent } from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { displayMultiple, displayStepDuration, STEP_TEXTS, type GraduateStep } from "../lib/graduate-steps";
import { CAREER_END_MULTIPLE, LIVES_WITH_PARENTS } from "../lib/profession-metrics";
import { EnrollStepDialog } from "./enroll-step-dialog";
import { FigureCard } from "./figure-card";
import { LeaveHomeDialog } from "./leave-home-dialog";
import { BlockNote, MechanicBlock } from "./mechanic-block";
import { PROFESSION_HISTORY_ID } from "./profession-history";

type GraduateMechanic = Extract<ProfessionMechanic, { kind: "graduate" }>;
type GraduateBlockProps = { mechanic: GraduateMechanic };

/** "Sua mecânica: escada acadêmica e mora com os pais" do Recém-formado: a curva do salário, os degraus e a casa dos pais. */
export function GraduateBlock({ mechanic }: GraduateBlockProps) {
  const [enrolling, setEnrolling] = useState<GraduateStep | null>(null);
  const [leaving, setLeaving] = useState(false);
  const current = mechanic.steps.find((step) => step.status === "current");
  const next = mechanic.steps.find((step) => step.status === "next");
  const afterCurrent = current && mechanic.steps.find((step) => step.status === "later");

  return (
    <MechanicBlock
      title="Sua mecânica: escada acadêmica e mora com os pais"
      description={
        current
          ? `${STEP_TEXTS[current.step].label} em curso: ${afterCurrent ? "o próximo degrau abre ao concluir." : "o último degrau da escada."}`
          : "Começa fraco e tem o maior salário numa partida longa. Cada degrau sobe o salário do fim da carreira."
      }
      status={mechanic.status}
      links={[{ label: "Histórico da profissão", anchor: PROFESSION_HISTORY_ID }]}
    >
      {/* Os números da carreira e da casa dos pais */}
      <div className="grid gap-3 md:grid-cols-3">
        <FigureCard
          label="Salário hoje"
          value={displayMoney(mechanic.salary)}
          note={
            mechanic.stipend_income !== null
              ? `ano ${mechanic.career_year} da carreira · bolsa de ${displayMoney(mechanic.stipend_income)} no lugar`
              : `ano ${mechanic.career_year} da carreira`
          }
        />
        <FigureCard
          label={
            <span className="inline-flex items-center gap-1">
              Múltiplo do fim da carreira <MetricHint metric={CAREER_END_MULTIPLE} />
            </span>
          }
          value={
            mechanic.next_final_multiple !== null
              ? `${displayMultiple(mechanic.final_multiple)} → ${displayMultiple(mechanic.next_final_multiple)}`
              : displayMultiple(mechanic.final_multiple)
          }
          note={mechanic.next_step ? `ao concluir ${STEP_TEXTS[mechanic.next_step].withArticle}` : "topo da escada"}
        />
        <HomeCard mechanic={mechanic} />
      </div>

      {/* Degraus da escada */}
      <div className="grid gap-2">
        <span className="text-[13px] font-semibold">Degraus</span>
        <ol className="divide-y rounded-[10px] border">
          {mechanic.steps.map((step, index) => (
            <StepRow
              key={step.step}
              step={step}
              position={index + 1}
              action={
                step === next ? (
                  <Button variant="outline" onClick={() => setEnrolling(step)}>
                    Matricular
                  </Button>
                ) : undefined
              }
            />
          ))}
        </ol>
      </div>

      {/* Desconto da matrícula e o degrau seguinte travado */}
      {next && (
        <BlockNote>
          Matricular com o desemprego acima do neutro de {displayPercent(mechanic.neutral_unemployment, 0)} dá desconto
          na mensalidade e bolsa maior. Hoje: {displayPercent(mechanic.unemployment, 1, { trim: true })},{" "}
          {mechanic.unemployment_discount ? "com desconto" : "sem desconto"}.
        </BlockNote>
      )}
      {current && afterCurrent && mechanic.next_opens_on && mechanic.months_left !== null && (
        <Alert variant="warning">
          <TriangleAlert aria-hidden="true" />
          <AlertDescription>
            {capitalize(STEP_TEXTS[afterCurrent.step].withArticle)} abre em {displayMonthYear(mechanic.next_opens_on)},
            quando {STEP_TEXTS[current.step].withArticle} acabar. Faltam {mechanic.months_left}{" "}
            {mechanic.months_left === 1 ? "mês" : "meses"}. <b className="font-semibold">Um degrau por vez.</b>
          </AlertDescription>
        </Alert>
      )}

      {/* Sair de casa */}
      {mechanic.home === "with_parents" && (
        <div className="grid items-end gap-x-4 gap-y-1 md:grid-cols-[1fr_auto]">
          <div className="grid gap-0.5">
            <span className="text-[13px] font-semibold">Sair de casa</span>
            <span className="text-xs text-muted-foreground">
              A despesa volta ao normal, {displayMoney(mechanic.full_expense)} por mês, e não dá para voltar.
            </span>
          </div>
          <Button variant="outline" onClick={() => setLeaving(true)}>
            Sair de casa
          </Button>
        </div>
      )}

      {enrolling && (
        <EnrollStepDialog
          open
          onOpenChange={(open) => !open && setEnrolling(null)}
          mechanic={mechanic}
          step={enrolling}
        />
      )}
      <LeaveHomeDialog open={leaving} onOpenChange={setLeaving} mechanic={mechanic} />
    </MechanicBlock>
  );
}

function capitalize(text: string) {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/** O cartão da casa dos pais: o desconto na despesa enquanto mora com eles e o estado sem desconto depois. */
function HomeCard({ mechanic }: GraduateBlockProps) {
  const label = (
    <span className="inline-flex items-center gap-1">
      Mora com os pais <MetricHint metric={LIVES_WITH_PARENTS} />
    </span>
  );
  switch (mechanic.home) {
    case "with_parents":
      return (
        <FigureCard
          label={label}
          value={`−${displayMoney(mechanic.home_discount)} por mês`}
          note={`despesa ${displayPercent(mechanic.home_discount_rate, 0)} menor até ${displayMonthYear(mechanic.home_until)}`}
        />
      );
    case "left":
      return (
        <FigureCard
          label={label}
          value="Saiu de casa"
          note={`despesa cheia de ${displayMoney(mechanic.full_expense)} por mês`}
        />
      );
    case "expired":
      return (
        <FigureCard
          label={label}
          value="Sem desconto"
          note={`o prazo acabou em ${displayMonthYear(mechanic.home_until)}`}
        />
      );
  }
}

type StepRowProps = { step: GraduateStep; position: number; action: ReactNode };

/** Uma linha da escada: o marcador, o degrau com o que ele custa, o andamento e o múltiplo ao concluir. */
function StepRow({ step, position, action }: StepRowProps) {
  const text = STEP_TEXTS[step.step];
  const done = step.status === "done";
  const current = step.status === "current";
  const cost =
    step.stipend !== null
      ? `bolsa de ${displayMoney(step.stipend)} no lugar do salário`
      : step.tuition !== null
        ? `mensalidade de ${displayMoney(step.tuition)} · trabalha junto`
        : null;
  const details = [
    done && step.concluded_on ? `concluída em ${displayMonthYear(step.concluded_on)}` : null,
    done ? null : cost,
    !done && step.unemployment_discount ? "com o desconto do desemprego" : null,
    current && step.ends_on ? `conclui em ${displayMonthYear(step.ends_on)}` : null,
  ].filter((part) => part !== null);

  return (
    <li className={cn("grid grid-cols-[auto_1fr_auto] items-start gap-3 px-5 py-2.75", current && "bg-primary/5")}>
      <span
        className={cn(
          "flex size-6 items-center justify-center rounded-full text-xs font-bold",
          done && "bg-success text-card",
          current && "bg-primary text-card",
          !done && !current && "bg-muted text-secondary-foreground",
        )}
      >
        {done ? <Check className="size-3.5" aria-label="concluído" /> : position}
      </span>
      <div className="grid gap-1">
        <span className="text-[13px] font-semibold">
          {text.label}
          {current && step.months_done !== null
            ? ` · ${step.months_done} de ${step.months} meses`
            : step.months > 0 && !done
              ? ` · ${displayStepDuration(step.months)}`
              : ""}
        </span>
        {details.length > 0 && <span className="text-xs text-muted-foreground">{details.join(" · ")}</span>}
        {current && step.months_done !== null && (
          <Progress value={(step.months_done / step.months) * 100} size="md" className="max-w-80" />
        )}
      </div>
      <div className="flex items-center gap-3">
        {action}
        <span className="text-right font-mono text-[13px] tracking-tight">{displayMultiple(step.final_multiple)}</span>
      </div>
    </li>
  );
}
