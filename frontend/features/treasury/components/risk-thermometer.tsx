import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { InfoHint } from "@/shared/components/info-hint";
import { Kpi } from "@/shared/components/kpi";
import { MetricHint } from "@/shared/components/metric-hint";
import { DEBT_GDP, RISK_PREMIUM } from "@/shared/lib/budget-metrics";
import { displayPercent } from "@/shared/lib/utils/display";
import type { TreasuryThermometer } from "@/types";
import { GAUGE_MAX_DEBT, PREMIUM_BANDS, gaugePosition, pointsOf, pointsUnit } from "../lib/treasury";

const BAND_BAR_CLASS = ["bg-success/20", "bg-chart-3/35", "bg-chart-3/75", "bg-destructive/35"];
const GAUGE_TICKS = [0.5, 0.8, 1];

// Centro de cada faixa na régua, em %, para pôr o nome dela em cima
const bandCenter = (index: number) =>
  (((PREMIUM_BANDS[index]?.from ?? 0) + (PREMIUM_BANDS[index + 1]?.from ?? GAUGE_MAX_DEBT)) / 2 / GAUGE_MAX_DEBT) * 100;

type RiskThermometerProps = { thermometer: TreasuryThermometer | null };

/** O risco do país: o prêmio de hoje, a dívida ÷ PIB numa régua de faixas e quanto falta para a próxima. */
export function RiskThermometer({ thermometer }: RiskThermometerProps) {
  return (
    <Card>
      {/* Cabeçalho */}
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-1.5">
            Termômetro do risco
            <InfoHint label="Como funciona o termômetro">
              Quando a dívida do governo passa de 50% do PIB (tudo o que o país produz num ano), o Tesouro soma um juro
              extra, o prêmio de risco, à taxa de todos os títulos. Quanto maior a dívida, maior o prêmio.
            </InfoHint>
          </span>
        </CardTitle>
        <CardDescription>Quanto o país deve decide o juro extra que o Tesouro paga.</CardDescription>
      </CardHeader>

      <CardContent>
        {thermometer ? (
          <Reading thermometer={thermometer} />
        ) : (
          <Alert variant="muted">
            <TriangleAlert />
            <AlertTitle>Sem prêmio nesta partida</AlertTitle>
            <AlertDescription>
              O prêmio de risco nasce da dívida do governo, que só existe com a expansão Governo & Política. Aqui as
              taxas seguem só a Selic e o IPCA.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}

function Reading({ thermometer }: { thermometer: TreasuryThermometer }) {
  const premium = Number(thermometer.premium);
  const debt = Number(thermometer.debt);
  const change = thermometer.debt_change_12m === null ? null : Number(thermometer.debt_change_12m);
  const band = PREMIUM_BANDS[thermometer.band_index];

  return (
    <div className="grid gap-5">
      {/* Prêmio de hoje */}
      <div className="flex items-end justify-between gap-3">
        <Kpi
          label={
            <>
              Prêmio de risco hoje <MetricHint metric={RISK_PREMIUM} />
            </>
          }
          size="lg"
          value={
            premium === 0 ? (
              "0 ponto"
            ) : (
              <>
                +{pointsOf(premium)}
                <span className="ml-1.5 font-sans text-sm font-medium text-muted-foreground">pontos</span>
              </>
            )
          }
        />
        <Badge variant={band?.tone ?? "secondary"}>{thermometer.band}</Badge>
      </div>

      {/* Régua da dívida */}
      <div className="grid gap-1.5">
        <div className="relative h-4">
          {PREMIUM_BANDS.map((item, index) => (
            <span
              key={item.name}
              className="absolute -translate-x-1/2 text-xs font-semibold whitespace-nowrap text-secondary-foreground"
              style={{ left: `${bandCenter(index)}%` }}
            >
              {item.name}
            </span>
          ))}
        </div>
        <div className="relative">
          <div className="flex h-3.5 overflow-hidden rounded-full">
            {PREMIUM_BANDS.map((item, index) => (
              <span
                key={item.name}
                className={BAND_BAR_CLASS[index]}
                style={{
                  width: `${(((PREMIUM_BANDS[index + 1]?.from ?? GAUGE_MAX_DEBT) - item.from) / GAUGE_MAX_DEBT) * 100}%`,
                }}
              />
            ))}
          </div>
          <span
            aria-hidden
            className="absolute -top-1.5 h-[26px] w-[3px] -translate-x-1/2 rounded-sm bg-foreground ring-2 ring-card"
            style={{ left: `${gaugePosition(debt)}%` }}
          />
        </div>
        <div className="relative h-3.5 font-mono text-xs text-faint-foreground">
          {GAUGE_TICKS.map((tick) => (
            <span key={tick} className="absolute -translate-x-1/2" style={{ left: `${gaugePosition(tick)}%` }}>
              {Math.round(tick * 100)}%
            </span>
          ))}
        </div>
      </div>

      {/* Dívida e próxima faixa */}
      <div className="grid grid-cols-2 gap-3">
        <Kpi
          label={
            <>
              Dívida ÷ PIB <MetricHint metric={DEBT_GDP} />
            </>
          }
          value={displayPercent(debt, 1)}
          note={
            change === null
              ? undefined
              : `${change > 0 ? "▲" : change < 0 ? "▼" : ""} ${pointsOf(Math.abs(change), 1)} ${pointsUnit(change)} em 12 meses`
          }
        />
        <NextBand thermometer={thermometer} />
      </div>

      <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs leading-normal text-muted-foreground">
        {debt <= 0.5
          ? "Até 50% do PIB o Tesouro não paga prêmio. A partir daí, cada ponto de dívida soma um pouco mais que o anterior."
          : `Cada ponto a mais de dívida soma ${pointsOf(thermometer.premium_per_debt_point)} ${pointsUnit(thermometer.premium_per_debt_point)} ao prêmio agora, e cada ponto seguinte soma um pouco mais.`}
      </p>
    </div>
  );
}

function NextBand({ thermometer }: { thermometer: TreasuryThermometer }) {
  if (thermometer.next_band === null || thermometer.next_band_limit === null) {
    return (
      <Kpi
        label="Próxima faixa"
        value="—"
        note="já na última faixa: o prêmio não tem teto e cresce mais rápido a cada ponto"
      />
    );
  }

  const missing = pointsOf(thermometer.debt_to_next_band ?? 0, 1);
  // Sem 12 meses de histórico não há ritmo para projetar; com o histórico, mês nulo é dívida estável ou caindo
  const pace =
    thermometer.debt_change_12m === null
      ? "o ritmo aparece com 12 meses de histórico"
      : thermometer.months_to_next_band === null
        ? "a dívida não está subindo"
        : `no ritmo dos últimos 12 meses, em uns ${thermometer.months_to_next_band} meses`;

  return (
    <Kpi
      label="Próxima faixa"
      value={thermometer.next_band}
      note={`em ${displayPercent(thermometer.next_band_limit, 0)}: faltam ${missing} pontos de dívida; ${pace}`}
    />
  );
}
