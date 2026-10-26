import { Lock } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { useSetMyStrategy } from "@/shared/hooks/mutations/useSetMyStrategy";
import type { TradeLock } from "@/shared/hooks/useTradeLock";
import { displayShortDate } from "@/shared/lib/utils/display";

/** Aviso das boletas travadas: o automático se desliga aqui mesmo (ou se troca em Estratégias); o presidente espera o fim do mandato. */
export function TradeLockNotice({ lock }: { lock: TradeLock }) {
  const setStrategy = useSetMyStrategy();

  return (
    <div className="flex items-center gap-2.5 rounded-lg border border-border bg-subtle px-3 py-2.5 text-[13px]">
      <Lock className="size-4 shrink-0 text-muted-foreground" />
      {lock.reason === "automatic" ? (
        <>
          <span className="grid gap-0.5">
            <b className="font-semibold">O automático está ligado</b>
            <span className="text-xs text-muted-foreground">Desligue para operar à mão.</span>
          </span>
          <span className="ml-auto grid justify-items-end gap-1.5">
            <Button
              size="sm"
              disabled={setStrategy.isPending}
              onClick={() => setStrategy.mutate({ key: null, params: {} })}
            >
              {setStrategy.isPending && <Spinner />}
              Desligar o automático
            </Button>
            <Link
              to="/strategies"
              className="text-xs font-medium whitespace-nowrap text-primary hover:text-primary-hover"
            >
              Ir para Estratégias
            </Link>
          </span>
        </>
      ) : (
        <span className="grid gap-0.5">
          <b className="font-semibold">Você governa</b>
          <span className="text-xs text-muted-foreground">
            Presidente não compra nem vende enquanto governa: sua carteira volta a operar em{" "}
            {displayShortDate(lock.until)}.
          </span>
        </span>
      )}
    </div>
  );
}
