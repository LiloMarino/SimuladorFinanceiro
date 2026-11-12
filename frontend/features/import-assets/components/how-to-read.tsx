import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Swatch } from "./coverage-legend";

/** Como ler a tabela de ativos: as barras, a classe e o setor. */
export function HowToRead() {
  return (
    <Card size="sm">
      <CardHeader>
        <CardTitle>Como ler</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 text-[13px] text-muted-foreground">
          <div className="grid gap-2">
            <span className="flex items-start gap-2">
              <span className="mt-1 inline-flex">
                <Swatch kind="real" />
              </span>
              Dado real, do histórico
            </span>
            <span className="flex items-start gap-2">
              <span className="mt-1 inline-flex">
                <Swatch kind="repeat" />
              </span>
              Ainda sem futuro gerado: a partida repete o último preço
            </span>
            <span className="flex items-start gap-2">
              <span className="mt-1 inline-flex">
                <Swatch kind="generated" />
              </span>
              Futuro gerado: plausível, montado com trechos reais
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
