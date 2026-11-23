import { Kpi } from "@/shared/components/kpi";
import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import { ProfessionTags } from "@/shared/components/profession-tags";
import { Card, CardContent } from "@/shared/components/ui/card";
import { PROFESSION_INCOME } from "@/shared/lib/life-metrics";
import { PROFESSIONS, type RoomRules, visibleProfession } from "@/shared/lib/professions";
import { displayMoney, displayPercent, displaySignedPercent } from "@/shared/lib/utils/display";
import type { ProfessionPage } from "@/types";
import { HEALTH_COST, LAYOFF_CHANCE, REAL_RAISE } from "../lib/profession-metrics";

// A parte da renda que a mecânica da profissão soma ao salário
const MECHANIC_INCOME_NAMES: Partial<Record<ProfessionPage["profession"], string>> = {
  BROKER: "comissão",
  CLT: "hora extra",
  OFFERS_BANKER: "comissão",
  RETIREE: "renda vitalícia",
};

// O que explica a renda quando a profissão não sobe pelo IPCA
const UNINDEXED_NOTES: Partial<Record<ProfessionPage["profession"], string>> = {
  FREELANCER: "a renda sobe pelo preço que você cobra",
  LANDLORD: "o aluguel se reajusta pelo IGP-M a cada 12 meses de contrato",
};

// O que compõe a renda do mês de quem não vive de salário
const INCOME_NOTES: Partial<Record<ProfessionPage["profession"], string>> = {
  LANDLORD: "a soma dos aluguéis dos imóveis alugados",
};

const RAISE_NOTES: Record<ProfessionPage["header"]["real_raise_source"], string> = {
  GDP_SHARE: "o próximo aumento, puxado pelo PIB",
  SERVANTS: "decidido pelo governo da sala",
  RETIREES: "decidido pelo governo da sala",
  NONE: "a renda só sobe com o IPCA",
};

/** O reajuste real é verde acima de zero, vermelho abaixo e neutro sem reajuste ou em zero. */
function raiseTone(raise: ProfessionPage["header"]["real_raise"]) {
  if (raise === null || Number(raise) === 0) return "default";
  return Number(raise) > 0 ? "success" : "destructive";
}

type ProfessionHeaderProps = {
  page: ProfessionPage;
  match: RoomRules;
};

/** Cabeçalho da página: a profissão, as regras dela na sala e os quatro números que decidem a renda. */
export function ProfessionHeader({ page, match }: ProfessionHeaderProps) {
  const { profession, header } = page;
  const { tags } = visibleProfession(profession, match);
  const { name, icon: Icon, description } = PROFESSIONS[profession];
  const mechanicName = MECHANIC_INCOME_NAMES[profession];
  const salary = Number(header.income) - Number(header.mechanic_income);
  const layoffMultiple = header.layoff_factor;
  const { mechanic } = page;
  // O Empreendedor mostra o lucro e quanto dele volta para a empresa
  const reinvested = mechanic.kind === "entrepreneur" && Number(mechanic.reinvested) > 0 ? mechanic.reinvested : null;

  return (
    <Card>
      <CardContent>
        <div className="grid gap-5">
          {/* Profissão */}
          <div className="flex items-start gap-4">
            <span className="inline-flex size-12 shrink-0 items-center justify-center rounded-xl bg-info-soft text-primary [&>svg]:size-6">
              <Icon />
            </span>
            <div className="grid min-w-0 flex-1 gap-2">
              <div className="grid gap-0.5">
                <h1 className="text-[22px] leading-tight font-bold">{name}</h1>
                <p className="max-w-3xl text-sm text-muted-foreground">{description}</p>
              </div>
              {tags.length > 0 && (
                <span className="flex flex-wrap items-center gap-x-2 gap-y-1">
                  <span className="text-[13px] text-muted-foreground">Afetado por</span>
                  <ProfessionTags profession={profession} tags={tags} salary={Number(match.monthly_salary)} />
                </span>
              )}
            </div>
          </div>

          {/* Os quatro números */}
          <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
            <Kpi
              label={
                <>
                  Renda do mês <MetricHint metric={PROFESSION_INCOME} />
                </>
              }
              value={displayMoney(header.income)}
              note={
                reinvested
                  ? `o lucro do mês, e ${displayMoney(reinvested)} volta para a empresa`
                  : mechanicName && Number(header.mechanic_income) > 0
                    ? `salário ${displayMoney(salary)} + ${mechanicName} ${displayMoney(header.mechanic_income)}`
                    : (INCOME_NOTES[profession] ?? "o salário do mês, já com o reajuste")
              }
            />
            <Kpi
              label={<MetricLabel metric={REAL_RAISE} />}
              value={header.real_raise === null ? "—" : `${displaySignedPercent(header.real_raise, 1)} ao ano`}
              note={
                header.inflation_indexed
                  ? RAISE_NOTES[header.real_raise_source]
                  : (UNINDEXED_NOTES[profession] ?? "esta partida não corrige pelo IPCA")
              }
              tone={raiseTone(header.real_raise)}
            />
            <Kpi
              label={<MetricLabel metric={LAYOFF_CHANCE} />}
              value={layoffMultiple === null ? "Sem risco" : LAYOFF_CHANCE.format(layoffMultiple)}
              note={
                layoffMultiple === null
                  ? "esta profissão não perde a renda por demissão"
                  : `desemprego de ${displayPercent(header.unemployment, 1)} contra ${displayPercent(header.neutral_unemployment, 0)} neutro`
              }
              tone={layoffMultiple !== null && Number(layoffMultiple) > 1 ? "destructive" : "default"}
            />
            <Kpi
              label={<MetricLabel metric={HEALTH_COST} />}
              value={HEALTH_COST.format(header.health_multiple)}
              note={
                Number(header.health_multiple) > Number(header.health_multiple_base)
                  ? "a hora extra dobra o custo"
                  : "o normal"
              }
              tone={Number(header.health_multiple) > Number(header.health_multiple_base) ? "warning" : "default"}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
