import { Link } from "react-router-dom";
import { Gauge, ShieldAlert } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";

/** Esqueleto no formato da tela: quatro cartões e a tabela. */
export function PerformanceLoading() {
  return (
    <div className="grid gap-5" aria-busy="true" aria-label="Carregando as medições">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
      <Skeleton className="h-96" />
    </div>
  );
}

/** Nada medido ainda: a partida está pausada desde o início. */
export function PerformanceEmpty() {
  return (
    <Card>
      <CardContent>
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <Gauge />
            </EmptyMedia>
            <EmptyTitle>Nada medido ainda</EmptyTitle>
            <EmptyDescription>
              As medições começam quando o tempo anda ou alguém usa o app. Dê play na partida e esta tela se enche
              sozinha em poucos segundos.
            </EmptyDescription>
          </EmptyHeader>
          <Badge variant="success">
            <span className="size-1.5 rounded-full bg-success" />
            Ao vivo · atualiza a cada 2 s
          </Badge>
        </Empty>
      </CardContent>
    </Card>
  );
}

/** Quem abre o endereço direto com o servidor fora do modo debug. */
export function PerformanceDebugOff() {
  return (
    <Card>
      <CardContent>
        <div className="grid max-w-xl gap-3">
          <Badge variant="secondary" className="w-max">
            Modo debug desligado
          </Badge>
          <h2 className="text-base font-semibold">O painel de desempenho só funciona com o modo debug</h2>
          <p className="text-muted-foreground">
            No executável ele vem desligado, para não pesar. Para ligar, feche o app e escolha um dos caminhos:
          </p>
          <pre className="rounded-lg bg-foreground px-3 py-2.5 font-mono text-[12.5px] leading-relaxed text-sidebar-foreground">
            <span className="text-sidebar-muted"># config.toml</span>
            {"\n[debug]\nenabled = true"}
          </pre>
          <p className="text-[13px] text-muted-foreground">
            ou abra pelo terminal com <code className="font-mono text-foreground">SimuladorFinanceiro.exe --debug</code>
          </p>
          <Button variant="outline" size="sm" className="w-max" nativeButton={false} render={<Link to="/portfolio" />}>
            Voltar à carteira
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

/** Só o host vê as medições: elas são do servidor dele. */
export function PerformanceHostOnly() {
  return (
    <Card>
      <CardContent>
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <ShieldAlert />
            </EmptyMedia>
            <EmptyTitle>Só o host vê o painel</EmptyTitle>
            <EmptyDescription>
              As medições são do servidor do host. Peça a ele se a partida estiver lenta para você.
            </EmptyDescription>
          </EmptyHeader>
          <Button variant="outline" size="sm" nativeButton={false} render={<Link to="/portfolio" />}>
            Voltar à carteira
          </Button>
        </Empty>
      </CardContent>
    </Card>
  );
}
