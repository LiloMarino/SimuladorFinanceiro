import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import type { MechanicStatus } from "@/types";

const STATUS_BADGES: Record<MechanicStatus, { label: string; variant: "info" | "success" | "warning" }> = {
  AVAILABLE: { label: "Disponível", variant: "info" },
  ACTIVE: { label: "Ativo", variant: "success" },
  LOCKED: { label: "Travado", variant: "warning" },
};

type MechanicBlockProps = {
  title: string;
  description: string;
  /** Sem estado, o bloco só informa (profissão sem mecânica a ligar) */
  status?: MechanicStatus;
  /** A ação principal do bloco, ao lado do estado */
  action?: ReactNode;
  /** As telas onde o produto da mecânica mora, ou o `id` de uma seção da própria página */
  links?: ({ label: string; to: string } | { label: string; anchor: string })[];
  children: ReactNode;
};

/** O molde do bloco da mecânica: título, estado, o conteúdo e o rodapé "Também em". */
export function MechanicBlock({ title, description, status, action, links = [], children }: MechanicBlockProps) {
  const badge = status && STATUS_BADGES[status];
  return (
    <Card>
      <CardHeader className="grid-cols-[1fr_auto]">
        <div className="grid gap-1">
          <CardTitle>{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </div>
        {(badge || action) && (
          <div className="flex items-center gap-2">
            {badge && <Badge variant={badge.variant}>{badge.label}</Badge>}
            {action}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">{children}</div>
      </CardContent>
      {links.length > 0 && (
        <CardFooter>
          {/* Também em */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[13px]">
            <span className="text-muted-foreground">Também em</span>
            {links.map((link) =>
              "anchor" in link ? (
                <Button
                  key={link.anchor}
                  variant="link"
                  onClick={() => document.getElementById(link.anchor)?.scrollIntoView({ behavior: "smooth" })}
                >
                  {link.label}
                </Button>
              ) : (
                <Button key={link.to + link.label} variant="link" nativeButton={false} render={<Link to={link.to} />}>
                  {link.label}
                </Button>
              ),
            )}
          </div>
        </CardFooter>
      )}
    </Card>
  );
}

/** O bloco ainda sem o dado: o mesmo formato, em esqueleto. */
export function MechanicBlockSkeleton() {
  return (
    <Card aria-busy="true" aria-label="Carregando a mecânica da profissão">
      <CardHeader>
        <Skeleton className="h-4 w-56" />
        <Skeleton className="h-3.5 w-80 max-w-full" />
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 sm:grid-cols-2">
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
        </div>
      </CardContent>
    </Card>
  );
}

/** Um painel dentro do bloco (FGTS, hora extra, margem). */
export function BlockPanel({ title, aside, children }: { title: string; aside?: ReactNode; children: ReactNode }) {
  return (
    <div className="grid content-start gap-3 rounded-[10px] border p-4">
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-sm font-semibold">{title}</h3>
        {aside}
      </div>
      {children}
    </div>
  );
}
