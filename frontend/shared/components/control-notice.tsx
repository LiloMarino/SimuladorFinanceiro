import { ShieldAlert, ShieldCheck } from "lucide-react";
import type { ReactNode } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";

type ControlNoticeProps = {
  keepsControl: boolean;
  title: ReactNode;
  children: ReactNode;
};

/** O aviso de controle: verde quando o gestor segue com mais da metade das cotas, âmbar quando perde. */
export function ControlNotice({ keepsControl, title, children }: ControlNoticeProps) {
  const Icon = keepsControl ? ShieldCheck : ShieldAlert;
  return (
    <Alert variant={keepsControl ? "success" : "warning"}>
      <Icon />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{children}</AlertDescription>
    </Alert>
  );
}
