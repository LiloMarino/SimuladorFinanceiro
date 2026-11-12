import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { OptionSelect } from "@/shared/components/option-select";
import { displayList } from "@/shared/lib/utils/display";
import type { GovernmentPanel } from "@/types";
import { NO_SECTOR, WHOLE_SECTOR } from "../lib/sector-address";

type SectorSegmentSelectProps = {
  sectors: GovernmentPanel["sectors"];
  sector: string;
  segment: string;
  onChange: (sector: string, segment: string) => void;
  label?: string;
  /** Com o texto, a lista ganha a opção de não apontar para setor nenhum (valor NO_SECTOR) */
  noneLabel?: string;
  /** Complemento de "Só os N ativos desse segmento ...", dito pela medida que usa a lista */
  segmentScope?: string;
};

/** O setor e, quando o setor tem mais de um, o segmento: a escolha do alvo de uma medida, de uma obra ou de uma emenda. */
export function SectorSegmentSelect({
  sectors,
  sector,
  segment,
  onChange,
  label = "Setor",
  noneLabel,
  segmentScope = "entram na medida",
}: SectorSegmentSelectProps) {
  const option = sectors.find((candidate) => candidate.name === sector);
  const segmentOption = option?.segments.find((candidate) => candidate.name === segment);

  return (
    <>
      <Field>
        <FieldLabel>{label}</FieldLabel>
        <OptionSelect
          value={sector || null}
          options={[
            ...(noneLabel ? [{ value: NO_SECTOR, label: noneLabel }] : []),
            ...sectors.map((candidate) => ({
              value: candidate.name,
              label: `${candidate.name} · ${candidate.assets} ativos`,
              triggerLabel: candidate.name,
            })),
          ]}
          onChange={(value) => onChange(value, WHOLE_SECTOR)}
          aria-label={label}
          className="w-full"
        />
        {option && (
          <FieldDescription>
            {displayList(option.tickers)}. Também dá para escolher só um segmento do setor.
          </FieldDescription>
        )}
      </Field>

      {option && option.segments.length > 1 && (
        <Field>
          <FieldLabel>Segmento</FieldLabel>
          <OptionSelect
            value={segment}
            options={[
              {
                value: WHOLE_SECTOR,
                label: `O setor inteiro · ${option.assets} ativos`,
                triggerLabel: "O setor inteiro",
              },
              ...option.segments.map((candidate) => ({
                value: candidate.name,
                label: `${candidate.name} · ${candidate.assets} ativos`,
                triggerLabel: candidate.name,
              })),
            ]}
            onChange={(value) => onChange(sector, value)}
            aria-label="Segmento"
            className="w-full"
          />
          {segmentOption && (
            <FieldDescription>
              Só os {segmentOption.assets} ativos desse segmento {segmentScope}.
            </FieldDescription>
          )}
        </Field>
      )}
    </>
  );
}
