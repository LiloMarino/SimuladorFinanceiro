import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";

/** Como ler a tabela: as barras, a classe e o setor. */
export function HowToRead() {
  return (
    <Card size="sm">
      <CardHeader>
        <CardTitle>Como ler</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 text-[13px] text-muted-foreground">
          <div className="grid gap-2">
            <span className="flex items-center gap-2">
              <span className="h-2.5 w-8 rounded-full bg-primary" />
              Dado real, do histórico
            </span>
            <span className="flex items-center gap-2">
              <span className="h-2.5 w-8 rounded-full bg-[repeating-linear-gradient(135deg,var(--chart-3)_0_3px,transparent_3px_6px)] opacity-70" />
              Depois do fim: repete o último valor
            </span>
          </div>
          <p>
            <b className="text-foreground">Classe</b> decide o IR na venda. Vem do final do código (11 → FII, 34 → BDR),
            mas ETF e units também terminam em 11: confira.
          </p>
          <p>
            <b className="text-foreground">Setor</b> agrupa a carteira e as estatísticas. O yFinance sugere na
            importação.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
