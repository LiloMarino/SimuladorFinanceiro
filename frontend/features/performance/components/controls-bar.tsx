import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";

interface ControlsBarProps {
  paused: boolean;
  /** A última leitura falhou: os números na tela são de antes. */
  failed: boolean;
  /** Instante da última leitura (ms), mostrado quando a atualização está pausada ou falhou. */
  updatedAt: number;
  resetting: boolean;
  onTogglePause: () => void;
  onReset: () => void;
}

export function ControlsBar({
  paused,
  failed,
  updatedAt,
  resetting,
  onTogglePause,
  onReset,
}: ControlsBarProps) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <p className="max-w-[720px] text-muted-foreground">
        Onde o tempo vai nesta partida, medido pelo próprio app. Cada linha usa
        as últimas 1.000 medições dela.
      </p>
      <div className="flex items-center gap-2">
        {failed ? (
          <Badge variant="destructive">
            Sem conexão · dados de{" "}
            {new Date(updatedAt).toLocaleTimeString("pt-BR")}
          </Badge>
        ) : paused ? (
          <Badge variant="warning">
            Pausado · dados de {new Date(updatedAt).toLocaleTimeString("pt-BR")}
          </Badge>
        ) : (
          <Badge variant="success">
            <span className="size-1.5 rounded-full bg-success" />
            Ao vivo · atualiza a cada 2 s
          </Badge>
        )}
        <Button variant="outline" size="sm" onClick={onTogglePause}>
          {paused ? "Retomar" : "Pausar"}
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={resetting}
          onClick={onReset}
        >
          Zerar medições
        </Button>
      </div>
    </div>
  );
}
