import type { ReactNode } from "react";
import { Bot } from "lucide-react";
import { Link } from "react-router-dom";
import { InfoHint } from "@/shared/components/info-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";

/** Gráfico ilustrativo de cada regra: desenho fixo, não usa dado da partida. */
function PreviewChart({ children }: { children: ReactNode }) {
  return (
    <svg viewBox="0 0 260 90" width="100%" height="90" aria-hidden="true">
      {children}
    </svg>
  );
}

const PREVIEWS = [
  {
    title: "Média móvel 50/200",
    rule: "Compra quando a média dos últimos 50 dias passa a média de 200 (tendência de alta começando).",
    reading:
      "Média móvel é o preço médio dos últimos N pregões. Ex.: se a média de 50 dias sobe de R$ 30 para R$ 32 e cruza a de 200 dias em R$ 31, a alta recente ficou mais forte que a tendência longa.",
    chart: (
      <PreviewChart>
        <path d="M0 70 C40 60 60 30 100 40 S160 70 200 30 S240 20 260 15" fill="none" stroke="var(--input)" strokeWidth="1.5" />
        <path d="M0 60 C60 55 100 50 140 45 S220 32 260 28" fill="none" stroke="var(--chart-1)" strokeWidth="2" />
        <path d="M0 50 C80 50 140 52 260 44" fill="none" stroke="var(--chart-5)" strokeWidth="2" strokeDasharray="4 3" />
        <circle cx="168" cy="47" r="5" fill="var(--success)" />
      </PreviewChart>
    ),
  },
  {
    title: "RSI sobrevendido / sobrecomprado",
    rule: "Compra quando o RSI cai abaixo de 30 e vende quando passa de 70.",
    reading:
      "O RSI (Índice de Força Relativa) vai de 0 a 100 e compara as altas com as quedas dos últimos 14 pregões. Abaixo de 30, a ação caiu muito e rápido; acima de 70, subiu muito e rápido.",
    chart: (
      <PreviewChart>
        <rect x="0" y="0" width="260" height="20" fill="var(--destructive-soft)" />
        <rect x="0" y="70" width="260" height="20" fill="var(--success-soft)" />
        <path
          d="M0 45 L30 60 L60 78 L90 62 L120 40 L150 22 L180 8 L210 30 L240 48 L260 40"
          fill="none"
          stroke="var(--chart-1)"
          strokeWidth="2"
        />
        <circle cx="60" cy="78" r="5" fill="var(--success)" />
        <circle cx="180" cy="8" r="5" fill="var(--destructive)" />
      </PreviewChart>
    ),
  },
  {
    title: "Rompimento",
    rule: "Compra quando o preço passa uma resistência com volume acima do normal.",
    reading:
      "Resistência é um preço que a ação tocou várias vezes sem passar. Ex.: depois de bater R$ 50 três vezes, fechar a R$ 51 com o dobro do volume médio sinaliza que pode seguir subindo.",
    chart: (
      <PreviewChart>
        <line x1="0" y1="35" x2="260" y2="35" stroke="var(--faint-foreground)" strokeDasharray="4 3" />
        <path
          d="M0 60 L30 40 L60 58 L90 38 L120 56 L150 40 L180 52 L200 30 L230 18 L260 10"
          fill="none"
          stroke="var(--chart-1)"
          strokeWidth="2"
        />
        <circle cx="196" cy="35" r="5" fill="var(--success)" />
        <g fill="var(--input)">
          {[
            [10, 82],
            [40, 80],
            [70, 83],
            [100, 81],
            [130, 82],
            [160, 80],
            [190, 64],
            [220, 70],
          ].map(([x, y]) => (
            <rect key={x} x={x} y={y} width="10" height={90 - y} />
          ))}
        </g>
      </PreviewChart>
    ),
  },
];

export default function StrategiesPage() {
  return (
    <div className="grid gap-5">
      {/* Cabeçalho */}
      <Card>
        <CardContent>
          <div className="flex items-center justify-between gap-6">
            <div className="grid max-w-160 gap-2">
              <Badge variant="warning">Em desenvolvimento</Badge>
              <h2 className="text-2xl font-bold">Estratégias automáticas</h2>
              <p className="text-[15px] text-muted-foreground">
                Robôs que compram e vendem por você seguindo uma regra fixa, enquanto a partida corre. Ainda não estão
                prontos: abaixo, as regras que estão sendo preparadas.
              </p>
            </div>
            <span className="flex size-18 shrink-0 items-center justify-center rounded-[18px] bg-info-soft text-primary">
              <Bot className="size-8.5" />
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Prévias */}
      <div className="grid grid-cols-3 gap-4">
        {PREVIEWS.map((p) => (
          <Card key={p.title}>
            <CardHeader>
              <CardTitle>
                <span className="inline-flex items-center gap-1">
                  {p.title}
                  <InfoHint label={`Como funciona ${p.title}`}>{p.reading}</InfoHint>
                </span>
              </CardTitle>
              <CardAction>
                <Badge variant="secondary">Prévia</Badge>
              </CardAction>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 opacity-90">
                {p.chart}
                <p className="text-[13px] text-muted-foreground">{p.rule}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Rodapé */}
      <Card>
        <CardContent>
          <div className="flex items-center justify-between gap-4">
            <p className="text-muted-foreground">
              Enquanto isso, monte a carteira à mão: a Correlação ajuda a escolher ações que não andam juntas.
            </p>
            <Button variant="outline" size="sm" nativeButton={false} render={<Link to="/correlation" />}>
              Abrir Correlação
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
