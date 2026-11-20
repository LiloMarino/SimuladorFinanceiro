import { InfoHint } from "@/shared/components/info-hint";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import {
  exchangeText,
  exitVoteNote,
  partnerFavor,
  partnerNote,
  ratioFormula,
  shortfallText,
  type AssemblyMerge,
} from "../lib/fund-merge";

type AssemblyMergeDetailsProps = { merge: AssemblyMerge };

/** O que a fusão faz: a troca de cotas, a saída de quem vota contra na incorporada e a votação da outra gestora. */
export function AssemblyMergeDetails({ merge }: AssemblyMergeDetailsProps) {
  const { mother, daughter } = merge;
  const partner = merge.is_mother ? daughter : mother;
  const shortfall = shortfallText(merge.shortfall);
  const formula = ratioFormula(daughter, mother, merge.ratio);

  return (
    <div className="grid gap-3">
      <div className="rounded-lg bg-background px-3.5 py-1">
        {/* Troca de cotas */}
        <KeyValueRow
          label={
            <span className="inline-flex items-center gap-1 text-xs font-medium text-muted-foreground">
              Relação de troca
              <InfoHint label="O que é a relação de troca">
                Quantas cotas da incorporada valem uma da incorporadora, pelo patrimônio por cota do dia da aprovação.
                Com R$ 50,00 por cota na incorporada e R$ 100,00 na incorporadora, 2 cotas da primeira viram 1 da
                segunda.
              </InfoHint>
            </span>
          }
          note={`Pelo patrimônio por cota do dia da aprovação${formula === null ? "" : `: ${formula}`}`}
          value={merge.ratio === null ? "—" : exchangeText(daughter.ticker, mother.ticker, merge.ratio)}
          valueClassName="font-medium"
        />
        {/* Saída de quem vota contra */}
        <KeyValueRow
          label={`Quem votar contra na ${daughter.name}`}
          note={exitVoteNote(daughter)}
          value="Sai pelo patrimônio por cota"
          valueClassName="font-medium"
        />
        {Number(merge.exit_quotas) > 0 && (
          <KeyValueRow
            label="Saem hoje"
            note="As cotas de quem já votou contra, pelo patrimônio por cota de hoje"
            value={`${displayQuantity(merge.exit_quotas)} cotas · ${displayMoney(merge.exit_amount)}`}
            valueClassName="font-medium"
          />
        )}
        {/* A outra assembleia */}
        <KeyValueRow
          label={`Assembleia da ${partner.name}`}
          note={partnerNote(merge)}
          value={partnerFavor(merge)}
          valueClassName="font-medium"
        />
      </div>
      {shortfall !== null && (
        <Alert variant="destructive">
          <AlertTitle>A fusão trava com os caixas de hoje</AlertTitle>
          <AlertDescription>{shortfall}</AlertDescription>
        </Alert>
      )}
    </div>
  );
}
