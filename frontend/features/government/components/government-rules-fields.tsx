import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Switch } from "@/shared/components/ui/switch";
import type { GovernmentRules } from "@/types";

export function GovernmentRulesFields({ value, onChange, disabled }: {
  value: GovernmentRules; onChange: (rules: GovernmentRules) => void; disabled: boolean;
}) {
  const patch = (update: Partial<GovernmentRules>) => onChange({ ...value, ...update });
  return <fieldset disabled={disabled} className="grid gap-4 rounded-lg border p-4">
    <legend className="px-2 font-semibold">Expansões · Governo</legend>
    <Label><Switch checked={value.enabled ?? false} onCheckedChange={enabled => patch({ enabled })} /> Partidos, eleições e governo</Label>
    <p className="text-sm text-muted-foreground">Exige ao menos 5 anos. Quem quiser entra na política; os demais continuam investindo. O presidente terá a carteira congelada durante o mandato.</p>
    {value.enabled && <>
      <div className="grid gap-3 sm:grid-cols-2">
        <Label className="grid">Dificuldade do computador
          <select className="h-9 rounded-md border bg-background px-3" value={value.difficulty ?? "medium"} onChange={e => patch({ difficulty: e.target.value as GovernmentRules["difficulty"] })}>
            <option value="easy">Fácil · 0,5× a verba média</option><option value="medium">Média · 1× a verba média</option><option value="hard">Difícil · 1,5× a verba média</option>
          </select>
        </Label>
        <Label className="grid">Ranking que decide a partida
          <select className="h-9 rounded-md border bg-background px-3" value={value.ranking ?? "individual"} onChange={e => patch({ ranking: e.target.value as GovernmentRules["ranking"] })}>
            <option value="individual">Individual · critério financeiro da partida</option><option value="parties">Partidos · soma dos patrimônios</option>
          </select>
        </Label>
      </div>
      <Label><Switch checked={value.manual_selic ?? false} onCheckedChange={manual_selic => patch({ manual_selic })} /> SELIC controlável pelo presidente</Label>
      <p className="text-xs text-muted-foreground">Desligada: Banco Central reage à inflação. Ligada: decisões com intervalo de 45 dias, limite por decisão e efeito inflacionário com atraso.</p>
      <div className="grid gap-3 sm:grid-cols-2">
        <Label className="grid">Piso de aprovação (%)<Input type="number" min={5} max={40} value={value.impeachment_floor ?? 25} onChange={e => patch({ impeachment_floor: Number(e.target.value) })} /></Label>
        <Label className="grid">Meses abaixo do piso<Input type="number" min={2} max={12} value={value.impeachment_months ?? 3} onChange={e => patch({ impeachment_months: Number(e.target.value) })} /></Label>
      </div>
      <p className="text-xs text-muted-foreground">Vitória por partidos exige partida clássica com jogadores individuais. Sem partidos humanos, vale o ranking individual. Parâmetros iniciais: R$ 8 mil/mês rendem +1,4 de alcance; R$ 16 mil rendem +2. A regra econômica e os perfis hipotéticos ficam disponíveis em Governo › Impactos.</p>
    </>}
  </fieldset>;
}
