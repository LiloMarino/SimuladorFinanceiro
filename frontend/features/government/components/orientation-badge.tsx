import { Check, X } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { orientationLabel } from "../lib/house";

/** "Sim" em verde ou "Não" em vermelho. */
export function OrientationBadge({ yes }: { yes: boolean }) {
  return (
    <Badge variant={yes ? "success" : "destructive"}>
      {yes ? <Check /> : <X />}
      {orientationLabel(yes)}
    </Badge>
  );
}
