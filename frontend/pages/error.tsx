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

  // Na partida: a carteira e, em segundo plano, o lobby; fora dela, só o lobby
  const exits = simulationActive
    ? [
        { label: "Ir para a carteira", href: "/portfolio" },
        { label: "Voltar ao lobby", href: "/lobby" },
      ]
    : [{ label: "Voltar ao lobby", href: "/lobby" }];
  // A ação da página, quando existe, vem primeiro e as saídas ficam secundárias
  const buttons = actionLabel && actionHref ? [{ label: actionLabel, href: actionHref }, ...exits] : exits;

  return (
    <section className="flex min-h-[70vh] items-center justify-center p-6">
      <div className="grid max-w-[380px] justify-items-start gap-3.5">
        <span className="font-mono text-[13px] font-semibold text-primary">{code}</span>
        <h2 className="text-[26px] font-bold">{title}</h2>
        <p className="text-muted-foreground">{message}</p>
        <div className="flex flex-wrap gap-2">
          {buttons.map((button, i) => (
            <Button
              key={button.href}
              variant={i === 0 ? "default" : "outline"}
              nativeButton={false}
              render={<Link to={button.href} />}
            >
              {button.label}
            </Button>
          ))}
        </div>
      </div>
    </section>
  );
}
