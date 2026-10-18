import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";

const DOCS_URL =
  "https://lilomarino.github.io/SimuladorFinanceiro/desenvolvimento/investigando-lentidao";

interface PySpyCardProps {
  pid: number;
}

/** O caminho depois de achar o ponto caro: o gráfico de chamas do processo em execução. */
export function PySpyCard({ pid }: PySpyCardProps) {
  const [copied, setCopied] = useState(false);
  const command = `py-spy record --pid ${pid} -o perfil.svg`;

  async function copy() {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Sem permissão para a área de transferência: o comando segue visível para copiar à mão
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Achou o ponto caro? Veja dentro dele</CardTitle>
        <CardDescription>
          O py-spy grava o que o servidor faz enquanto roda, sem mudar código, e
          gera um gráfico de chamas.
        </CardDescription>
      </CardHeader>

      <CardContent>
        <ol className="grid gap-3 text-sm">
          <li className="grid grid-cols-[22px_1fr] gap-2.5">
            <Step n={1} />
            <div className="grid gap-2">
              <span>Num terminal, rode (o número é o processo deste app):</span>
              <div className="flex items-center justify-between gap-3 rounded-lg bg-foreground px-3 py-2.5 font-mono text-[12.5px] text-sidebar-foreground">
                <code className="min-w-0 truncate">
                  py-spy record --pid{" "}
                  <span className="text-primary-foreground/90">{pid}</span> -o
                  perfil.svg
                </code>
                <Button variant="inverse" size="xs" onClick={() => void copy()}>
                  {copied ? <Check /> : <Copy />}
                  {copied ? "Copiado" : "Copiar"}
                </Button>
              </div>
            </div>
          </li>
          <li className="grid grid-cols-[22px_1fr] gap-2.5">
            <Step n={2} />
            <span>
              Repita a lentidão por uns 30 s no jogo e pare com Ctrl+C.
            </span>
          </li>
          <li className="grid grid-cols-[22px_1fr] gap-2.5">
            <Step n={3} />
            <span>
              Abra o perfil.svg no navegador: quanto mais larga a barra, mais
              tempo a função gastou.
            </span>
          </li>
          <li>
            <a
              href={DOCS_URL}
              target="_blank"
              rel="noreferrer"
              className="text-[13px] font-medium text-primary hover:underline"
            >
              Passo a passo nos docs →
            </a>
          </li>
        </ol>
      </CardContent>

      <CardFooter>
        <div className="grid gap-1.5">
          <span className="text-[13px] text-muted-foreground">
            <strong className="font-semibold text-foreground">
              Na aba Rede (F12):
            </strong>{" "}
            cada resposta traz o cabeçalho{" "}
            <code className="font-mono">Server-Timing</code> com o tempo do
            servidor.
          </span>
          <span className="text-[13px] text-muted-foreground">
            <strong className="font-semibold text-foreground">
              Requisições acima de 500 ms
            </strong>{" "}
            ficam em <code className="font-mono">logs/slow.log</code>.
          </span>
        </div>
      </CardFooter>
    </Card>
  );
}

function Step({ n }: { n: number }) {
  return (
    <span className="inline-flex size-5.5 items-center justify-center rounded-full bg-muted text-xs font-semibold text-secondary-foreground">
      {n}
    </span>
  );
}
