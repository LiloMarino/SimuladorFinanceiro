import { Link } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { useSimulation } from "@/shared/hooks/useSimulation";

type ErrorPageProps = {
  /** Código do erro, ex: "404", "500" */
  code?: string;
  title?: string;
  message?: string;
  /** Ação principal da página; sem ela, só aparece a saída do momento */
  actionLabel?: string;
  actionHref?: string;
};

export function ErrorPage({
  code = "404",
  title = "Essa página não existe",
  message = "O endereço pode ter sido digitado errado ou a tela mudou de lugar.",
  actionLabel,
  actionHref,
}: ErrorPageProps) {
  const { simulationActive } = useSimulation();

  // Na partida a saída é a carteira; fora dela, o lobby
  const exit = simulationActive
    ? { label: "Ir para a carteira", href: "/portfolio" }
    : { label: "Voltar ao lobby", href: "/lobby" };
  const hasAction = !!actionLabel && !!actionHref;

  return (
    <section className="flex min-h-[70vh] items-center justify-center p-6">
      <div className="grid max-w-[380px] justify-items-start gap-3.5">
        <span className="font-mono text-[13px] font-semibold text-primary">{code}</span>
        <h2 className="text-[26px] font-bold">{title}</h2>
        <p className="text-muted-foreground">{message}</p>
        <div className="flex gap-2">
          {hasAction && (
            <Button nativeButton={false} render={<Link to={actionHref} />}>
              {actionLabel}
            </Button>
          )}
          <Button variant={hasAction ? "outline" : "default"} nativeButton={false} render={<Link to={exit.href} />}>
            {exit.label}
          </Button>
        </div>
      </div>
    </section>
  );
}
