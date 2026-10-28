import { useState } from "react";
import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Slider } from "@/shared/components/ui/slider";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayList, displayMoneyCompact } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import type { PromisesPanel } from "@/types";
import { type GeneralKind, generalLabel, isGeneral, percentLabel, rateToFraction } from "../lib/government";
import type { PromiseDraft, PromiseOption } from "../lib/promises";

const WHOLE_SECTOR = "all";
// Metade de um ponto percentual por passo do controle
const SLIDER_STEP = 0.5;

type Mode = "general" | "sector";

type PromiseEditorProps = {
  draft: PromiseDraft;
  panel: PromisesPanel;
  /** As medidas que as outras promessas da lista já ocupam */
  taken: Set<string>;
  disabled: boolean;
  onChange: (draft: PromiseDraft) => void;
};

/** Edita uma promessa da lista: um imposto geral com alvo, ou a isenção de um setor ou segmento. */
export function PromiseEditor({ draft, panel, taken, disabled, onChange }: PromiseEditorProps) {
  const mode: Mode = draft.sector === null ? "general" : "sector";
  const option = panel.options.find((candidate) => candidate.kind === draft.kind);

  const changeMode = (next: Mode) => {
    if (next === mode) return;
    if (next === "sector") {
      onChange({ kind: "SECTOR_EXEMPT", target: null, sector: panel.sectors[0]?.name ?? null, segment: null });
      return;
    }
    const first = panel.options.find((candidate) => !taken.has(candidate.kind)) ?? panel.options[0];
    if (first) onChange({ kind: first.kind, target: first.baseline, sector: null, segment: null });
  };

  return (
    <div className="grid gap-3.5">
      <ToggleGroup
        variant="segmented"
        aria-label="Tipo de promessa"
        className="w-full"
        value={[mode]}
        disabled={disabled}
        onValueChange={(values) => values[0] && changeMode(values[0] as Mode)}
      >
        <ToggleGroupItem value="general" className="flex-1">
          Imposto geral
        </ToggleGroupItem>
        <ToggleGroupItem value="sector" className="flex-1">
          Isentar um setor
        </ToggleGroupItem>
      </ToggleGroup>

      {mode === "general" && option && (
        <GeneralFields
          draft={draft}
          option={option}
          panel={panel}
          taken={taken}
          disabled={disabled}
          onChange={onChange}
        />
      )}
      {mode === "sector" && <SectorFields draft={draft} panel={panel} disabled={disabled} onChange={onChange} />}
    </div>
  );
}

type GeneralFieldsProps = Omit<PromiseEditorProps, "disabled"> & { option: PromiseOption; disabled: boolean };

