import { Circle, Square } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { useStartEngineProfile } from "../hooks/mutations/useStartEngineProfile";
import { useStopEngineProfile } from "../hooks/mutations/useStopEngineProfile";
import { useEngineProfile } from "../hooks/queries/useEngineProfile";

/** Grava o perfil do motor: o tempo de cada função enquanto a partida roda. */
export function EngineProfileCard() {
  const { data } = useEngineProfile();
  const start = useStartEngineProfile();
  const stop = useStopEngineProfile();
  const recording = data?.recording ?? false;
  const saved = stop.data?.file;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Gravar perfil do motor</CardTitle>
        <CardDescription>
          Grava o tempo de cada função do servidor enquanto você joga, um a dois minutos no x100, e salva um arquivo
          para abrir no snakeviz. Enquanto grava, o jogo anda mais devagar: o perfil mostra as proporções, não os
          milissegundos.
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="grid gap-3">
          <div>
            {recording ? (
              <Button variant="destructive" disabled={stop.isPending} onClick={() => stop.mutate()}>
                <Square />
                Parar e gravar o arquivo
              </Button>
            ) : (
              <Button variant="outline" disabled={start.isPending} onClick={() => start.mutate()}>
                <Circle />
                Começar a gravar
              </Button>
            )}
          </div>

          {saved && !recording && (
            <div className="grid gap-1.5 text-sm">
              <span>Perfil gravado. Para abrir, rode num terminal:</span>
              <code className="rounded-lg bg-foreground px-3 py-2.5 font-mono text-[12.5px] text-sidebar-foreground">
                pnpm profile:view {saved}
              </code>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
