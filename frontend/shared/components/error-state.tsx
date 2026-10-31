import { CircleAlert } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import type ApiError from "@/shared/lib/models/ApiError";

interface ErrorStateProps {
  title: string;
  /** Sem texto próprio, vale a mensagem do erro da API */
  description?: string;
  error?: ApiError | null | undefined;
  onRetry?: (() => void) | undefined;
  children?: React.ReactNode;
}

/** Erro de carregamento: o que houve, o que fazer e a linha técnica da resposta. */
export function ErrorState({ title, description, error, onRetry, children }: ErrorStateProps) {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyMedia variant="destructive">
          <CircleAlert />
        </EmptyMedia>
        <EmptyTitle>{title}</EmptyTitle>
        <EmptyDescription>{description ?? error?.message}</EmptyDescription>
        {error && <p className="font-mono text-[11px] text-faint-foreground">{error.statusLine}</p>}
      </EmptyHeader>
      {(onRetry || children) && (
        <EmptyContent className="flex-row justify-center">
          {onRetry && <Button onClick={onRetry}>Tentar de novo</Button>}
          {children}
        </EmptyContent>
      )}
    </Empty>
  );
}
