import { useState, type ReactNode } from "react";
import { ArrowRight, Info } from "lucide-react";
import { Link } from "react-router-dom";
import { MetricHint } from "@/shared/components/metric-hint";
import { Button } from "@/shared/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { Slider } from "@/shared/components/ui/slider";
import { cn } from "@/shared/lib/utils";
import {
  displayMoney,
  displayNumber,
  displayPercent,
  displayShortDate,
  displaySignedMoney,
  displaySignedPercent,
} from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { useLockExchange } from "../hooks/mutations/useLockExchange";
import { useSetExportMix } from "../hooks/mutations/useSetExportMix";
import { DOLLAR_CHANGE, EXPORT_MIX, GDP_12M, LOCKED_DOLLAR } from "../lib/profession-metrics";
import { MechanicBlock } from "./mechanic-block";
import { PROFESSION_HISTORY_ID } from "./profession-history";

type ExporterMechanic = Extract<ProfessionMechanic, { kind: "exporter" }>;
type ExporterBlockProps = { mechanic: ExporterMechanic };
type LockTerm = number;

// A fatia da receita que a trava cobre começa em metade e o prazo no mais longo
const DEFAULT_LOCK_PERCENT = 50;
const DEFAULT_LOCK_TERM: LockTerm = 12;

const dollarText = (value: string) => `R$ ${displayNumber(value, 4)}`;

/** "Sua mecânica: trava de câmbio e mix" do Exportador: a trava e o mix lado a lado. */
export function ExporterBlock({ mechanic }: ExporterBlockProps) {
  const lockExchange = useLockExchange();
  // Nulo mostra o que o servidor devolveu; o jogador só guarda o que escolheu
  const [chosenPercent, setChosenPercent] = useState<number | null>(null);
  const [chosenTerm, setChosenTerm] = useState<LockTerm | null>(null);
  const percent = chosenPercent ?? DEFAULT_LOCK_PERCENT;
  const term = chosenTerm ?? DEFAULT_LOCK_TERM;
  const { lock } = mechanic;
  const option = mechanic.lock_options.find((candidate) => candidate.months === term);
  const losing = lock !== null && Number(lock.dollar_gap) < 0;

  return (
    <MechanicBlock
      title="Sua mecânica: trava de câmbio e mix"
      description={describe(lock, losing)}
      status={mechanic.status}
      action={
        lock ? (
          <Button variant="outline" nativeButton={false} render={<Link to="/economy" />}>
            Ver o dólar futuro
            <ArrowRight />
          </Button>
        ) : (
          <Button
            disabled={lockExchange.isPending}
            onClick={() => lockExchange.mutate({ share: percent / 100, months: term })}
          >
            Travar {percent}% por {term} meses
          </Button>
        )
      }
      links={[
        { label: "Carteira", to: "/portfolio" },
        { label: "Histórico da profissão", anchor: PROFESSION_HISTORY_ID },
      ]}
    >
      {lock ? (
        <ActiveLock lock={lock} dollar={mechanic.dollar} losing={losing} />
      ) : (
        <LockOffer
          mechanic={mechanic}
          percent={percent}
          term={term}
          lockedDollar={option?.locked_dollar}
          onPercentChange={setChosenPercent}
          onTermChange={setChosenTerm}
        />
      )}
      <MixStrip mechanic={mechanic} />
    </MechanicBlock>
  );
}

function describe(lock: ExporterMechanic["lock"], losing: boolean) {
  if (!lock) return "Nenhuma trava agora: a receita exportada segue o dólar do dia.";
  if (losing) return "O dólar subiu depois da trava.";
  return "Trave o dólar de parte da receita e escolha quanto vende para fora.";
}

type ActiveLockProps = {
  lock: NonNullable<ExporterMechanic["lock"]>;
  dollar: string;
  losing: boolean;
};

