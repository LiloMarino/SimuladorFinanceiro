import { TriangleAlert } from "lucide-react";
import { InfoHint } from "@/shared/components/info-hint";
import { SpendingIcon } from "@/shared/components/spending-icon";
import { MarkedSlider } from "@/shared/components/marked-slider";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { SpendingRow } from "@/types";
import { SPENDING_KINDS, SPENDING_LABEL, type SpendingKind } from "@/shared/lib/spending-kinds";
import {
  checkValue,
  chipFits,
  chipLabel,
  chipValueText,
  outsideSentence,
  pointsOf,
  spendingUnit,
  spendingValue,
  stepChips,
  valueWindow,
  windowSentence,
} from "../lib/spending";

const SLIDER_STEP = { raise: 0.5, share: 0.05 };

type SpendingFormProps = {
  rows: SpendingRow[];
  kind: SpendingKind;
  onKindChange: (kind: SpendingKind) => void;
  valueText: string;
  onValueTextChange: (text: string) => void;
};

/** A escolha da medida de gasto e do valor novo: o campo, os atalhos de passo e a régua da janela que a medida alcança. */
export function SpendingForm({ rows, kind, onKindChange, valueText, onValueTextChange }: SpendingFormProps) {
  const row = rows.find((candidate) => candidate.kind === kind);
  const raise = kind === "SERVANT_RAISE" || kind === "RETIREE_RAISE";

  return (
    <>
      <Field>
        <FieldLabel>Medida</FieldLabel>
        <div className="grid grid-cols-2 gap-2">
          {SPENDING_KINDS.map((candidate) => {
            const candidateRow = rows.find((item) => item.kind === candidate);
            if (!candidateRow) return null;
            return (
              <KindCard
                key={candidate}
                kind={candidate}
                row={candidateRow}
                selected={candidate === kind}
                onSelect={() => onKindChange(candidate)}
              />
            );
          })}
        </div>
      </Field>

      {row && !row.pending && (
        <ValueField
          kind={kind}
          row={row}
          label={raise ? "Novo ganho real" : "Novo valor"}
          valueText={valueText}
          onValueTextChange={onValueTextChange}
        />
      )}

      {row?.pending && (
        <div className="flex items-start gap-2 rounded-lg border border-warning/30 bg-warning-soft/40 p-3 text-[13px]">
          <TriangleAlert className="mt-0.5 size-4 shrink-0 text-warning" />
          <span>
            {SPENDING_LABEL[kind]} já tem uma medida{" "}
            {row.pending.vote_date ? `na fila, com voto em ${displayDayMonth(row.pending.vote_date)}` : "a caminho"}. Só
            uma medida de cada tipo por vez: espere esta valer ou escolha outra.
          </span>
        </div>
      )}
    </>
  );
}

type KindCardProps = { kind: SpendingKind; row: SpendingRow; selected: boolean; onSelect: () => void };

function KindCard({ kind, row, selected, onSelect }: KindCardProps) {
  const queued = row.pending !== null;
  const atFloor = (kind === "SERVANT_RAISE" || kind === "RETIREE_RAISE") && Number(row.value) === 0;
  return (
    <button
      type="button"
      aria-pressed={selected}
      disabled={queued}
      onClick={onSelect}
      className={cn(
        "grid grid-cols-[auto_minmax(0,1fr)] items-center gap-2.5 rounded-lg border bg-card px-3 py-2.5 text-left transition-colors",
        selected ? "border-info bg-info-soft/40" : "hover:bg-subtle",
        queued && "cursor-not-allowed bg-subtle opacity-55 hover:bg-subtle",
      )}
    >
      <span
        className={cn(
          "grid size-7 place-items-center rounded-md",
          selected ? "bg-info-soft text-info" : "bg-muted text-muted-foreground",
        )}
      >
        <SpendingIcon kind={kind} className="size-4" />
      </span>
      <span className="grid min-w-0 gap-0.5">
        <span className="text-[13.5px] font-semibold">{SPENDING_LABEL[kind]}</span>
        <span className="text-xs text-muted-foreground">Hoje: {spendingValue(kind, row.value)}</span>
        {queued && row.pending && (
          <Badge variant="warning" size="sm" className="w-fit">
            na fila{row.pending.vote_date ? ` · vota em ${displayDayMonth(row.pending.vote_date)}` : ""}
          </Badge>
        )}
        {!queued && atFloor && (
          <Badge variant="secondary" size="sm" className="w-fit">
            no piso: só dá para subir
          </Badge>
        )}
      </span>
    </button>
  );
}

