import { Bot, Grid3x3 } from "lucide-react";
import { Link } from "react-router-dom";
import { Alert, AlertAction, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";

const PREVIEWS = [
  {
    title: "Média móvel 50/200",
    rule: "Compra quando a média dos últimos 50 dias passa a média de 200 (tendência de alta começando).",
    reading:
      "Média móvel é o preço médio dos últimos N pregões. Ex.: se a média de 50 dias sobe de R$ 30 para R$ 32 e cruza a de 200 dias em R$ 31, a alta recente ficou mais forte que a tendência longa.",
  },
  {
    title: "RSI sobrevendido / sobrecomprado",
    rule: "Compra quando o RSI cai abaixo de 30 e vende quando passa de 70.",
    reading:
      "O RSI (Índice de Força Relativa) vai de 0 a 100 e compara as altas com as quedas dos últimos 14 pregões. Abaixo de 30, a ação caiu muito e rápido; acima de 70, subiu muito e rápido.",
  },
  {
    title: "Rompimento",
    rule: "Compra quando o preço passa uma resistência com volume acima do normal.",
    reading:
      "Resistência é um preço que a ação tocou várias vezes sem passar. Ex.: depois de bater R$ 50 três vezes, fechar a R$ 51 com o dobro do volume médio sinaliza que pode seguir subindo.",
  },
];

export default function StrategiesPage() {
  return (
    <div className="grid gap-5">
      <Card size="lg">
        <CardHeader>
          <CardTitle>
            <span className="flex items-center gap-2.5">
              <Bot />
              Estratégias automáticas
            </span>
          </CardTitle>
          <CardDescription>
            Robôs que compram e vendem por você seguindo uma regra fixa, enquanto a partida corre. Ainda não estão
            prontos: abaixo, as regras que estão sendo preparadas.
          </CardDescription>
          <CardAction>
            <Badge variant="info">Em desenvolvimento</Badge>
          </CardAction>
        </CardHeader>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        {PREVIEWS.map((p) => (
          <Card key={p.title}>
            <CardHeader>
              <CardTitle>{p.title}</CardTitle>
              <CardAction>
                <Badge variant="secondary">Prévia</Badge>
              </CardAction>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2.5">
                <p>{p.rule}</p>
                <p className="text-xs text-muted-foreground">{p.reading}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Alert variant="info">
        <Grid3x3 />
        <AlertDescription>
          Enquanto isso, monte a carteira à mão: a Correlação ajuda a escolher ações que não andam juntas.
        </AlertDescription>
        <AlertAction>
          <Button variant="outline" size="sm" nativeButton={false} render={<Link to="/correlation" />}>
            Abrir Correlação
          </Button>
        </AlertAction>
      </Alert>
    </div>
  );
}