function ActiveLock({ lock, dollar, losing }: ActiveLockProps) {
  const gap = displayNumber(Math.abs(Number(lock.dollar_gap)), 4);
  const gainLoss = Number(lock.gain) < 0;
  const share = displayPercent(lock.share, 0);
  const expires = displayShortDate(lock.expires_on);

  return (
    <div className="grid gap-3">
      {/* Os números da trava */}
      <div className="grid gap-3 md:grid-cols-3">
        <FigureCard
          label={
            <span className="inline-flex items-center gap-1">
              Trava ativa <MetricHint metric={LOCKED_DOLLAR} />
            </span>
          }
          value={dollarText(lock.locked_dollar)}
          note={`${share} da receita · ${lock.months} meses`}
        />
        <FigureCard
          label="Dólar hoje"
          value={dollarText(dollar)}
          note={`a trava paga R$ ${gap} ${losing ? "a menos" : "a mais"} por dólar`}
        />
        <FigureCard
          label={losing ? "Resultado da trava até agora" : "Ganho da trava até agora"}
          value={`${gainLoss ? "" : "+"}${displaySignedMoney(lock.gain)}`}
          valueClassName={gainLoss ? "text-destructive" : "text-success"}
          note={`${lock.paid_months} de ${lock.months} meses, contra o dólar de hoje`}
        />
      </div>
      {/* O que a trava significa */}
      <div className="grid gap-1.5 text-[13px]">
        {losing ? (
          <>
            <Remark>
              A trava vale até <b className="font-semibold">{expires}</b> e não se desfaz antes.
            </Remark>
            <Remark>
              {Number(lock.share) < 1 && "A parte solta da receita ganhou com a alta. "}A trava protege da queda e abre
              mão da alta: é o preço da previsibilidade.
            </Remark>
          </>
        ) : (
          <Remark>
            A trava vale até <b className="font-semibold">{expires}</b> e não se desfaz antes: se o dólar subir acima de{" "}
            {dollarText(lock.locked_dollar)}, a parte travada recebe menos que a solta.
          </Remark>
        )}
        <Remark>Uma trava por vez. A próxima se contrata quando esta vencer.</Remark>
      </div>
    </div>
  );
}

type LockOfferProps = {
  mechanic: ExporterMechanic;
  percent: number;
  term: LockTerm;
  lockedDollar: string | undefined;
  onPercentChange: (value: number) => void;
  onTermChange: (value: LockTerm) => void;
};

function LockOffer({ mechanic, percent, term, lockedDollar, onPercentChange, onTermChange }: LockOfferProps) {
  const monthly = (Number(mechanic.exported_revenue) * percent) / 100;
  const coverage = percent === 50 ? "na metade da receita" : `em ${percent}% da receita`;

  return (
    <div className="grid gap-3">
      {/* Quanto da receita travar */}
      <div className="grid gap-2">
        <span className="flex items-center gap-1 text-sm font-medium">
          Quanto da receita travar <MetricHint metric={LOCKED_DOLLAR} />
        </span>
        <div className="grid grid-cols-[1fr_auto] items-center gap-x-4">
          <Slider
            aria-label="Quanto da receita exportada travar"
            min={1}
            max={100}
            step={1}
            value={percent}
            onValueChange={onPercentChange}
          />
          <span className="font-mono text-[13px]">
            <b className="font-semibold">{percent}%</b> · {displayMoney(monthly)} por mês
          </span>
        </div>
        <span className="text-right text-xs text-muted-foreground">até 100%</span>
      </div>
      {/* Prazo */}
      <RadioGroup
        className="md:grid-cols-2"
        value={String(term)}
        onValueChange={(value) => onTermChange(Number(value))}
      >
        {mechanic.lock_options.map((option) => (
          <TermOption
            key={option.months}
            months={option.months}
            dollar={option.locked_dollar}
            selected={option.months === term}
          />
        ))}
      </RadioGroup>
      {/* O que a trava significa */}
      <div className="grid gap-1.5 text-[13px]">
        {lockedDollar && (
          <Remark>
            Travando <b className="font-semibold">{percent}%</b> por <b className="font-semibold">{term} meses</b> a{" "}
            <b className="font-mono font-semibold">{dollarText(lockedDollar)}</b>, cada mês recebe esse dólar {coverage}
            , suba ou caia o dólar.
          </Remark>
        )}
        <Remark>Sem saída antes do vencimento.</Remark>
      </div>
    </div>
  );
}

type TermOptionProps = { months: number; dollar: string; selected: boolean };

