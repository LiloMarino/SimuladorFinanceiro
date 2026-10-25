import { Component, type ErrorInfo, type ReactNode } from "react";
import { logger } from "@/shared/lib/logger";

interface Props {
  fallback: ReactNode;
  children: ReactNode;
}

/** Contém a falha da ilustração (chunk que não carregou, alvo que a cena não achou) no quadro dela. */
export class IllustrationBoundary extends Component<Props, { failed: boolean }> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    logger.error("Ilustração do Como jogar falhou:", error, info.componentStack);
  }

  render() {
    return this.state.failed ? this.props.fallback : this.props.children;
  }
}
