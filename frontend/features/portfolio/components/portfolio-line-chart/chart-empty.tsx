import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";

export function PortfolioLineEmpty() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Evolução do Patrimônio</CardTitle>
      </CardHeader>
      <CardContent className="h-[380px] flex flex-col items-center justify-center">
        <div className="text-center space-y-2">
          <div className="text-4xl text-muted-foreground/50">📊</div>
          <p className="text-muted-foreground text-sm">Nenhum dado disponível ainda</p>
        </div>
      </CardContent>
    </Card>
  );
}
