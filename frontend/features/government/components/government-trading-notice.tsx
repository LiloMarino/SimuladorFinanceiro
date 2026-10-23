import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { useGovernment } from "../hooks/queries/useGovernment";

export function GovernmentTradingNotice() {
  const { data } = useGovernment();
  return data?.trading_frozen ? <Alert><AlertDescription>Presidência em exercício: sua carteira está congelada. Compras e vendas ficam bloqueadas; rendimentos e vencimentos continuam automáticos.</AlertDescription></Alert> : null;
}
