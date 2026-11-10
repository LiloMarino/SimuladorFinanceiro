import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
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
        <Select
          value={sector}
          items={{
            ...(noneLabel ? { [NO_SECTOR]: noneLabel } : {}),
            ...Object.fromEntries(sectors.map((candidate) => [candidate.name, candidate.name])),
          }}
          onValueChange={(value) => value && onChange(value, WHOLE_SECTOR)}
        >
          <SelectTrigger size="lg" className="w-full" aria-label={label}>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {noneLabel && <SelectItem value={NO_SECTOR}>{noneLabel}</SelectItem>}
            {sectors.map((candidate) => (
              <SelectItem key={candidate.name} value={candidate.name}>
                {candidate.name} · {candidate.assets} ativos
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {option && (
          <FieldDescription>
            {displayList(option.tickers)}. Também dá para escolher só um segmento do setor.
          </FieldDescription>
        )}
      </Field>

      {option && option.segments.length > 1 && (
        <Field>
          <FieldLabel>Segmento</FieldLabel>
          <Select
            value={segment}
            items={{
              [WHOLE_SECTOR]: "O setor inteiro",
              ...Object.fromEntries(option.segments.map((candidate) => [candidate.name, candidate.name])),
            }}
            onValueChange={(value) => value && onChange(sector, value)}
          >
            <SelectTrigger size="lg" className="w-full" aria-label="Segmento">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={WHOLE_SECTOR}>O setor inteiro · {option.assets} ativos</SelectItem>
              {option.segments.map((candidate) => (
                <SelectItem key={candidate.name} value={candidate.name}>
                  {candidate.name} · {candidate.assets} ativos
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
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
