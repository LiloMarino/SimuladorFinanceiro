import { cn } from "@/shared/lib/utils";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Card } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBug, faCircleQuestion, faTriangleExclamation, type IconDefinition } from "@fortawesome/free-solid-svg-icons";

type ErrorStateProps = {
  /** Código do erro, ex: "404", "500" */
  code?: string;
  /** Título principal (curto e direto) */
  title?: string;
  /** Mensagem explicativa abaixo do título */
  message?: string;
  /** Texto do botão */
  actionLabel?: string;
  /** Caminho de destino do botão */
  actionHref?: string;
  /** Classe opcional pra customização */
  className?: string;
};

type ErrorVisual = {
  icon: IconDefinition;
  iconColor: string;
  bgColor: string;
};

function resolveErrorVisual(code?: string): ErrorVisual {
  const status = Number(code);

  if (status >= 400 && status < 500) {
    return {
      icon: faTriangleExclamation,
      iconColor: "text-yellow-600",
      bgColor: "bg-yellow-100",
    };
  }

  if (status >= 500 && status < 600) {
    return {
      icon: faBug,
      iconColor: "text-red-600",
      bgColor: "bg-red-100",
    };
  }

  return {
    icon: faCircleQuestion,
    iconColor: "text-muted-foreground",
    bgColor: "bg-muted",
  };
}

export function ErrorPage({
  code = "404",
  title = "Página não encontrada",
  message = "Parece que você tentou acessar algo que não existe.",
  actionLabel,
  actionHref,
  className,
}: ErrorStateProps) {
  const visual = resolveErrorVisual(code);
  const hasPrimaryAction = actionHref && actionLabel;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={cn("flex min-h-[80vh] w-full items-center justify-center px-4", className)}
    >
      <section className="w-full max-w-lg px-4">
        <Card className="p-6">
          <div className="flex flex-col items-center text-center gap-4">
            <div className={cn("rounded-full w-16 h-16 flex items-center justify-center", visual.bgColor)}>
              <FontAwesomeIcon icon={visual.icon} className={visual.iconColor} size="2x" />
            </div>

            <div className="flex flex-col items-center">
              <div className="text-3xl font-bold text-primary">{code}</div>
              <h2 className="mt-2 text-2xl font-semibold text-foreground">{title}</h2>
              <p className="mt-1 text-sm text-muted-foreground leading-relaxed ">{message}</p>
            </div>

            <div className="mt-4 flex gap-2">
              {hasPrimaryAction && (
                <Button asChild>
                  <Link to={actionHref}>{actionLabel}</Link>
                </Button>
              )}
              <Button asChild variant={hasPrimaryAction ? "outline" : "default"}>
                <Link to="/">Voltar para o Início</Link>
              </Button>
            </div>
          </div>
        </Card>
      </section>
    </motion.div>
  );
}