type ValueFieldProps = {
  kind: SpendingKind;
  row: SpendingRow;
  label: string;
  valueText: string;
  onValueTextChange: (text: string) => void;
};

function ValueField({ kind, row, label, valueText, onValueTextChange }: ValueFieldProps) {
  const check = checkValue(row, valueText);
  const window = valueWindow(row);
  const today = Number(row.value) * 100;
  const typed = Number(valueText.replace(",", "."));
  const sliderValue = Math.min(
    Math.max(Number.isFinite(typed) && valueText.trim() !== "" ? typed : today, window.min * 100),
    window.max * 100,
  );
  const step = kind === "SERVANT_RAISE" || kind === "RETIREE_RAISE" ? SLIDER_STEP.raise : SLIDER_STEP.share;
  const marks = rulerMarks(window.min * 100, today, window.max * 100);

  return (
    <Field data-invalid={check.status === "outside" || undefined}>
      <FieldLabel htmlFor="measure-spending-value">
        {label}
        <span className="font-normal text-muted-foreground"> · {spendingUnit(kind)}</span>
        <InfoHint label="Como o valor é lido">
          <div className="space-y-1 text-left">
            <p>
              {kind === "SERVANT_RAISE" || kind === "RETIREE_RAISE"
                ? "Ganho real é o quanto a folha sobe acima da inflação. Todo janeiro o salário (ou o benefício) sobe a inflação mais esse tanto."
                : "O valor é a fatia do PIB que o governo gasta com essa medida em um ano."}
            </p>
            <p>
              Uma medida só anda um passo: {pointsOf(row.step)} ponto
              {Number(row.step) <= 0.01 ? "" : "s"} para cima ou para baixo. Para ir mais longe, o presidente propõe
              outra medida depois que esta valer.
            </p>
          </div>
        </InfoHint>
      </FieldLabel>

      <div className="flex flex-wrap items-center gap-3">
        <Input
          id="measure-spending-value"
          numeric
          inputMode="decimal"
          placeholder={pointsOf(row.value)}
          className="w-28"
          aria-invalid={check.status === "outside" || undefined}
          value={valueText}
          onChange={(event) => onValueTextChange(event.target.value)}
        />
        <div className="flex gap-1.5">
          {stepChips(kind).map((points) => (
            <Button
              key={points}
              type="button"
              size="xs"
              variant="outline"
              disabled={!chipFits(row, points)}
              onClick={() => onValueTextChange(chipValueText(row, points))}
            >
              {chipLabel(points)}
            </Button>
          ))}
        </div>
      </div>

      <div className="mx-1.5 mt-1">
        <MarkedSlider
          aria-label={label}
          value={sliderValue}
          min={window.min * 100}
          max={window.max * 100}
          step={step}
          marks={marks}
          onValueChange={(value) => onValueTextChange(String(Math.round(value * 100) / 100).replace(".", ","))}
        />
      </div>

      {check.status === "outside" ? (
        <>
          <FieldError>{outsideSentence(kind, row, valueText)}</FieldError>
          <FieldDescription>Hoje {pointsOf(row.value)}%.</FieldDescription>
        </>
      ) : (
        <FieldDescription>{windowSentence(kind, row)}</FieldDescription>
      )}
    </Field>
  );
}

/** As marcas da régua: o piso, o valor de hoje e o teto da janela; encostado numa ponta, "hoje" ocupa o lugar do número. */
function rulerMarks(min: number, today: number, max: number) {
  const label = (value: number) => `${pointsOf(value / 100)}%`;
  if (today <= min)
    return [
      { value: min, label: `hoje · ${label(min)}` },
      { value: max, label: label(max) },
    ];
  if (today >= max)
    return [
      { value: min, label: label(min) },
      { value: max, label: `hoje · ${label(max)}` },
    ];
  return [
    { value: min, label: label(min) },
    { value: today, label: "hoje" },
    { value: max, label: label(max) },
  ];
}
