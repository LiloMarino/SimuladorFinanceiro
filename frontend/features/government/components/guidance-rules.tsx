import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import type { ElectionPanel } from "@/types";
import { useSetGuidanceRule } from "../hooks/mutations/useSetGuidanceRule";
import { VALUE_INFO } from "@/shared/lib/party-flags";

type GuidanceRulesProps = {
  rules: NonNullable<ElectionPanel["my_party"]>["guidance"];
  /** Só o líder muda a orientação padrão */
  isLeader: boolean;
  abbr: string;
};

/** A orientação padrão da bancada, um valor por vez: vale na votação em que o líder não orienta. */
export function GuidanceRules({ rules, isLeader, abbr }: GuidanceRulesProps) {
  const set = useSetGuidanceRule();

  return (
    <div className="grid gap-1.5">
      <span className="text-sm font-medium">Orientação padrão da bancada</span>
      <div className="grid">
        {rules.map((rule) => (
          <div key={rule.value} className="flex items-center justify-between gap-3 border-t py-1.5 text-[13px]">
            <span>{VALUE_INFO[rule.value].label}</span>
            <ToggleGroup
              variant="segmented"
              aria-label={`Orientação do ${abbr} nas medidas que puxam ${VALUE_INFO[rule.value].label}`}
              value={[rule.yes ? "yes" : "no"]}
              disabled={!isLeader || set.isPending}
              onValueChange={(values) => values[0] && set.mutate({ value: rule.value, yes: values[0] === "yes" })}
            >
              <ToggleGroupItem value="yes">Sim</ToggleGroupItem>
              <ToggleGroupItem value="no">Não</ToggleGroupItem>
            </ToggleGroup>
          </div>
        ))}
      </div>
      <span className="text-xs text-muted-foreground">
        {isLeader
          ? `Quando você não orienta uma votação, o ${abbr} vota Sim nas medidas que mais puxam um valor marcado Sim, e Não nas outras.`
          : `Só o líder muda. Quando ele não orienta uma votação, o ${abbr} vota por esta lista.`}
      </span>
    </div>
  );
}
