import type { ReactNode } from "react";
import { InfoHint } from "@/shared/components/info-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import type { FuturePreview } from "@/types";
import {
  ibovEndNumber,
  ipcaPeakNumber,
  maxDrawdownNumber,
  selicPeakNumber,
  type PreviewNumber,
} from "../lib/preview-format";

const TONE_CLASS: Record<PreviewNumber["tone"], string> = {
  up: "text-success",
  down: "text-destructive",
  neutral: "text-foreground",
};

type NumberTileProps = { label: string; hint: ReactNode; number: PreviewNumber };

function NumberTile({ label, hint, number }: NumberTileProps) {
  return (
    <Card size="sm">
      <CardContent className="min-w-0">
        <div className="grid gap-0.5">
          <span className="flex items-start gap-1 text-xs font-medium text-muted-foreground">
            {label}
            <InfoHint label={`O que é ${label}`}>
              <div className="space-y-1 text-left">{hint}</div>
            </InfoHint>
          </span>
          <span className={cn("font-mono text-lg font-semibold tabular-nums", TONE_CLASS[number.tone])}>
            {number.value}
          </span>
          <span className="text-[11.5px] text-muted-foreground">{number.detail}</span>
        </div>
      </CardContent>
    </Card>
  );
}

/** Os quatro números que resumem o futuro da prévia, cada um com a dica de como lê-lo. */
export function PreviewNumbers({ preview }: { preview: FuturePreview }) {
  return (
    <div className="grid grid-cols-2 gap-2 min-[1100px]:grid-cols-4">
      <NumberTile
        label="Ibovespa no fim"
        number={ibovEndNumber(preview.ibov_change)}
        hint={
          <>
            <p>Quanto o Ibovespa muda do último dado real até o fim do futuro gerado.</p>
            <p>+31% quer dizer que 100 mil pontos viram 131 mil. É o resultado desta semente: outra semente dá outro número, igualmente plausível.</p>
          </>
        }
      />
      <NumberTile
        label="Maior queda"
        number={maxDrawdownNumber(preview.max_drawdown)}
        hint={
          <>
            <p>
              Quanto o Ibovespa caiu do ponto mais alto até o mais baixo depois dele, dentro do futuro gerado. −24% quer
              dizer que quem comprou no pico chegou a perder 24% antes de recuperar.
            </p>
            <p>No histórico real, a mediana num ano é −20%; o pior ano foi 2008, com −60%.</p>
          </>
        }
      />
      <NumberTile
        label="SELIC no pico"
        number={selicPeakNumber(preview.selic_peak)}
        hint={
          <>
            <p>
              A SELIC é a taxa básica de juros, em % ao ano. O pico é o valor mais alto que ela atinge no futuro gerado,
              ao lado do valor de hoje para comparar.
            </p>
            <p>Juro alto encarece o crédito e costuma derrubar a bolsa. Desde 2000 a SELIC ficou entre 1,9% e 26,4%.</p>
          </>
        }
      />
      <NumberTile
        label="Inflação no pico"
        number={ipcaPeakNumber(preview.ipca_peak)}
        hint={
          <>
            <p>
              IPCA de 12 meses é quanto os preços subiram nos últimos 12 meses. O pico é o maior valor no futuro gerado,
              ao lado do valor de hoje para comparar.
            </p>
            <p>10% ao ano é uma inflação alta: foi o que o Brasil viveu em 2015.</p>
          </>
        }
      />
    </div>
  );
}
