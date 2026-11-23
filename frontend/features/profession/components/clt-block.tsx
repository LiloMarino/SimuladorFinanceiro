import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricHint } from "@/shared/components/metric-hint";
import { Label } from "@/shared/components/ui/label";
import { Switch } from "@/shared/components/ui/switch";
import { displayMoney, displayPercent, displaySignedPercent } from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { useSetOvertime } from "../hooks/mutations/useSetOvertime";
import { FGTS_BALANCE, GDP_12M, HEALTH_COST, OVERTIME, TR } from "../lib/profession-metrics";
import { BlockPanel, MechanicBlock } from "./mechanic-block";

type CltBlockProps = {
  mechanic: Extract<ProfessionMechanic, { kind: "clt" }>;
};

/** "Sua mecânica: FGTS e hora extra" do CLT, lado a lado. */
export function CltBlock({ mechanic }: CltBlockProps) {
  return (
    <MechanicBlock
      title="Sua mecânica: FGTS e hora extra"
      description="O FGTS cresce sozinho todo mês; a hora extra é a sua escolha de renda contra saúde."
      status={mechanic.status}
      links={[
        { label: "Carteira, linha FGTS", to: "/portfolio" },
        { label: "Meta, renda do mês", to: "/goal" },
      ]}
    >
      <div className="grid gap-4 md:grid-cols-2">
        <FgtsPanel mechanic={mechanic} />
        <OvertimePanel mechanic={mechanic} />
      </div>
    </MechanicBlock>
  );
}

function FgtsPanel({ mechanic }: CltBlockProps) {
  return (
    <BlockPanel title="FGTS" aside={<MetricHint metric={FGTS_BALANCE} />}>
      <div className="grid">
        <KeyValueRow
          label="Saldo do FGTS"
          note="conta no patrimônio, fora do caixa"
          value={displayMoney(mechanic.fgts_balance)}
        />
        <KeyValueRow
          label="Depósito do mês"
          note="8% do salário bruto, pago pela empresa"
          value={`+${displayMoney(mechanic.fgts_deposit)}`}
        />
        <KeyValueRow
          label={
            <span className="inline-flex items-center gap-1">
              Rendimento <MetricHint metric={TR} />
            </span>
          }
          note={
            <span className="grid">
              <span>TR de hoje: {displayPercent(mechanic.tr, 2)} ao ano</span>
              <span>3% ao ano + TR</span>
            </span>
          }
          value={`${displayPercent(mechanic.fgts_yield, 2)} ao ano`}
        />
        <KeyValueRow
          label="Se você for demitido"
          note="saldo + multa de 40% caem no caixa"
          value={displayMoney(mechanic.layoff_payout)}
        />
      </div>
    </BlockPanel>
  );
}

function OvertimePanel({ mechanic }: CltBlockProps) {
  const setOvertime = useSetOvertime();
  const locked = mechanic.status === "LOCKED";
  const income = displayMoney(mechanic.overtime_income);

  return (
    <BlockPanel title="Hora extra" aside={<MetricHint metric={OVERTIME} />}>
      <div className="flex items-center gap-2">
        <Switch
          id="overtime"
          checked={mechanic.overtime}
          disabled={locked || setOvertime.isPending}
          onCheckedChange={(enabled) => setOvertime.mutate({ enabled })}
        />
        <Label htmlFor="overtime">{mechanic.overtime ? "Ligada" : "Desligada"}</Label>
      </div>
      <div className="grid gap-1 text-[13px]">
        <p>
          <b className="font-semibold">+{displayPercent(mechanic.overtime_rate, 0)} na renda:</b>{" "}
          <b className="font-mono font-semibold">{income}</b> a mais por mês. Em troca, o imprevisto de saúde{" "}
          <MetricHint metric={HEALTH_COST} /> custa o dobro.
        </p>
        <p className="text-muted-foreground">
          Disponível enquanto o PIB de 12 meses fica em 0 ou mais · hoje{" "}
          <b className="font-mono">{displaySignedPercent(mechanic.growth, 1)}</b> <MetricHint metric={GDP_12M} />
        </p>
      </div>
      {locked && (
        <Alert variant="warning">
          <AlertTitle>
            {mechanic.overtime_waiting
              ? "Travado: a recessão cortou a hora extra."
              : "Travado: o PIB está abaixo de zero."}
          </AlertTitle>
          <AlertDescription>
            O PIB de 12 meses está em {displaySignedPercent(mechanic.growth, 1)} <MetricHint metric={GDP_12M} />
            {": "}a empresa só mantém a hora extra com o PIB em zero ou mais. Quando ele voltar, você escolhe se liga de
            novo.
          </AlertDescription>
        </Alert>
      )}
    </BlockPanel>
  );
}
