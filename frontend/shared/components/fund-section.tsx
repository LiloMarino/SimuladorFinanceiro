import type { ReactNode } from "react";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";

type FundSectionProps = {
  title: ReactNode;
  /** O que fica à direita do título: um botão, uma legenda */
  action?: ReactNode;
  children: ReactNode;
  className?: string;
};

/** O cartão de uma seção da página da gestora: título, ação opcional e o conteúdo. */
export function FundSection({ title, action, children, className }: FundSectionProps) {
  return (
    <Card {...(className ? { className } : {})}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {action && <CardAction>{action}</CardAction>}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
