import { Spinner } from "@/shared/components/ui/spinner";
import { CorrelationTool } from "../components/correlation-tool";
import { useCorrelationAssets } from "../hooks/queries/useCorrelationAssets";

export default function CorrelationPage() {
  const { data, isLoading } = useCorrelationAssets();

  if (isLoading) {
    return (
      <div className="flex h-72 items-center justify-center">
        <Spinner className="size-6" />
      </div>
    );
  }

  if (!data?.last_date) {
    return (
      <p className="p-6 text-center text-sm text-muted-foreground">
        Nenhum ativo com preço. Importe ativos na Central de dados para medir a correlação.
      </p>
    );
  }

  return <CorrelationTool tickers={data.tickers} lastDate={data.last_date} endFixed={data.end_fixed} />;
}