function TermOption({ months, dollar, selected }: TermOptionProps) {
  return (
    <label
      className={cn(
        "grid cursor-pointer grid-cols-[auto_1fr_auto] items-center gap-x-2.5 gap-y-0.5 rounded-[10px] border px-3 py-2.5 text-[13px]",
        selected && "border-primary bg-info-soft/60 ring-1 ring-primary",
      )}
    >
      <RadioGroupItem value={String(months)} className="row-span-2" />
      <b className="font-semibold">{months} meses</b>
      <span className="font-mono font-semibold">{dollarText(dollar)}</span>
      <span className="col-span-2 col-start-2 text-xs text-muted-foreground">
        {months === 6 ? "dólar de hoje × (1 + CDI) ÷ (1 + Fed Funds) em 6 meses" : "o mesmo cálculo em 12 meses"}
      </span>
    </label>
  );
}

function MixStrip({ mechanic }: ExporterBlockProps) {
  const setMix = useSetExportMix();
  // Nulo mostra a fração que o servidor guarda; o jogador só guarda o que escolheu
  const [chosen, setChosen] = useState<number | null>(null);
  const serverPercent = Math.round(Number(mechanic.export_share) * 100);
  const percent = chosen ?? serverPercent;
  const canSubmit = mechanic.can_change_mix && percent !== serverPercent && !setMix.isPending;

  return (
    <div className="grid gap-2 border-t pt-4">
      <span className="flex items-center gap-1 text-sm font-semibold">
        Mix de exportação <MetricHint metric={EXPORT_MIX} />
      </span>
      <div className="grid items-center gap-x-6 gap-y-2 md:grid-cols-[1fr_auto]">
        <div className="grid gap-1.5">
          <Slider
            aria-label="Fração da receita exportada"
            min={0}
            max={100}
            step={1}
            value={percent}
            disabled={!mechanic.can_change_mix}
            onValueChange={setChosen}
          />
          <div className="flex flex-wrap justify-between gap-x-4 text-xs text-muted-foreground">
            <span>
              <b className="font-mono font-semibold text-foreground">{percent}%</b> exportado · segue o dólar
            </span>
            <span>
              <b className="font-mono font-semibold text-foreground">{100 - percent}%</b> no Brasil · segue o PIB
            </span>
          </div>
        </div>
        <div className="grid justify-items-start gap-1 md:justify-items-end">
          <Button
            variant="outline"
            disabled={!canSubmit}
            onClick={() => setMix.mutate({ share: percent / 100 }, { onSuccess: () => setChosen(null) })}
          >
            Mudar o mix
          </Button>
          <span className="text-xs text-muted-foreground">
            {mechanic.next_mix_change
              ? `próxima mudança em ${displayShortDate(mechanic.next_mix_change)}`
              : "uma mudança por trimestre"}
          </span>
        </div>
      </div>
      <p className="text-[13px] text-muted-foreground">
        Parte exportada: dólar 12 meses <b className="font-mono">{displaySignedPercent(mechanic.dollar_change, 1)}</b>{" "}
        <MetricHint metric={DOLLAR_CHANGE} />, fator <Factor value={mechanic.exported_factor} />. Parte no Brasil: PIB{" "}
        <b className="font-mono">{displayPercent(mechanic.growth, 1)}</b> <MetricHint metric={GDP_12M} />, fator{" "}
        <Factor value={mechanic.domestic_factor} />. Juntas: <Factor value={mechanic.mix_factor} /> a renda base.
      </p>
    </div>
  );
}

function Factor({ value }: { value: string }) {
  return <b className="font-mono font-bold text-foreground">{displayNumber(value, 2)}×</b>;
}

type FigureCardProps = {
  label: ReactNode;
  value: string;
  note: string;
  valueClassName?: string;
};

function FigureCard({ label, value, note, valueClassName }: FigureCardProps) {
  return (
    <div className="grid content-start gap-1 rounded-[10px] border p-4">
      <span className="text-[13px] text-muted-foreground">{label}</span>
      <b className={cn("font-mono text-[17px] font-semibold", valueClassName)}>{value}</b>
      <span className="text-xs text-muted-foreground">{note}</span>
    </div>
  );
}

function Remark({ children }: { children: ReactNode }) {
  return (
    <p className="flex items-start gap-2">
      <Info className="mt-0.5 size-3.5 shrink-0 text-muted-foreground" />
      <span>{children}</span>
    </p>
  );
}
