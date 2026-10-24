import { InfoHint } from "@/shared/components/info-hint";
import { PROMISE_BANDS } from "../lib/election";
import { PROMISE } from "../lib/election-metrics";

/** A dica do "Promessa": as cinco faixas da régua e onde cada medida de governo cai. */
export function PromiseHint() {
  return (
    <InfoHint interactive label="A régua da promessa, explicada">
      <div className="grid w-80 gap-2.5">
        <b className="text-[13px]">A régua da promessa, explicada</b>
        <ol className="grid gap-2">
          {PROMISE_BANDS.map((band) => (
            <li key={band.value} className="grid grid-cols-[1.5rem_1fr] items-start gap-2.5">
              <span className="inline-flex size-6 items-center justify-center rounded-md bg-muted text-xs font-semibold">
                {band.value}
              </span>
              <span className="grid gap-px">
                <b className="text-[13px]">{band.title}</b>
                <span className="text-muted-foreground">{band.description}</span>
              </span>
            </li>
          ))}
        </ol>
        <p className="text-muted-foreground">
          Cada medida aprovada tem uma posição na régua: corte geral de imposto vale 1, isenção setorial 2, taxar um
          setor 4 e imposto geral novo 5. A marca do governo é a média das medidas aprovadas: isentar energia (2),
          taxar bancos (4) e subir o day trade (5) dá 3,7. Cada faixa de distância até a promessa tira 3 pontos de
          aprovação: prometer 3 e chegar a 3,7 tira 2.
        </p>
      </div>
    </InfoHint>
  );
}

/** Rótulo "Promessa" com a dica da régua ao lado. */
export function PromiseLabel() {
  return (
    <span className="inline-flex items-center gap-1">
      {PROMISE.label}
      <PromiseHint />
    </span>
  );
}
