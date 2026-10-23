import { Lock } from "lucide-react";
import { Link } from "react-router-dom";

/** Aviso das boletas travadas: o automático opera pelo jogador e a saída é a página de estratégias. */
export function AutomaticLock() {
  return (
    <div className="flex items-center gap-2.5 rounded-lg border border-border bg-subtle px-3 py-2.5 text-[13px]">
      <Lock className="size-4 shrink-0 text-muted-foreground" />
      <span className="grid gap-0.5">
        <b className="font-semibold">O automático está ligado</b>
        <span className="text-xs text-muted-foreground">Para operar à mão, volte ao manual.</span>
      </span>
      <Link to="/strategies" className="ml-auto font-medium whitespace-nowrap text-primary hover:text-primary-hover">
        Ir para Estratégias
      </Link>
    </div>
  );
}
