import { useState } from "react";
import { TriangleAlert } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Slider } from "@/shared/components/ui/slider";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { displayMoney, displayPercent, displaySignedMoney } from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { useSellCapital } from "../hooks/mutations/useSellCapital";
import { useSetReinvestShare } from "../hooks/mutations/useSetReinvestShare";
import { CAPITAL_INCOME, CAPITAL_SALE, COMPANY_CAPITAL, REINVEST_SHARE } from "../lib/profession-metrics";
import { FigureCard } from "./figure-card";
import { MechanicBlock } from "./mechanic-block";
import { PROFESSION_HISTORY_ID } from "./profession-history";

type EntrepreneurMechanic = Extract<ProfessionMechanic, { kind: "entrepreneur" }>;
type EntrepreneurBlockProps = { mechanic: EntrepreneurMechanic };

// A venda abre na opção do meio do caminho
const DEFAULT_SALE_SHARE = "0.25";

/** "Sua mecânica: reinvestimento" do Empreendedor: o capital da empresa, o que ele rende com o PIB, a fração do lucro que volta e a venda de parte. */
export function EntrepreneurBlock({ mechanic }: EntrepreneurBlockProps) {
  const { recession } = mechanic;

  return (
    <MechanicBlock
      title="Sua mecânica: reinvestimento"
      description={
        recession
          ? "Recessão: o capital está encolhendo."
          : "Parte do lucro volta para a empresa e vira capital, que rende com o PIB."
      }
      status={mechanic.status}
      links={[
        { label: "Carteira, linha Capital da empresa", to: "/portfolio" },
        { label: "Histórico da profissão", anchor: PROFESSION_HISTORY_ID },
      ]}
    >
      {/* Os números do capital */}
      <div className="grid gap-3 md:grid-cols-3">
        <FigureCard
          label={
            <span className="inline-flex items-center gap-1">
              Capital da empresa <MetricHint metric={COMPANY_CAPITAL} />
            </span>
          }
          value={displayMoney(mechanic.capital)}
          note={
            recession && mechanic.capital_months_ago !== null
              ? `era ${displayMoney(mechanic.capital_months_ago)} há 3 meses`
              : "conta no patrimônio, linha da carteira"
          }
        />
        <FigureCard
          label={
            <span className="inline-flex items-center gap-1">
              Renda do capital no mês <MetricHint metric={CAPITAL_INCOME} />
            </span>
          }
          value={`${Number(mechanic.income) > 0 ? "+" : ""}${displaySignedMoney(mechanic.income)}`}
          tone={
            Number(mechanic.income) > 0
              ? "success"
              : recession && Number(mechanic.income) < 0
                ? "destructive"
                : "default"
          }
          note={`${displayPercent(mechanic.rate, 1)} ao mês com o PIB 12 meses em ${displayPercent(mechanic.growth, 1)}`}
        />
        <FigureCard
          label="Lucro do mês"
          value={displayMoney(mechanic.profit)}
          note="a sua renda antes do reinvestimento"
        />
      </div>
      {/* O aviso da recessão */}
      {recession && (
        <Alert variant="warning">
          <TriangleAlert />
          <AlertDescription>
            <b className="font-semibold">
              {mechanic.negative_quarters > 0
                ? `O PIB está negativo há ${mechanic.negative_quarters} ${mechanic.negative_quarters === 1 ? "trimestre" : "trimestres"}.`
                : "O PIB de 12 meses está negativo."}
            </b>{" "}
            Cada real reinvestido agora encolhe. Baixar o reinvestimento para 0% ou vender uma parte protege o que já
            está na empresa.
          </AlertDescription>
        </Alert>
      )}
      <ReinvestRuler mechanic={mechanic} />
      <CapitalSale mechanic={mechanic} />
    </MechanicBlock>
  );
}

/** A régua da fração do lucro que volta para a empresa, que nasce na fração salva e só guarda o que o jogador mexeu. */
function ReinvestRuler({ mechanic }: EntrepreneurBlockProps) {
  const setShare = useSetReinvestShare();
  // Nulo mostra a fração que o servidor guarda; o jogador só guarda o que escolheu
  const [chosen, setChosen] = useState<number | null>(null);
  const savedPercent = Math.round(Number(mechanic.reinvest_share) * 100);
  const percent = chosen ?? savedPercent;
  // Na fração salva vale o que o servidor reinveste; na que o jogador mexe, a conta da régua
  const back = percent === savedPercent ? Number(mechanic.reinvested) : (Number(mechanic.profit) * percent) / 100;

  return (
    <div className="grid gap-2 border-y py-3">
      <span className="flex items-center gap-1.5 text-[13px] font-semibold">
        Quanto do lucro volta para a empresa <MetricHint metric={REINVEST_SHARE} />
      </span>
      <div className="grid items-center gap-x-6 gap-y-2 md:grid-cols-[1fr_auto]">
        <div className="grid gap-1.5">
          <Slider
            aria-label="Fração do lucro que volta para a empresa"
            min={0}
            max={100}
            step={1}
            value={percent}
            onValueChange={setChosen}
          />
          <div className="flex justify-between gap-x-4 text-xs text-muted-foreground">
            <span>
              <b className="font-mono font-semibold text-foreground">{percent}%</b> · {displayMoney(back)} volta,{" "}
              {displayMoney(Number(mechanic.profit) - back)} cai no caixa
            </span>
            <span>100%</span>
          </div>
        </div>
        <Button
          variant="outline"
          disabled={percent === savedPercent || setShare.isPending}
          onClick={() => setShare.mutate({ share: String(percent / 100) }, { onSuccess: () => setChosen(null) })}
        >
          Salvar
        </Button>
      </div>
      <p className="text-xs text-muted-foreground">
        Vale a partir do próximo mês. Com o PIB negativo, o capital passa a render negativo.
      </p>
    </div>
  );
}

/** A venda de parte da empresa: as quatro frações e o que a escolhida põe no caixa com o desconto. */
function CapitalSale({ mechanic }: EntrepreneurBlockProps) {
  const sell = useSellCapital();
  const [chosen, setChosen] = useState(DEFAULT_SALE_SHARE);
  const option = mechanic.sale_options.find((candidate) => Number(candidate.share) === Number(chosen));
  const label = displayPercent(chosen, 0);

  return (
    <div className="grid gap-2 border-b pb-3">
      <span className="flex items-center gap-1.5 text-[13px] font-semibold">
        Vender parte da empresa <MetricHint metric={CAPITAL_SALE} />
      </span>
      <div className="grid items-center gap-x-6 gap-y-2 md:grid-cols-[auto_1fr_auto]">
        <ToggleGroup
          variant="outline"
          spacing={0}
          aria-label="Quanto do capital vender"
          value={[chosen]}
          onValueChange={(values) => values[0] && setChosen(values[0])}
        >
          {mechanic.sale_options.map((candidate) => (
            <ToggleGroupItem key={candidate.share} value={String(Number(candidate.share))}>
              {displayPercent(candidate.share, 0)}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
        <p className="text-xs text-muted-foreground">
          {label} do capital é {displayMoney(option?.part ?? 0)}; com o desconto de 20% na venda, entram no caixa{" "}
          <b className="font-mono font-bold text-foreground">{displayMoney(option?.proceeds ?? 0)}</b>.
        </p>
        <Button
          variant="outline"
          disabled={Number(mechanic.capital) <= 0 || sell.isPending}
          onClick={() => sell.mutate({ share: chosen })}
        >
          Vender {label}
        </Button>
      </div>
    </div>
  );
}