function GeneralFields({ draft, option, panel, taken, disabled, onChange }: GeneralFieldsProps) {
  const kinds = panel.options.filter((candidate): candidate is typeof candidate & { kind: GeneralKind } =>
    isGeneral(candidate.kind),
  );

  return (
    <div className="grid gap-3.5 sm:grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)]">
      <Field>
        <FieldLabel>Medida</FieldLabel>
        <Select
          value={draft.kind}
          disabled={disabled}
          items={Object.fromEntries(
            kinds.map((candidate) => [candidate.kind, generalLabel(candidate.kind, candidate.baseline)]),
          )}
          onValueChange={(value) => {
            const next = kinds.find((candidate) => candidate.kind === value);
            if (next) onChange({ kind: next.kind, target: next.baseline, sector: null, segment: null });
          }}
        >
          <SelectTrigger size="lg" className="w-full" aria-label="Medida">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {kinds.map((candidate) => (
              <SelectItem
                key={candidate.kind}
                value={candidate.kind}
                disabled={taken.has(candidate.kind) && candidate.kind !== draft.kind}
              >
                {generalLabel(candidate.kind, candidate.baseline)}
                {taken.has(candidate.kind) && candidate.kind !== draft.kind && (
                  <span className="text-xs text-muted-foreground">já prometida</span>
                )}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <FieldDescription>Uma medida que o governo pode propor, com o alvo que a chapa promete.</FieldDescription>
      </Field>

      {/* O controle remonta ao trocar de medida: o texto digitado nasce do alvo dela */}
      <TargetField key={draft.kind} draft={draft} option={option} disabled={disabled} onChange={onChange} />
    </div>
  );
}

type TargetFieldProps = {
  draft: PromiseDraft;
  option: PromiseOption;
  disabled: boolean;
  onChange: (draft: PromiseDraft) => void;
};

const percentText = (fraction: string | null) =>
  fraction === null ? "" : String(Math.round(Number(fraction) * 1000) / 10).replace(".", ",");

function TargetField({ draft, option, disabled, onChange }: TargetFieldProps) {
  const isMoney = option.kind === "STOCK_EXEMPTION";
  const [text, setText] = useState(() =>
    isMoney ? formatMoney(String(Math.round(Number(draft.target ?? 0) * 100))) : percentText(draft.target),
  );

  const set = (target: string | null) => onChange({ ...draft, target });

  if (isMoney) {
    return (
      <Field>
        <FieldLabel htmlFor="promise-limit">Novo limite por mês</FieldLabel>
        <Input
          id="promise-limit"
          numeric
          inputMode="decimal"
          placeholder="R$ 0,00"
          disabled={disabled}
          value={text}
          onChange={(event) => {
            const next = formatMoney(event.target.value);
            setText(next);
            const value = normalizeNumberString(next);
            set(value === "" ? null : value);
          }}
        />
        <FieldDescription>Hoje a isenção vai {`até ${displayMoneyCompact(option.baseline)}/mês`}.</FieldDescription>
      </Field>
    );
  }

  const limit = Number(option.limit ?? 1) * 100;
  const sliderValue = Math.min(Math.max(Number(draft.target ?? option.baseline) * 100, 0), limit);

  return (
    <Field>
      <div className="flex items-center justify-between">
        <FieldLabel htmlFor="promise-target">Alvo (%)</FieldLabel>
        <span className="text-xs text-muted-foreground">passo de {Number(option.step) * 100} pontos</span>
      </div>
      <div className="grid grid-cols-[minmax(0,1fr)_84px] items-center gap-3.5">
        <Slider
          aria-label="Alvo da promessa"
          min={0}
          max={limit}
          step={SLIDER_STEP}
          disabled={disabled}
          value={sliderValue}
          onValueChange={(next) => {
            const fraction = String(Math.round(next * 10) / 1000);
            setText(percentText(fraction));
            set(fraction);
          }}
        />
        <Input
          id="promise-target"
          numeric
          inputMode="decimal"
          disabled={disabled}
          value={text}
          onChange={(event) => {
            setText(event.target.value);
            set(rateToFraction(event.target.value));
          }}
        />
      </div>
      <FieldDescription>
        Hoje {percentLabel(option.baseline)}. Quanto maior o passo, mais rende agora e mais rejeição soma se não
        cumprir.
      </FieldDescription>
    </Field>
  );
}

type SectorFieldsProps = Omit<PromiseEditorProps, "taken">;

function SectorFields({ draft, panel, disabled, onChange }: SectorFieldsProps) {
  const sector = panel.sectors.find((candidate) => candidate.name === draft.sector);
  const segment = sector?.segments.find((candidate) => candidate.name === draft.segment);

  return (
    <div className="grid gap-3.5">
      <Field>
        <FieldLabel>Setor</FieldLabel>
        <Select
          value={draft.sector ?? ""}
          disabled={disabled}
          items={Object.fromEntries(panel.sectors.map((candidate) => [candidate.name, candidate.name]))}
          onValueChange={(value) => value && onChange({ ...draft, sector: value, segment: null })}
        >
          <SelectTrigger size="lg" className="w-full" aria-label="Setor">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {panel.sectors.map((candidate) => (
              <SelectItem key={candidate.name} value={candidate.name}>
                {candidate.name} · {candidate.assets} ativos
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {sector && <FieldDescription>{displayList(sector.tickers)}.</FieldDescription>}
      </Field>

      {sector && sector.segments.length > 1 && (
        <Field>
          <FieldLabel>Segmento</FieldLabel>
          <Select
            value={draft.segment ?? WHOLE_SECTOR}
            disabled={disabled}
            items={{
              [WHOLE_SECTOR]: "O setor inteiro",
              ...Object.fromEntries(sector.segments.map((candidate) => [candidate.name, candidate.name])),
            }}
            onValueChange={(value) => value && onChange({ ...draft, segment: value === WHOLE_SECTOR ? null : value })}
          >
            <SelectTrigger size="lg" className="w-full" aria-label="Segmento">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={WHOLE_SECTOR}>O setor inteiro · {sector.assets} ativos</SelectItem>
              {sector.segments.map((candidate) => (
                <SelectItem key={candidate.name} value={candidate.name}>
                  {candidate.name} · {candidate.assets} ativos
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {segment && (
            <FieldDescription>Só os {segment.assets} ativos desse segmento entram na promessa.</FieldDescription>
          )}
        </Field>
      )}
      <p className="text-xs text-muted-foreground">
        A promessa de setor é sim ou não: cumprida quando o setor passa a ser isento.
      </p>
    </div>
  );
}
