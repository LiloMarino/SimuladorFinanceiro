import { lazy, Suspense, useEffect } from "react";
import { useDebugMode } from "@/shared/hooks/queries/useDebugMode";
import { setDebugLogging } from "@/shared/lib/logger";

// O export padrão do pacote vira um componente vazio no build de produção; o `/production`
// funciona em dev e no executável. `lazy` mantém o código fora do bundle principal.
const Devtools = lazy(() =>
  import("@tanstack/react-query-devtools/production").then((m) => ({ default: m.ReactQueryDevtools })),
);

/** Liga as ferramentas de diagnóstico do front quando o servidor sobe em modo debug. */
export function DebugTools() {
  const debug = useDebugMode();

  useEffect(() => {
    setDebugLogging(debug);
  }, [debug]);

  return debug ? (
    <Suspense fallback={null}>
      <Devtools initialIsOpen={false} />
    </Suspense>
  ) : null;
}
