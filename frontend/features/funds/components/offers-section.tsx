import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";

const TONE = {
  warning: { chip: "bg-warning-soft text-warning", badge: "warning" },
  fund: { chip: "bg-fund-soft text-fund", badge: "secondary" },
  muted: { chip: "bg-muted text-muted-foreground", badge: "secondary" },
} as const;

type OffersSectionProps = {
  icon: LucideIcon;
  tone: keyof typeof TONE;
  title: string;
  count: number;
  /** Diz o que o bloco mostra */
  hint: string;
  children: ReactNode;
};

/** Um bloco da página Ofertas públicas: o ícone, o título com a contagem, a frase que explica o bloco e o conteúdo. */
export function OffersSection({ icon: Icon, tone, title, count, hint, children }: OffersSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <span className={cn("grid size-7 shrink-0 place-items-center rounded-lg", TONE[tone].chip)}>
            <Icon className="size-4.5" />
          </span>
          <div className="grid gap-0.5">
            <CardTitle>
              <h2 className="flex items-center gap-2">
                {title}
                <Badge variant={TONE[tone].badge} size="tag">
                  {count}
                </Badge>
              </h2>
            </CardTitle>
            <CardDescription>{hint}</CardDescription>
          </div>
        </div>
      </CardHeader>
      {children}
    </Card>
  );
}
